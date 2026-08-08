#!/usr/bin/env python3
"""Analyze research/_index/manifest.jsonl + source ledgers to derive per-subject
ingestion metadata (verification_status, primary_source_coverage, priority, ...).

This is a decision-support script for Agent 8 (Research Corpus Ingestion Queue).
It reads the corpus read-only; the assignments it prints are reviewed and then
written into the manifest by the agent, not by this script.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "research")
MANIFEST = os.path.join(ROOT, "_index", "manifest.jsonl")

URL_RE = re.compile(r"https?://([^/\s)\]>\"']+)", re.I)

# Domain classification
AUTHORITATIVE_DOMS = {
    "nih.gov", "ncbi.nlm.nih.gov", "pubmed.ncbi.nlm.nih.gov", "pubchem.ncbi.nlm.nih.gov",
    "pmc.ncbi.nlm.nih.gov", "webbook.nist.gov", "nist.gov", "acs.org", "pubs.acs.org",
    "fda.gov", "dea.gov", "usda.gov", "europa.eu", "ema.europa.eu", "nih.gov",
    "pubmed.gov", "science.gov", "cdc.gov", "doi.org", "springer.com", "link.springer.com",
    "sciencedirect.com", "nature.com", "cell.com", "elsevier.com", "tandfonline.com",
    "wiley.com", "onlinelibrary.wiley.com", "mdpi.com", "karger.com", "thieme-connect.com",
    "frontiersin.org", "plos.org", "journals.plos.org", "cambridge.org", "academic.oup.com",
    "oup.com", "sci-hub.se", "researchgate.net", "scholar.google.com", "semanticscholar.org",
    "core.ac.uk", "osti.gov", "drugs.com", "medlineplus.gov", "clinicaltrials.gov",
    "chemistryworld.com", "pubs.rsc.org", "rsc.org", "degruyter.com", "wiley.com",
    "pubmed.ncbi.nlm.nih.gov", "biorxiv.org", "medrxiv.org", "hindawi.com", "iupac.org",
    "un.org", "who.int", "nap.nationalacademies.org", "jncc.gov.uk", "gov.uk",
    "canada.ca", "gc.ca", "health.gov", "hhs.gov", "justice.gov", "atf.gov",
    "archive.org", "web.archive.org", "patents.google.com", "uspto.gov",
    "gov", "edu", "org",  # handled separately by TLD rule
}
# Domains that are canonical supplier/homepages get "official" credit when the
# subject slug token appears in the domain.
WEAK_DOMS = {
    "reddit.com", "youtube.com", "instagram.com", "facebook.com", "twitter.com",
    "x.com", "tiktok.com", "amazon.com", "amazon.co.uk", "ebay.com", "aliexpress.com",
    "dhgate.com", "wish.com", "etsy.com", "weedmaps.com", "leafly.com", "allbud.com",
    "youtube", "vapor.com", "vapefuse.com", "vapesourcing.com", "blogspot.com",
    "wordpress.com", "medium.com", "quora.com", "linkedin.com", "cannabiscafe.net",
    "fuckcombustion.com", "vapingunderground.com", "grasscity.com", "reddit",
}
TLD_AUTH = (".gov", ".edu", ".mil", ".int")
TLD_WEAK = (".ru", ".cn", ".in", ".info", ".biz", ".top", ".xyz", ".click")

MULTI_RUN_SUBJECTS = {
    "7th Floor, LLC (dba Elev8 Glass Gallery)",
    "Cannabigerolic Acid (CBGA)",
    "DaVinci Tech (DVNT Holdings)",
    "Ditanium Vapor (DitaniumVapor)",
    "EpicVape LLC (Epickai)",
    "Eucalyptol (1,8-Cineole)",
    "Lotus Vaporizer (Mendocino Therapeutics / INHALE)",
    "Ocimene (α/β isomers)",
    "Smiss Technology Co., Ltd.",
    "Vapvana, LLC",
    "Wulf Mods LLC",
    "Zeus Arsenal",
    "α-Humulene",
}
IDENTITY_RISK_SUBJECTS = {
    "Smiss Technology Co., Ltd.",        # Flowermate parentage unverified
    "TopGreen Technology (XMAX)",        # XMAX vs XVape brand split
    "XVape (TopGreen Technology)",       # same
}

def classify_domain(domain):
    d = domain.lower()
    d = re.sub(r"^www\.", "", d)
    # strip port
    d = d.split(":")[0]
    for auth in AUTHORITATIVE_DOMS:
        if d == auth or d.endswith("." + auth):
            return "authoritative"
    for weak in WEAK_DOMS:
        if d == weak or d.endswith("." + weak):
            return "weak"
    if d.endswith(TLD_AUTH):
        return "authoritative"
    if d.endswith(TLD_WEAK):
        return "weak"
    return "neutral"

GENERIC_TOKENS = {
    "vapor", "vaporizer", "vaporizers", "vape", "vapes", "tech", "technology",
    "technologies", "devices", "dry", "herb", "herbal", "herbs", "cannabis",
    "brand", "brands", "official", "home", "shop", "store", "stores", "online",
    "products", "product", "smoke", "smoking", "glass", "warehouse", "supply",
    "supplies", "distributor", "group", "international", "global", "world",
    "worldwide", "company", "companies", "corp", "corporation", "llc", "inc",
    "ltd", "limited", "gmbh", "oem", "factory", "manufacturer", "manufacturing",
    "shenzhen", "china", "usa", "american", "eu", "european", "uk", "oils",
    "oil", "the", "and", "of", "dba", "formerly", "house", "holdings", "sdn",
    "bhd", "industries", "industrial", "solutions", "systems", "mfg", "co", "ltd",
}


def brand_tokens(subject):
    """Derive candidate brand tokens from a canonical subject string."""
    tokens = set()
    for part in re.split(r"[()/—–,]+|\b(?:formerly|dba|later|aka|parent|related to)\b", subject):
        for w in re.findall(r"[a-zA-Z0-9]{4,}", part):
            wl = w.lower()
            if wl in GENERIC_TOKENS or wl in ("the", "and", "of", "with", "for", "from"):
                continue
            tokens.add(wl)
    # drop tokens that are also generic substrings of common words
    return tokens


def scan_ledger(path, subject=None):
    """Extract domains + ledger type markers from a research file.
    Returns (cats, markers, brand_hits)."""
    cats = Counter()
    markers = Counter()
    brand_hits = set()
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return cats, markers, brand_hits
    domains = set()
    for m in URL_RE.finditer(text):
        domains.add(m.group(1).lower())
    for d in domains:
        cats[classify_domain(d)] += 1
    if subject:
        toks = brand_tokens(subject)
        for d in domains:
            host = re.sub(r"^www\.", "", d)
            if any(t in host for t in toks):
                brand_hits.add(host)
    # Ledger type markers, applied ONLY within the source-ledger region of the
    # file so prose and device-spec tables don't inflate coverage.
    marker_pat = {
        "official": re.compile(r"Official\s*\(|Official\s+\w+\s+(site|page|product page|website|store)", re.I),
        "manual": re.compile(r"Manual\s*\(PDF\)|User\s+Manual|Owner's?\s+Manual|official\s+manual|Manual\s+Source\s*:\s*\[?PDF", re.I),
        "patent": re.compile(r"\bPatent\b|\bUSPTO\b", re.I),
        "sec": re.compile(r"SEC\s+filing|\b10-K\b|\b10-Q\b|\b8-K\b|\|\s*SEC\b|\bNASDAQ\b|\bNYSE\b", re.I),
        "govreg": re.compile(r"\bFDA\b|\bCPSC\b|\bT\u00dcV\b|\bEU MDR\b|\|\s*(Government|Regulatory|Registration|State|Federal|Agency)\b", re.I),
        "sci": re.compile(r"\bPubChem\b|\bNIST\b|\bNIH\b|\bPMC\b|\bPubMed\b|\bdoi\.org\b|\|\s*(Academic|Journal|Scientific|Peer-?reviewed)\b", re.I),
    }
    in_ledger = False
    header_re = re.compile(r"^#{1,6}\s+(.+)$")
    ledger_header_re = re.compile(r"^#{1,6}\s*(?:\d+[.:]\s*)?(Sources?|Source Ledger|References?|Citations?|Footnotes?|Source List|Works Cited|Bibliography|Source Records?|Provenance)\s*[:#]?", re.I)
    for line in text.splitlines():
        stripped = line.strip()
        h = header_re.match(stripped)
        if h:
            in_ledger = bool(ledger_header_re.match(stripped))
            continue
        if not in_ledger:
            continue
        is_ledger_row = "|" in stripped or stripped.startswith("- [") or stripped.startswith("- ")
        if not is_ledger_row:
            continue
        for name, pat in marker_pat.items():
            if pat.search(line):
                markers[name] += 1
    return cats, markers, brand_hits

def main():
    with open(MANIFEST, encoding="utf-8") as fh:
        recs = [json.loads(l) for l in fh if l.strip()]

    # group by canonical_subject
    subjects = defaultdict(list)
    for r in recs:
        subjects[r["canonical_subject"]].append(r)

    rows = []
    for subject, rs in sorted(subjects.items()):
        roles = Counter(r["research_role"] for r in rs)
        sub_types = Counter(r["subject_subtype"] for r in rs)
        stype = Counter(r["subject_type"] for r in rs).most_common(1)[0][0]
        # files to scan: artifact + export (skip redundant)
        scan_files = []
        for r in rs:
            if r["research_role"] in ("artifact", "export"):
                p = os.path.join(ROOT, r["normalized_path"].replace("research/", "", 1))
                if os.path.exists(p):
                    scan_files.append(p)
        agg = Counter()
        markers = Counter()
        brand_hits = set()
        for p in scan_files:
            c, m, bh = scan_ledger(p, subject)
            agg.update(c)
            markers.update(m)
            brand_hits |= bh
        auth = agg.get("authoritative", 0)
        weak = agg.get("weak", 0)
        neutral = agg.get("neutral", 0)
        total = auth + weak + neutral
        # Coverage reflects the REPORTED ledger: authoritative databases + official
        # manufacturer/government documents (manual, patent, SEC, FDA/regulatory).
        official_docs = markers.get("official", 0) + markers.get("manual", 0)
        gov_sci = markers.get("govreg", 0) + markers.get("sec", 0) + markers.get("sci", 0) + markers.get("patent", 0)
        brand_official = len(brand_hits)
        if total == 0 and brand_official == 0:
            coverage = "weak"  # no ledger evidence found
        else:
            ratio = auth / total if total else 0
            if (auth >= 3 and ratio >= 0.5) or (brand_official + official_docs >= 3 and (gov_sci >= 1 or auth >= 2)) or (brand_official >= 2 and auth >= 1) or (stype == "compounds" and auth >= 10 and ratio >= 0.4):
                coverage = "strong"
            elif (auth >= 2 and ratio >= 0.3) or (brand_official >= 2 and (auth >= 1 or official_docs >= 1)) or (brand_official + markers.get("manual", 0) >= 2) or (gov_sci >= 3) or (auth >= 4):
                coverage = "moderate"
            else:
                coverage = "weak"
        has_artifact = roles.get("artifact", 0) > 0
        has_export = roles.get("export", 0) > 0
        multi = subject in MULTI_RUN_SUBJECTS
        idrisk = subject in IDENTITY_RISK_SUBJECTS
        rows.append({
            "subject": subject, "stype": stype, "subtype": sub_types.most_common(1)[0][0],
            "roles": dict(roles), "files": len(scan_files), "auth": auth, "weak": weak,
            "neutral": neutral, "coverage": coverage, "has_artifact": has_artifact,
            "has_export": has_export, "multi": multi, "idrisk": idrisk,
            "_markers": markers, "_brand": brand_hits,
        })

    print(f"{'subject':60s} {'type':10s} {'A':>1} {'E':>1} {'auth':>3} {'off':>3} {'mnl':>3} {'gov':>3} {'brd':>3} {'cov':9s} {'mult':>4} {'risk':>4}")
    for r in sorted(rows, key=lambda x: (x["coverage"] != "strong", x["subject"])):
        mk = r.get("_markers", Counter())
        print(f"{r['subject'][:60]:60s} {r['stype'][:10]:10s} {int(r['has_artifact']):1d} {int(r['has_export']):1d} "
              f"{r['auth']:3d} {mk.get('official',0):3d} {mk.get('manual',0):3d} {mk.get('govreg',0)+mk.get('sec',0):3d} "
              f"{len(r.get('_brand', set())):3d} {r['coverage']:9s} {str(r['multi']):>4} {str(r['idrisk']):>4}")
    print()
    print("coverage distribution:", Counter(r["coverage"] for r in rows))

if __name__ == "__main__":
    main()
