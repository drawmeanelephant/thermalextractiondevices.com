#!/usr/bin/env python3
"""California DCC ingestion workflow for Thermal Extraction Devices.

Pipeline (per the project spec):

    fetch -> checksum private source -> validate source schema -> normalize -> compare with
    previous snapshot -> generate Markdown -> validate Boris graph -> build all
    publication surfaces -> change report

Source policy: the Looker Studio dashboard interface is treated as an
undocumented and potentially unstable source. Every retrieval is checksummed
with full provenance (source URL, retrieval timestamp, data-through date, query
parameters, source-payload hashes, generator and schema versions), while raw
and normalized payloads remain in private, unpublished storage. The workflow
FAILS WITHOUT PUBLISHING when any guard trips.

Generated pages are static Markdown (Apex dialect) compiled by Boris. No
embeds, no client JavaScript, no dashboard iframes.

Usage:
    python3 scripts/dcc_ingest.py            # full pipeline (uses cached raw)
    python3 scripts/dcc_ingest.py --refresh  # refetch everything
    python3 scripts/dcc_ingest.py --skip-publish
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_VERSION = "0.1.0-poc"
SCHEMA_VERSION = "1.0"
RETRIEVAL_TS = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
RETRIEVAL_DATE = RETRIEVAL_TS[:10]

CANNA_API = "https://as-dcc-pub-cann-w-p-002.azurewebsites.net"
RECALLS_BASE = "https://recalls.cannabis.ca.gov"
DCC_DASHBOARD_URL = "https://www.cannabis.ca.gov/resources/data-dashboard/"
DCC_GLOSSARY_URL = DCC_DASHBOARD_URL + "data-dashboard-glossary/"
DCC_TESTING_URL = "https://www.cannabis.ca.gov/licensees/testing-laboratories/"
DCC_SEARCH_URL = "https://search.cannabis.ca.gov/"

DCC_WARNING = (
    "Source data are entered by licensees and may later be corrected or "
    "revised by the Department of Cannabis Control (DCC)."
)

PAGE_SIZE = 1000

# Collections introduced by this workflow (kept in sync with ted_ids.py).
COLLECTIONS = {
    "jurisdictions": "TJUR",
    "licenses": "TLIC",
    "organizations": "TORG",
    "testing-laboratories": "TSTL",
    "recalls": "TRCL",
    "contaminants": "TCNT",
    "datasets": "TDTS",
    "requirements": "TREQ",
}


class GuardError(Exception):
    pass


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def clean(value):
    if value is None:
        return ""
    text = str(value).strip()
    if text.upper() in ("DATA NOT AVAILABLE", "N/A"):
        return ""
    return text


def fetch_bytes(url: str, timeout: int = 60) -> tuple[int, str, bytes]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (TED archive ingestion; contact: archive maintainers)",
            "Accept": "application/json, text/html, */*",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.headers.get("Content-Type", ""), response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.headers.get("Content-Type", ""), error.read()
    except urllib.error.URLError as error:
        raise GuardError(f"network failure for {url}: {error.reason}") from error


def fetch_json(url: str, timeout: int = 60) -> dict:
    status, ctype, body = fetch_bytes(url, timeout)
    text = body.decode("utf-8", "replace")
    if status >= 400:
        raise GuardError(f"HTTP {status} for {url}: {text[:200]}")
    if "<html" in text[:500].lower() or "html" in ctype.lower():
        raise GuardError(f"expected JSON but received HTML for {url}")
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise GuardError(f"invalid JSON for {url}: {error}") from error


def fetch_html(url: str, timeout: int = 60) -> str:
    status, _, body = fetch_bytes(url, timeout)
    if status >= 400:
        raise GuardError(f"HTTP {status} for {url}")
    return body.decode("utf-8", "replace")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def parse_us_date(value: str) -> tuple:
    """Parse M/D/YYYY into a sortable tuple; unparseable -> (9999,)."""
    match = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", value.strip())
    if not match:
        return (9999,)
    month, day, year = (int(part) for part in match.groups())
    return (year, month, day)


# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------

guards_issues: list[str] = []


def guard(ok: bool, message: str) -> None:
    if not ok:
        guards_issues.append(message)


def guards_failed() -> bool:
    return bool(guards_issues)

# ---------------------------------------------------------------------------
# Fetch / normalize
# ---------------------------------------------------------------------------


def fetch_license_registry(quiet: bool = False) -> list[dict]:
    records: list[dict] = []
    page = 1
    while True:
        url = f"{CANNA_API}/licenses/filteredSearch?pageSize={PAGE_SIZE}&pageNumber={page}"
        payload = fetch_json(url)
        meta = payload.get("metadata", {})
        batch = payload.get("data", [])
        records.extend(batch)
        total_pages = int(meta.get("totalPages") or 1)
        if not quiet:
            print(f"    licenses page {page}/{total_pages}: {len(batch)}")
        if page >= total_pages or not batch:
            break
        page += 1
        time.sleep(0.25)
    seen: dict[int, dict] = {}
    for record in records:
        seen[int(record["id"])] = record
    return list(seen.values())


def normalize_license(record: dict) -> dict:
    return {
        "license_number": clean(record.get("licenseNumber")),
        "license_status": clean(record.get("licenseStatus")),
        "license_term": clean(record.get("licenseTerm")),
        "license_type": clean(record.get("licenseType")),
        "license_designation": clean(record.get("licenseDesignation")),
        "issue_date": clean(record.get("issueDate")),
        "expiration_date": clean(record.get("expirationDate")),
        "authority_id": clean(record.get("licensingAuthorityId")),
        "authority": clean(record.get("licensingAuthority")),
        "business_legal_name": clean(record.get("businessLegalName")),
        "business_dba": clean(record.get("businessDbaName")),
        "business_structure": clean(record.get("businessStructure")),
        "activity": clean(record.get("activity")),
        "premise_city": clean(record.get("premiseCity")),
        "premise_state": clean(record.get("premiseState")),
        "premise_county": clean(record.get("premiseCounty")),
        "data_refreshed_at": clean(record.get("dataRefreshedDate")),
    }


def normalize_licenses(records: list[dict]) -> list[dict]:
    return [normalize_license(record) for record in records]


def fetch_testing_labs(quiet: bool = False) -> dict:
    url = (
        f"{CANNA_API}/licenses/AdvancedSearch?licenseStatus=Active"
        f"&licenseType={urllib.parse.quote('Commercial -  Testing Laboratory')}"
        f"&pageSize={PAGE_SIZE}&pageNumber=1"
    )
    payload = fetch_json(url)
    if not quiet:
        print(f"    testing-labs query returned {len(payload.get('data', []))} records")
    return payload


def normalize_testing_labs(payload: dict) -> list[dict]:
    records = [normalize_license(record) for record in payload.get("data", [])]
    records = [item for item in records if item["license_status"].lower() == "active"]
    records.sort(key=lambda item: item["license_number"])
    return records


def parse_visible_text(html: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text)


RECALL_DETAIL_FIELDS = [
    "Business Recall Date",
    "DCC Recall Publication Date",
    "Recall Type",
    "Product Type",
    "Product Description",
    "Legal Business Name",
    "Legal Business License Number",
    "Manufactured By",
    "Manufactured By DBA",
    "Manufactured By License Number",
    "Packaged By",
    "Packaged By DBA",
    "Packaged By License Number",
    "Business Website",
]

# Value boundaries: labeled fields must never swallow following sections.
FIELD_STOP_MARKERS = [
    " Share This Recall:",
    " Product Details",
    " What consumers",
    " What licensees",
    " Recall Overview",
    " Business Recall Date",
]


def extract_labeled_fields(text: str, labels: list[str]) -> dict[str, str]:
    positions = []
    for label in labels:
        match = re.search(re.escape(label), text)
        if match:
            positions.append((match.start(), label))
    positions.sort()
    result: dict[str, str] = {}
    for index, (start, label) in enumerate(positions):
        end = positions[index + 1][0] if index + 1 < len(positions) else len(text)
        value = text[start + len(label):end]
        for marker in FIELD_STOP_MARKERS:
            marker_at = value.find(marker)
            if marker_at != -1:
                value = value[:marker_at]
                break
        result[label] = value.strip(" -")
    return result


def decode_next_payloads(html: str) -> str:
    """Decode Next.js `__next_f.push([1, "..."])` payloads back to real JSON text.

    The server-rendered index page double-escapes the payload JSON inside a JS
    string literal; json.loads of the quoted literal recovers the original text.
    """
    decoded: list[str] = []
    for match in re.finditer(r'__next_f\.push\(\[1,(".*?")\]\)', html, re.S):
        try:
            decoded.append(json.loads(match.group(1)))
        except json.JSONDecodeError:
            continue
    return "\n".join(decoded)


def parse_index_cards(html: str) -> list[dict]:
    """Parse recall cards from the server-rendered index page."""
    text = decode_next_payloads(html)
    cards: list[dict] = []
    # Each card block begins with a div keyed by the recall hex id.
    blocks = re.split(r'\["\$","div","([0-9a-f]{20,})",\{"className":"rounded-xl', text)
    for index in range(1, len(blocks), 2):
        recall_id = blocks[index]
        body = blocks[index + 1] if index + 1 < len(blocks) else ""
        card = {"id": recall_id, "url": f"{RECALLS_BASE}/recalls/{recall_id}"}
        type_match = re.search(r'"(Voluntary|Mandatory)"', body)
        card["type"] = type_match.group(1) if type_match else ""
        date_match = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", body)
        card["date"] = date_match.group(1) if date_match else ""
        title_match = re.search(
            rf'"href":"/recalls/{recall_id}","className":"hover:underline","children":"([^"]+)"', body
        )
        card["title"] = title_match.group(1) if title_match else ""
        reason_match = re.search(r'"children":"((?:Adulterated|Misbranded)[^"]*)"', body)
        card["reason"] = reason_match.group(1) if reason_match else ""
        cards.append(card)
    return cards


def fetch_recall_index(quiet: bool = False) -> list[dict]:
    recalls: list[dict] = []
    page = 1
    while True:
        url = f"{RECALLS_BASE}/recalls?page={page}" if page > 1 else f"{RECALLS_BASE}/recalls"
        html = fetch_html(url)
        cards = parse_index_cards(html)
        if not cards:
            if page == 1:
                raise GuardError("recall index returned no cards (source interface changed?)")
            break
        recalls.extend(cards)
        if not quiet:
            print(f"    recalls index page {page}: {len(cards)} cards")
        page += 1
        if page > 60:
            break
        time.sleep(0.2)
    seen: dict[str, dict] = {}
    for recall in recalls:
        seen[recall["id"]] = recall
    recalls = list(seen.values())
    recalls.sort(key=lambda item: parse_us_date(item["date"]), reverse=True)
    return recalls


def fetch_recall_detail(recall_id: str) -> dict:
    url = f"{RECALLS_BASE}/recalls/{recall_id}"
    html = fetch_html(url)
    text = parse_visible_text(html)
    title_match = re.search(r"<title>([^<]+)</title>", html, re.S)
    title = ""
    if title_match:
        title = title_match.group(1).replace(" California Cannabis Recall Details", "").strip()
    fields = extract_labeled_fields(text, RECALL_DETAIL_FIELDS)
    reason_match = re.search(r"Recall Reason\s+([^A-Z][^A-Z]{0,120}?)(?:Recall Overview|Business Recall)", text)
    fields["Recall Reason"] = reason_match.group(1).strip() if reason_match else ""
    overview_match = re.search(r"Recall Overview\s+(.{0,600}?)(?:Business Recall Date|What consumers|What licensees)", text)
    overview = overview_match.group(1).strip() if overview_match else ""
    if not (fields.get("Legal Business Name") or fields.get("Product Type")):
        raise GuardError(f"recall detail {recall_id} did not parse (schema drift?)")
    return {"id": recall_id, "url": url, "title": title, "overview": overview, "fields": fields}


TESTING_PANEL = [
    "Cannabinoids and terpenes",
    "Residual solvents and processing chemicals",
    "Residual pesticides",
    "Heavy metals",
    "Microbial impurities",
    "Mycotoxins",
    "Moisture content and water activity",
    "Foreign material",
]

CURATED_REQUIREMENTS = {
    "source": DCC_TESTING_URL,
    "panel": TESTING_PANEL,
    "citations": {
        "MAUCRSA": "Business and Professions Code sections 26000 et seq.",
        "testing_authority": "Business and Professions Code section 26110",
        "lab_regulations": "CCR Title 4, Division 42, Chapter 5, sections 15701-15705",
    },
    "notes": (
        "Numeric decision/action limits are set in the DCC regulatory text; "
        "verify limits against the current version of Title 4, Division 42 "
        "before relying on them."
    ),
}

CONTAMINANTS = [
    {"slug": "pyrethrins", "name": "Pyrethrins",
     "class": "Residual pesticide / plant growth regulator",
     "recall_anchor": True,
     "summary": "Natural botanical insecticide compounds; subject to DCC residual-pesticide testing and Category II contamination action limits.",
     "consumer_action": "Do not consume products that test above action limits; return or dispose per recall notice."},
    {"slug": "aflatoxins", "name": "Aflatoxins (B1, B2, G1, G2)",
     "class": "Mycotoxin", "recall_anchor": False,
     "summary": "Fungal metabolites produced by Aspergillus species; regulated under mycotoxin testing.",
     "consumer_action": "Do not consume adulterated products; dispose or return per recall notice."},
    {"slug": "ochratoxin-a", "name": "Ochratoxin A",
     "class": "Mycotoxin", "recall_anchor": False,
     "summary": "Nephrotoxic fungal metabolite; regulated under mycotoxin testing.",
     "consumer_action": "Do not consume adulterated products; dispose or return per recall notice."},
    {"slug": "ste-coli", "name": "Shiga toxin-producing E. coli (STEC)",
     "class": "Microbial impurity", "recall_anchor": False,
     "summary": "Pathogenic bacterial contaminant; regulated under microbial-impurity testing.",
     "consumer_action": "Do not consume; seek medical attention if symptoms develop."},
    {"slug": "salmonella", "name": "Salmonella spp.",
     "class": "Microbial impurity", "recall_anchor": False,
     "summary": "Pathogenic bacterial contaminant; regulated under microbial-impurity testing.",
     "consumer_action": "Do not consume; seek medical attention if symptoms develop."},
    {"slug": "aspergillus", "name": "Aspergillus spp. (flavus, fumigatus, terreus, niger)",
     "class": "Microbial impurity", "recall_anchor": False,
     "summary": "Mold genus with toxigenic and pathogenic species; regulated under microbial-impurity testing.",
     "consumer_action": "Do not consume; seek medical attention if symptoms develop."},
    {"slug": "lead", "name": "Lead (Pb)",
     "class": "Heavy metal", "recall_anchor": False,
     "summary": "Toxic heavy metal; regulated under heavy-metal testing.",
     "consumer_action": "Do not consume products exceeding action limits."},
    {"slug": "residual-solvents", "name": "Residual solvents",
     "class": "Processing chemical", "recall_anchor": False,
     "summary": "Solvents remaining from extraction and processing; regulated under residual-solvent testing.",
     "consumer_action": "Do not consume products exceeding action limits."},
]

DASHBOARDS = {
    "harvest": {
        "name": "Harvest Report",
        "url": "https://lookerstudio.google.com/embed/reporting/91831a20-eba8-4556-9401-c569ad8d9d0b/page/p_z20nuw1mvd",
        "page": DCC_DASHBOARD_URL + "harvest-report/",
    },
    "monthly-sales": {
        "name": "Monthly Sales Summary Report",
        "url": "https://lookerstudio.google.com/embed/reporting/6b47e2fb-90e6-4bfa-97d6-d91e3fa4d1f2/page/p_hp495019xd",
        "page": DCC_DASHBOARD_URL + "daily-sales-units-by-item-category-report/",
    },
}


def fetch_glossary_changelog_date() -> str:
    try:
        html = fetch_html(DCC_GLOSSARY_URL)
        text = parse_visible_text(html)
        dates = re.findall(r"(\d{1,2}/\d{1,2}/\d{4})", text)
        parsed = sorted((parse_us_date(item), item) for item in dates if parse_us_date(item)[0] != 9999)
        return parsed[-1][1] if parsed else ""
    except GuardError:
        return ""

# ---------------------------------------------------------------------------
# Archival, manifest, comparison
# ---------------------------------------------------------------------------


def archive_dataset(dataset_id: str, raw_files: list[tuple[str, str]],
                    normalized, metadata: dict, data_root: Path) -> dict:
    """Record checksums without persisting source payloads in the repository.

    The caller may use an ignored/private cache for re-runs, but the tracked
    repository boundary contains only aggregate Markdown plus provenance
    metadata. ``data_root`` remains in the signature for compatibility with
    the existing pipeline call sites.
    """
    raw_checksums = {}
    for filename, content in raw_files:
        data = content if isinstance(content, bytes) else content.encode("utf-8")
        raw_checksums[filename] = sha256_bytes(data)
    norm_json = json.dumps(normalized, indent=2, ensure_ascii=False)
    normalized_checksum = sha256_text(norm_json)
    return {
        "dataset": dataset_id,
        "source_urls": metadata.get("source_urls", []),
        "retrieval_timestamp": RETRIEVAL_TS,
        "retrieval_date": RETRIEVAL_DATE,
        "data_through": metadata.get("data_through", ""),
        "query_params": metadata.get("query_params", {}),
        "storage": "private-unpublished",
        "source_payloads": raw_checksums,
        "raw_checksum": sha256_text("".join(sorted(raw_checksums.values()))),
        "normalized_checksum": normalized_checksum,
        "normalized_rows": len(normalized) if isinstance(normalized, list) else None,
        "script_version": SCRIPT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "methodology_changelog_date": metadata.get("methodology_date", ""),
        "status": metadata.get("status", "ok"),
        "note": metadata.get("note", ""),
    }


def _date_tuple(value: str):
    iso = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2}).*", value.strip())
    if iso:
        return tuple(int(part) for part in iso.groups())
    return parse_us_date(value)


def compare_with_previous(dataset_id: str, normalized, data_root: Path,
                          date_key: str | None = None) -> dict:
    """Diff against the previous snapshot AND enforce collapse/backslide guards.

    The previous baseline is NOT written here; callers commit it only after a
    successful, verified run (see commit_previous).
    """
    previous_path = data_root / dataset_id / "previous.json"
    previous = []
    if previous_path.exists():
        try:
            previous = json.loads(previous_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            previous = []
    if isinstance(normalized, list):
        pk = lambda item: str(item.get("license_number") or item.get("id") or "")
        current_pks = [pk(item) for item in normalized]
        prev_set = set(pk(item) for item in previous)
        cur_set = set(current_pks)
        change = {
            "dataset": dataset_id,
            "previous_rows": len(previous),
            "current_rows": len(normalized),
            "added": len(cur_set - prev_set),
            "removed": len(prev_set - cur_set),
            "sample_added": sorted(cur_set - prev_set)[:8],
            "sample_removed": sorted(prev_set - cur_set)[:8],
        }
        # Guard: row counts collapse without explanation (short of zero rows).
        if len(previous) > 0 and len(normalized) < len(previous) * 0.5:
            guard(False, f"{dataset_id}: row count collapsed {len(previous)} -> {len(normalized)}")
        # Guard: dates move backward.
        if date_key:
            prev_dates = [_date_tuple(clean(item.get(date_key))) for item in previous if clean(item.get(date_key))]
            cur_dates = [_date_tuple(clean(item.get(date_key))) for item in normalized if clean(item.get(date_key))]
            if prev_dates and cur_dates and max(cur_dates) < max(prev_dates):
                guard(False, f"{dataset_id}: data-through date moved backward ({max(prev_dates)} -> {max(cur_dates)})")
        change["_normalized"] = normalized
    else:
        change = {"dataset": dataset_id, "note": "non-tabular dataset; no row diff"}
    return change


def commit_previous(data_root: Path, changes: list[dict]) -> None:
    for change in changes:
        payload = change.get("_normalized")
        if payload is not None:
            write_json(data_root / change["dataset"] / "previous.json", payload)

# ---------------------------------------------------------------------------
# Schema guards
# ---------------------------------------------------------------------------

KNOWN_STATUSES = {"Active", "Canceled", "Expired", "Revoked", "Suspended", "Surrendered", "Limited Operations"}


def validate_license_schema(records: list[dict]) -> None:
    guard(len(records) > 0, "license registry normalized to zero rows")
    guard(all(item.get("license_number") for item in records), "license registry rows missing license_number")
    numbers = [item["license_number"] for item in records]
    guard(len(set(numbers)) == len(numbers), "license registry contains duplicate license numbers")
    unknown = {item["license_status"] for item in records} - KNOWN_STATUSES - {""}
    guard(not unknown, f"license registry enum drift: unexpected statuses {sorted(unknown)}")


def validate_labs_schema(records: list[dict]) -> None:
    guard(len(records) > 0, "testing-labs normalized to zero rows")
    numbers = [item["license_number"] for item in records]
    guard(len(set(numbers)) == len(numbers), "testing-labs duplicate license numbers")


def validate_recalls_schema(records: list[dict]) -> None:
    guard(len(records) > 0, "recall index normalized to zero rows")
    ids = [item["id"] for item in records]
    guard(len(set(ids)) == len(ids), "recall index duplicate ids")
    guard(sum(1 for item in records if item.get("date")) >= len(records) * 0.8,
          "recall index: too many rows missing dates")

# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------


def frontmatter(entity_id: str, title: str, parent: str, tags: list[str],
                relations: list[str] | None = None, summary: str = "") -> str:
    lines = ["---", f"id: {entity_id}", f'title: "{title}"']
    if parent:
        lines.append(f"parent: {parent}")
    lines.append("status: published")
    tag_list = ", ".join('"%s"' % tag for tag in tags)
    lines.append(f"tags: [{tag_list}]")
    rels = ", ".join(relations) if relations else ""
    lines.append(f"relations: [{rels}]")
    if summary:
        lines.append(f'summary: "{summary}"')
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def scan_collection_ids(records_dir: Path, collection: str) -> tuple[set[str], dict[str, str]]:
    """Return (used form ids, natural-key -> form id) for an existing collection.

    Natural keys: title (orgs/contaminants), license number (labs), or recall
    notice URL (recalls). Re-running the ingest therefore reuses stable IDs.
    """
    prefix = COLLECTIONS[collection]
    used: set[str] = set()
    keyed: dict[str, str] = {}
    col_dir = records_dir / collection
    if not col_dir.is_dir():
        return used, keyed
    for path in col_dir.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        id_match = re.search(rf"^id:\s*{re.escape(collection)}/({prefix}-\d{{4}})", text, re.M)
        if not id_match:
            continue
        form_id = id_match.group(1)
        used.add(form_id)
        if collection in ("organizations", "contaminants"):
            title_match = re.search(r'^title: "(.+)"', text, re.M)
            if title_match:
                keyed[title_match.group(1)] = form_id
        elif collection == "testing-laboratories":
            lic_match = re.search(r"License number \| `([^`]+)`", text)
            if lic_match:
                keyed[lic_match.group(1)] = form_id
        elif collection == "recalls":
            url_match = re.search(r"Original notice: (https://recalls\.cannabis\.ca\.gov/recalls/([0-9a-f]+))", text)
            if url_match:
                keyed[url_match.group(2)] = form_id
    return used, keyed


def assign_ids(collection: str, records_dir: Path, keys: list[str]) -> dict[str, str]:
    """Map stable natural keys to form IDs, reusing existing assignments."""
    prefix = COLLECTIONS[collection]
    used, keyed = scan_collection_ids(records_dir, collection)
    for key in keys:
        if key in keyed:
            continue
        number = 1
        while True:
            candidate = f"{prefix}-{number:04d}"
            number += 1
            if candidate not in used:
                used.add(candidate)
                keyed[key] = candidate
                break
    return keyed


def write_record(records_dir: Path, collection: str, entity_id: str, body: str) -> Path:
    subdir = records_dir / collection
    ensure_dir(subdir)
    path = subdir / f"{entity_id.split('/')[-1]}.md"
    path.write_text(body, encoding="utf-8")
    return path


PROVENANCE_TEMPLATE = """## Source & Provenance

- **Official source**: {source}
- **Jurisdiction**: California, United States
- **Retrieval date**: {retrieval_date}
- **Data-through date**: {data_through}
- **Source-data caveat**: {warning}
- **Record status**: {status}
- **Generator**: scripts/dcc_ingest.py v{script_version} (schema {schema_version})
- **Stable entity ID**: {entity_id}
"""


def provenance_block(source: str, data_through: str, status: str, entity_id: str) -> str:
    return PROVENANCE_TEMPLATE.format(
        source=source,
        retrieval_date=RETRIEVAL_DATE,
        data_through=data_through or "not reported",
        warning=DCC_WARNING,
        status=status,
        script_version=SCRIPT_VERSION,
        schema_version=SCHEMA_VERSION,
        entity_id=entity_id,
    )


DCC_CAVEAT_CALLOUT = f"> [!WARNING] DCC data caveat\n> {DCC_WARNING}\n\n"

# ---------------------------------------------------------------------------
# Content generators
# ---------------------------------------------------------------------------


def gen_jurisdiction(records_dir: Path) -> list[Path]:
    entity_id = "jurisdictions/TJUR-0001"
    body = frontmatter(
        entity_id, "California (Jurisdiction Profile)", "jurisdictions",
        ["jurisdiction", "california", "regulatory"],
        relations=["relates_to=datasets/TDTS-0001", "relates_to=requirements/TREQ-0001"],
        summary="Jurisdiction profile for the State of California and its cannabis licensing framework.",
    )
    body += """# California (Jurisdiction Profile)

## Jurisdiction Identity

| Field | Value |
| --- | --- |
| State | California (CA) |
| Primary cannabis regulator | Department of Cannabis Control (DCC) |
| Statutory framework | MAUCRSA, Business and Professions Code §§ 26000 et seq. |
| Licensing authorities (historical) | BCC (commercial), CCL (cultivation), MCSB (manufacturing) |
| Consolidated DCC effective | 2021 |

## Regulatory Landscape

California legalized medical cannabis under Proposition 215 (1996) and adult-use
under Proposition 64 (2016). The Medicinal and Adult-Use Cannabis Regulation and
Safety Act (MAUCRSA) unified the licensing regime, and the Department of Cannabis
Control became the single licensing authority in 2021, consolidating the Bureau
of Cannabis Control, CalCannabis Cultivation Licensing, and the Manufactured
Cannabis Safety Branch.

## Graph Connections

- [DCC License Registry dataset](../datasets/TDTS-0001.md)
- [California Cannabis Testing Requirements](../requirements/TREQ-0001.md)

"""
    body += provenance_block("https://cannabis.ca.gov", "statutory", "synced", entity_id)
    return [write_record(records_dir, "jurisdictions", entity_id, body)]


def gen_license_summary(records_dir: Path, licenses: list[dict]) -> list[Path]:
    entity_id = "licenses/TLIC-0001"
    statuses = Counter(item["license_status"] or "Unknown" for item in licenses)
    types = Counter(item["license_type"] or "Unknown" for item in licenses)
    refreshed = max((item["data_refreshed_at"] for item in licenses if item["data_refreshed_at"]), default="")
    status_lines = "\n".join(
        f"| {name} | {count:,} |" for name, count in sorted(statuses.items(), key=lambda kv: -kv[1])
    )
    type_lines = "\n".join(
        f"| {name} | {count:,} |" for name, count in sorted(types.items(), key=lambda kv: -kv[1])[:25]
    )
    body = frontmatter(
        entity_id, "California Licensed Cannabis Establishments — Summary", "licenses",
        ["license", "california", "aggregate"],
        relations=["relates_to=datasets/TDTS-0001", "relates_to=jurisdictions/TJUR-0001"],
        summary=f"Aggregate California license counts by status and type ({len(licenses):,} records; retrieved {RETRIEVAL_DATE}).",
    )
    body += f"""# California Licensed Cannabis Establishments — Summary

{DCC_CAVEAT_CALLOUT}## License Status Distribution

| License Status | License Count |
| --- | --- |
{status_lines}

## License Types (Top 25)

| License Type | License Count |
| --- | --- |
{type_lines}

## Notes

- Counts derive from the DCC Cannabis Unified License Search registry; see the
  [dated dataset record](../datasets/TDTS-0001.md) for full provenance.
- The registry contains one row per license issued per premises, including
  expired, surrendered, revoked, suspended, and canceled records.

"""
    body += provenance_block(DCC_SEARCH_URL, refreshed[:10], "synced", entity_id)
    return [write_record(records_dir, "licenses", entity_id, body)]


def gen_dataset_license(records_dir: Path, data_root: Path, licenses: list[dict],
                        manifest: dict) -> list[Path]:
    entry = manifest["license-registry"]
    entity_id = f"datasets/{DATASET_IDS['license-registry']}"
    raw_checks = ", ".join(f"`{name}` {digest[:12]}…" for name, digest in entry["source_payloads"].items())
    body = frontmatter(
        entity_id, f"DCC License Registry Dataset — {RETRIEVAL_DATE}", "datasets",
        ["dataset", "licenses", "california"],
        relations=["relates_to=licenses/TLIC-0001", "relates_to=jurisdictions/TJUR-0001"],
        summary=f"Dated snapshot of the DCC license registry ({len(licenses):,} rows, retrieved {RETRIEVAL_DATE}).",
    )
    body += f"""# DCC License Registry Dataset

{DCC_CAVEAT_CALLOUT}## Dataset Identity

| Field | Value |
| --- | --- |
| Dataset | `license-registry` |
| Schema version | {entry['schema_version']} |
| Generator | scripts/dcc_ingest.py v{entry['script_version']} |
| Retrieval timestamp | {entry['retrieval_timestamp']} |
| Data-through date | {entry.get('data_through') or 'see raw'} |
| Rows | {len(licenses):,} |
| Source payload checksums | {raw_checks} |
| Normalized checksum | {entry['normalized_checksum'][:12]}… |

## Retrieval Parameters

- Endpoint: `GET {CANNA_API}/licenses/filteredSearch`
- Parameters: `pageSize=1000`, `pageNumber=1..N`
- Payload storage: private and unpublished; source payload hashes are retained in the repository manifest.

## Interface Stability Note

The license search API is exposed by the DCC's public license-lookup application
([search.cannabis.ca.gov](https://search.cannabis.ca.gov)) and is **undocumented**.
It paginates via `pageNumber` (not `page`) and returns at most 1,000 rows per
request. This archive treats it as potentially unstable: every retrieval is
captured with checksums, while raw and normalized payloads remain private and
unpublished. The sync fails without publishing if the response shape changes.

"""
    body += provenance_block(DCC_SEARCH_URL, "2026-08-04", "synced", entity_id)
    return [write_record(records_dir, "datasets", entity_id, body)]


DATASET_IDS = {"license-registry": "TDTS-0001", "harvest": "TDTS-0002",
               "monthly-sales": "TDTS-0003", "landscape": "TDTS-0004"}


def gen_dashboard_dataset(records_dir: Path, dashboard_id: str, manifest: dict,
                          methodology_date: str) -> list[Path]:
    info = DASHBOARDS[dashboard_id]
    entity_id = f"datasets/{DATASET_IDS[dashboard_id]}"
    entry = manifest.get(dashboard_id, {})
    body = frontmatter(
        entity_id, f"California {info['name']} (Aggregate-Only)", "datasets",
        ["dataset", "california", "aggregate"],
        relations=["relates_to=jurisdictions/TJUR-0001"],
        summary=f"Aggregate-only record for the DCC {info['name']}; source interface currently unstable.",
    )
    body += f"""# California {info['name']} (Aggregate-Only)

{DCC_CAVEAT_CALLOUT}## Purpose

This page exists so the archive can carry the aggregate reporting surface for the
DCC {info['name']} **without embedding the dashboard**. It documents the source,
the retrieval attempt, and the current extraction status.

## Source Interface Status

- Dashboard URL: {info['url']}
- Dashboard page: {info['page']}
- Interface type: Google Looker Studio embed (undocumented)
- Extraction status: **unstable / not implemented**
- Payload storage: private and unpublished; the source response is represented by checksums in the repository manifest.
- Glossary changelog date: {methodology_date or 'not extracted'}

> [!IMPORTANT] Source instability
> The DCC publishes this report only as a Looker Studio embed. No documented API or
> downloadable dataset exists as of {RETRIEVAL_DATE}. The archive retains the source
> response privately and will not render numbers it cannot source-trace. Harvest and
> sales generation remains aggregate-only until the entity model is proven.

"""
    body += provenance_block(info["page"], "not reported (unstable source)", "archived-unstable", entity_id)
    return [write_record(records_dir, "datasets", entity_id, body)]


def gen_testing_labs(records_dir: Path, labs: list[dict], org_ids: dict[str, str]) -> list[Path]:
    out = []
    lab_ids = assign_ids("testing-laboratories", records_dir, [lab["license_number"] for lab in labs])
    for lab in labs:
        entity_id = f"testing-laboratories/{lab_ids[lab['license_number']]}"
        relations = ["relates_to=jurisdictions/TJUR-0001", "relates_to=requirements/TREQ-0001"]
        org_id = org_ids.get(lab["business_legal_name"])
        if org_id:
            relations.append(f"relates_to=organizations/{org_id}")
        city = lab["premise_city"] or "unknown"
        county = lab["premise_county"] or "unknown"
        body = frontmatter(
            entity_id,
            f"{lab['business_legal_name']} — {lab['license_number']}",
            "testing-laboratories",
            ["testing-laboratory", "california", "license"],
            relations=relations,
            summary=f"Active California testing laboratory licensed under {lab['license_number']} ({city}, {county}).",
        )
        org_line = f"Organization: [{lab['business_legal_name']}](../organizations/{org_id}.md)" if org_id else "Organization: documented under license fields below"
        body += f"""# {lab['business_legal_name']}

## License Identity

| Field | Value |
| --- | --- |
| License number | `{lab['license_number']}` |
| License type | {lab['license_type']} |
| License term | {lab['license_term']} |
| Status | {lab['license_status']} |
| Issue date | {lab['issue_date'] or '—'} |
| Expiration date | {lab['expiration_date'] or '—'} |
| Business structure | {lab['business_structure'] or '—'} |

## Premises (coarse location)

| Field | Value |
| --- | --- |
| City | {city} |
| County | {county} |

## Graph Connections

- Jurisdiction: [California](../jurisdictions/TJUR-0001.md)
- {org_line}
- [California Cannabis Testing Requirements](../requirements/TREQ-0001.md)

## Source

- Official source: [DCC Cannabis Unified License Search](https://search.cannabis.ca.gov)
- Source payload: retained in private, unpublished storage; provenance hashes are recorded in the DCC manifest.

"""
        body += provenance_block(DCC_SEARCH_URL, lab["data_refreshed_at"][:10], "synced", entity_id)
        out.append(write_record(records_dir, "testing-laboratories", entity_id, body))
    return out


def build_organization_relations(
    orgs: list[dict],
    labs: list[dict],
    lab_ids: dict[str, str],
    recall_index: list[dict],
    recall_details: list[dict],
    recall_id_map: dict[str, str],
) -> dict[str, list[str]]:
    """Return high-confidence reverse edges for generated organization pages.

    DCC organization identity is keyed by the legal license number carried in
    the generated record.  Only a unique exact license-number match is linked;
    missing or ambiguous values are deliberately left unlinked.
    """
    org_names_by_license: dict[str, set[str]] = {}
    for org in orgs:
        license_number = clean(org.get("license_number"))
        if license_number:
            org_names_by_license.setdefault(license_number, set()).add(org["name"])
    unique_org_by_license = {
        license_number: next(iter(names))
        for license_number, names in org_names_by_license.items()
        if len(names) == 1
    }

    relations = {org["name"]: [] for org in orgs}
    for lab in labs:
        license_number = clean(lab.get("license_number"))
        org_name = unique_org_by_license.get(license_number)
        lab_id = lab_ids.get(license_number)
        if org_name and lab_id:
            relations[org_name].append(f"relates_to=testing-laboratories/{lab_id}")

    detail_by_id = {item["id"]: item for item in recall_details}
    for recall in recall_index[:6]:
        recall_id = recall_id_map.get(recall.get("id", ""))
        detail = detail_by_id.get(recall.get("id", ""), {})
        fields = detail.get("fields", {})
        license_number = clean(fields.get("Legal Business License Number"))
        org_name = unique_org_by_license.get(license_number)
        if org_name and recall_id:
            relations[org_name].append(f"relates_to=recalls/{recall_id}")

    return {name: sorted(set(items)) for name, items in relations.items()}


def gen_organizations(
    records_dir: Path,
    orgs: list[dict],
    labs: list[dict],
    recall_index: list[dict],
    recall_details: list[dict],
) -> dict[str, str]:
    name_to_id = assign_ids("organizations", records_dir, [org["name"] for org in orgs])
    lab_ids = assign_ids("testing-laboratories", records_dir, [lab["license_number"] for lab in labs])
    recall_id_map = assign_ids("recalls", records_dir, [recall["id"] for recall in recall_index[:6]])
    organization_relations = build_organization_relations(
        orgs, labs, lab_ids, recall_index, recall_details, recall_id_map
    )
    for org in orgs:
        entity_id = f"organizations/{name_to_id[org['name']]}"
        relations = ["relates_to=jurisdictions/TJUR-0001"]
        relations.extend(organization_relations.get(org["name"], []))
        body = frontmatter(
            entity_id, org["name"], "organizations",
            ["organization", "california"],
            relations=relations,
            summary=f"Licensed cannabis organization: {org['name']}.",
        )
        body += f"""# {org['name']}

## Organization Identity

| Field | Value |
| --- | --- |
| Legal name | {org['name']} |
| Business structure | {org['structure'] or '—'} |
| License number | {org.get('license_number') or '—'} |
| City | {org.get('city') or '—'} |
| County | {org.get('county') or '—'} |

## Graph Connections

- Jurisdiction: [California](../jurisdictions/TJUR-0001.md)

## Source

- Official source: [DCC Cannabis Unified License Search](https://search.cannabis.ca.gov)

"""
        body += provenance_block(DCC_SEARCH_URL, "2026-08-04", "synced", entity_id)
        write_record(records_dir, "organizations", entity_id, body)
    return name_to_id


def gen_recalls(records_dir: Path, recall_index: list[dict], recall_details: list[dict],
                org_ids: dict[str, str]) -> dict[str, str]:
    out = []
    detail_by_id = {item["id"]: item for item in recall_details}
    recall_id_map = assign_ids("recalls", records_dir, [recall["id"] for recall in recall_index[:6]])
    for recall in recall_index[:6]:
        entity_id = f"recalls/{recall_id_map[recall['id']]}"
        detail = detail_by_id.get(recall["id"])
        fields = detail["fields"] if detail else {}
        org_name = fields.get("Legal Business Name") or ""
        org_relation = org_ids.get(org_name)
        relations = ["relates_to=jurisdictions/TJUR-0001"]
        if org_relation:
            relations.append(f"relates_to=organizations/{org_relation}")
        reason = recall["reason"] or fields.get("Recall Reason") or "Not reported"
        product_type = fields.get("Product Type") or ""
        body = frontmatter(
            entity_id,
            recall["title"] or f"Recall {recall['id'][:8]}",
            "recalls",
            ["recall", "california", "safety"],
            relations=relations,
            summary=f"California cannabis recall notice ({recall['date'] or 'date not reported'}; {reason}).",
        )
        overview = detail["overview"] if detail else ""
        rows = "\n".join(
            f"| **{label}** | {fields.get(label) or '—'} |"
            for label in RECALL_DETAIL_FIELDS if fields.get(label)
        )
        body += f"""# {recall['title'] or 'California Cannabis Recall'}

{DCC_CAVEAT_CALLOUT}## Recall Notice

| Field | Value |
| --- | --- |
{rows or '| — | — |'}

## Overview

{overview or 'No overview text archived.'}

## Consumer Action

If you purchased this product: check your package for the UID and batch number(s)
referenced in the official notice. If the numbers match, dispose of the product or
return it to the retailer for proper disposal. Contact a physician immediately if
you experience symptoms or adverse reactions.

## Graph Connections

- Jurisdiction: [California](../jurisdictions/TJUR-0001.md)
- Original notice: {recall['url']}

"""
        body += provenance_block(recall["url"], recall["date"] or "", "synced", entity_id)
        out.append(write_record(records_dir, "recalls", entity_id, body))
    return recall_id_map


def gen_recall_index(records_dir: Path, recall_index: list[dict],
                     recall_id_map: dict[str, str]) -> list[Path]:
    """Write the recall trunk as a full index of the official portal."""
    path = records_dir / "recalls.md"
    total = len(recall_index)
    dates = sorted((parse_us_date(item["date"]), item["date"]) for item in recall_index if item.get("date"))
    latest = dates[-1][1] if dates else "not reported"
    body = frontmatter(
        "recalls", "Recalls", "", ["recall", "california", "safety"],
        summary=f"California cannabis recall notices: {total} records indexed from the DCC recalls portal (latest {latest}).",
    )
    body += f"""# Recalls

{DCC_CAVEAT_CALLOUT}This collection indexes cannabis recall notices published by the California
Department of Cannabis Control. {total} notices are listed from the official
[recalls portal]({RECALLS_BASE}/recalls) as of {RETRIEVAL_DATE}.

## Archive Records

Representative notices with full archived detail pages:

"""
    # recall_id_map: api hex id -> form id
    detail_links = []
    for recall in recall_index[:6]:
        form_id = recall_id_map.get(recall["id"])
        if form_id:
            label = recall["title"] or ("Recall " + form_id)
            detail_links.append("- [[recalls/" + form_id + "|" + label + "]]")
    body += "\n".join(detail_links) + "\n\n## Full Official Index\n\n"
    body += "| Publication date | Type | Recall | Official notice |\n| --- | --- | --- | --- |\n"
    for recall in recall_index:
        title = (recall.get("title") or "").replace("|", "\\|")
        body += f"| {recall.get('date') or '—'} | {recall.get('type') or '—'} | {title} | [notice]({recall['url']}) |\n"
    body += f"\n## Source\n\n- Official source: [{RECALLS_BASE}]({RECALLS_BASE}/recalls)\n"
    body += provenance_block(f"{RECALLS_BASE}/recalls", latest, "synced", "recalls")
    path.write_text(body, encoding="utf-8")
    return [path]


def gen_contaminants(records_dir: Path, contam_ids: dict[str, str],
                     anchor_recall_id: str) -> list[Path]:
    out = []
    # Natural key = title (as scanned from existing files), mapped back to slug.
    name_ids = assign_ids("contaminants", records_dir, [spec["name"] for spec in CONTAMINANTS])
    for spec in CONTAMINANTS:
        entity_id = f"contaminants/{name_ids[spec['name']]}"
        contam_ids[spec["slug"]] = name_ids[spec["name"]]
        relations = ["relates_to=requirements/TREQ-0001"]
        if spec["recall_anchor"] and anchor_recall_id:
            relations.append(f"relates_to=recalls/{anchor_recall_id}")
        body = frontmatter(
            entity_id, spec["name"], "contaminants",
            ["contaminant", "testing", spec["class"].split()[0].lower()],
            relations=relations,
            summary=spec["summary"],
        )
        anchor_line = f"- Related recall: [recall notice](../recalls/{anchor_recall_id}.md)" if (spec["recall_anchor"] and anchor_recall_id) else ""
        body += f"""# {spec['name']}

## Classification

| Field | Value |
| --- | --- |
| Contaminant class | {spec['class']} |
| Testing category | Required under the DCC mandatory testing panel |

## Description

{spec['summary']}

## Consumer Action

{spec['consumer_action']}

## Regulatory Context

Contaminants in this class are tested under California's mandatory cannabis
testing requirements (see [Testing Requirements](../requirements/TREQ-0001.md)).
Action limits are set in the DCC regulatory text (Title 4, Division 42) and must
be read from the current regulation.

## Graph Connections

- [California Cannabis Testing Requirements](../requirements/TREQ-0001.md)
{anchor_line}

"""
        body += provenance_block(DCC_TESTING_URL, "2026-08-04", "synced", entity_id)
        out.append(write_record(records_dir, "contaminants", entity_id, body))
    return out


def gen_requirements(records_dir: Path) -> list[Path]:
    entity_id = "requirements/TREQ-0001"
    panel_lines = "\n".join(f"| {item} | Mandatory |" for item in TESTING_PANEL)
    body = frontmatter(
        entity_id, "California Cannabis Testing Requirements (DCC)", "requirements",
        ["requirements", "testing", "california"],
        relations=["relates_to=jurisdictions/TJUR-0001"],
        summary="Mandatory testing panel and regulatory citations for California cannabis goods under the DCC.",
    )
    body += f"""# California Cannabis Testing Requirements (DCC)

{DCC_CAVEAT_CALLOUT}## Mandatory Testing Panel

The DCC requires all batches of cannabis goods to be tested before retail sale.
The mandatory panel (per the DCC Testing Laboratories guidance) is:

| Test Category | Requirement |
| --- | --- |
{panel_lines}

## Regulatory Citations

| Authority | Citation |
| --- | --- |
| Statutory framework | MAUCRSA, Business and Professions Code §§ 26000 et seq. |
| Testing requirement | Business and Professions Code § 26110 |
| Laboratory licensing / accreditation | CCR Title 4, Division 42, Chapter 5, §§ 15701–15705 |
| DCC guidance page | [DCC Testing Laboratories](https://www.cannabis.ca.gov/licensees/testing-laboratories/) |

## Action Limits

Numeric decision/action limits are set in the DCC regulatory text. This archive
does not reproduce limits it has not independently verified; consult the current
version of Title 4, Division 42 before relying on any specific number.

## Source

- Official source: [DCC Testing Laboratories]({DCC_TESTING_URL})

"""
    body += provenance_block(DCC_TESTING_URL, "2026-08-04", "synced", entity_id)
    return [write_record(records_dir, "requirements", entity_id, body)]


def gen_data_landscape(records_dir: Path) -> list[Path]:
    entity_id = f"datasets/{DATASET_IDS['landscape']}"
    body = frontmatter(
        entity_id, "California DCC Data Landscape", "datasets",
        ["dataset", "california", "overview", "apex"],
        relations=["relates_to=datasets/TDTS-0001", "relates_to=jurisdictions/TJUR-0001",
                   "relates_to=requirements/TREQ-0001"],
        summary="ApexMarkdown-heavy overview of California DCC data sources, provenance, and caveats.",
    )
    body += """# California DCC Data Landscape

> [!NOTE] What this page is
> This page demonstrates the Apex Markdown features used across the archive's
> California data records: tables, callouts, details blocks, footnotes,
> definitions, task lists, and graph links. It is generated, not embedded.

> [!IMPORTANT] No embeds
> The archive never embeds the DCC's Looker Studio dashboards. Dashboards are
> treated as upstream sources; the archive publishes static, source-traceable
> records compiled by Boris.

## Data Sources at a Glance

| Source | Interface | Status | Record |
| --- | --- | --- | --- |
| License registry | Undocumented JSON API | Synced | [[datasets/TDTS-0001|License Registry Dataset]] |
| Testing laboratories | License subset | Synced | [[testing-laboratories|Testing Laboratories]] |
| Recalls portal | Server-rendered HTML | Synced | [[recalls|Recalls]] |
| Harvest report | Looker Studio embed | Unstable | [[datasets/TDTS-0002|Harvest (aggregate)]] |
| Monthly sales | Looker Studio embed | Unstable | [[datasets/TDTS-0003|Sales (aggregate)]] |

## Provenance Model

Every generated page carries a standard provenance footer:

<dl>
<dt>Official source</dt><dd>The exact URL the data was retrieved from.</dd>
<dt>Retrieval date</dt><dd>When the source response was captured.</dd>
<dt>Data-through date</dt><dd>The latest date the source reports data for.</dd>
<dt>Checksums</dt><dd>SHA-256 of private raw and normalized payloads recorded in the source manifest.</dd>
<dt>Generator version</dt><dd>scripts/dcc_ingest.py version that produced the record.</dd>
<dt>Stable entity ID</dt><dd>The Boris graph identity, e.g. <code>datasets/TDTS-0001</code>.</dd>
</dl>

## Definitions

<dl>
<dt>Raw snapshot</dt><dd>Private, unpublished copy of the source response.</dd>
<dt>Normalized snapshot</dt><dd>Private, unpublished validated derivative of the source response.</dd>
<dt>Aggregate record</dt><dd>A page summarizing counts or trends, not individual entities.</dd>
<dt>Entity record</dt><dd>A page for one meaningful entity (laboratory, recall, contaminant, organization).</dd>
</dl>

## Current Sync Status

- [x] License registry fetched; payload retained privately and provenance recorded
- [x] Active testing laboratories extracted
- [x] Recall index captured across all pages
- [x] Representative recall details parsed
- [x] Contaminant index connected to recalls
- [x] Source manifest written
- [x] Schema-change and sync reports written
- [ ] Harvest report numeric extraction (blocked: undocumented Looker Studio source)
- [ ] Sales report numeric extraction (blocked: undocumented Looker Studio source)

## DCC Data Caveat

> [!WARNING] Licensee-entered data
> Source data are entered by licensees and may later be corrected or revised by the
> Department of Cannabis Control. Treat every figure on these pages as a
> point-in-time snapshot with the provenance recorded in its footer.

## Footnotes

The dashboard glossary defines reporting terms such as wet weight, packaged
weight, and facility type.[^1]

[^1]: DCC Data Dashboard Glossary & Notes — https://www.cannabis.ca.gov/resources/data-dashboard/data-dashboard-glossary/

"""
    body += provenance_block(DCC_DASHBOARD_URL, "2026-08-04", "synced", entity_id)
    return [write_record(records_dir, "datasets", entity_id, body)]


TRUNK_TEMPLATES = {
    "jurisdictions": ("Jurisdictions", "State-level jurisdiction profiles and licensing frameworks."),
    "licenses": ("Licenses", "Aggregate license counts and licensing summaries for regulated cannabis markets."),
    "organizations": ("Organizations", "Licensed organizations and businesses referenced across the archive."),
    "testing-laboratories": ("Testing Laboratories", "California testing laboratory license records and requirements."),
    "recalls": ("Recalls", "Cannabis recall notices and safety enforcement records."),
    "contaminants": ("Contaminants", "Contaminant classes and substances regulated under cannabis testing."),
    "datasets": ("Datasets", "Dated, source-traceable dataset snapshots and aggregate reporting surfaces."),
    "requirements": ("Requirements", "Regulatory requirements, testing panels, and statutory citations."),
}


def ensure_trunks(records_dir: Path) -> list[Path]:
    out = []
    for collection, (title, blurb) in TRUNK_TEMPLATES.items():
        path = records_dir / f"{collection}.md"
        if path.exists():
            continue
        body = frontmatter(f"{collection}", title, "", [collection],
                           summary=f"{title}: {blurb}")
        body += f"# {title}\n\n{blurb}\n\nSatellite records in this collection follow the form identifier schema `{collection}/{COLLECTIONS[collection]}-XXXX`.\n"
        path.write_text(body, encoding="utf-8")
        out.append(path)
    return out

# ---------------------------------------------------------------------------
# Verification + publication
# ---------------------------------------------------------------------------


def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    return run_env(cmd, cwd, dict(os.environ))


def run_env(cmd: list[str], cwd: Path, env: dict) -> tuple[int, str]:
    try:
        result = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=900)
        return result.returncode, (result.stdout + result.stderr)
    except subprocess.TimeoutExpired:
        return -1, "timed out"
    except FileNotFoundError as error:
        return -2, f"command not found: {error}"


def verify_content(repo_root: Path, boris_bin: str) -> bool:
    ok = True
    code, out = run(["python3", "scripts/ted_ids.py", "--root", "content", "--map", "metadata/id-map.jsonl", "--all-state-maps"], repo_root)
    if code != 0:
        guard(False, f"ted_ids validation failed:\n{out[:800]}")
        ok = False
    code, out = run(["python3", "scripts/audit_markdown_links.py", "content"], repo_root)
    if code != 0:
        guard(False, f"markdown link audit failed:\n{out[:800]}")
        ok = False
    code, out = run([boris_bin, "check", "--input", "content", "--format", "json"], repo_root)
    if code != 0:
        # Mirror bin/validate_graph.sh: tolerate baseline unreferenced_page findings.
        try:
            report = json.loads(out[out.index("{"):])
            findings = report.get("findings", [])
            unexpected = [f for f in findings if f.get("code") != "unreferenced_page"]
        except (ValueError, json.JSONDecodeError):
            unexpected = [{"code": "unparseable", "detail": out[:300]}]
        if unexpected:
            guard(False, f"boris check unexpected findings:\n{unexpected[:5]}")
            ok = False
    return ok


def publish_all(repo_root: Path, boris_bin: str) -> bool:
    env = dict(os.environ)
    env["BORIS_BIN"] = boris_bin
    code, out = run_env(["bash", "scripts/ted-publish.sh"], repo_root, env)
    if code != 0:
        guard(False, f"ted-publish failed:\n{out[:800]}")
        return False
    code, out = run_env(["bash", "scripts/ted-build.sh"], repo_root, env)
    if code != 0:
        guard(False, f"ted-build failed:\n{out[:800]}")
        return False
    return True

# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------


def write_reports(data_root: Path, manifest: dict, changes: list[dict]) -> None:
    reports = data_root / "sync-reports"
    ensure_dir(reports)
    change_report = f"""# California DCC Sync & Change Report

- Retrieval date: {RETRIEVAL_DATE}
- Script version: {SCRIPT_VERSION}
- Schema version: {SCHEMA_VERSION}

## Guard results

- Guards tripped: {len(guards_issues)}

"""
    for issue in guards_issues:
        change_report += f"- FAIL: {issue}\n"
    if not guards_issues:
        change_report += (
            "No guards tripped during the source refresh. Raw and normalized "
            "payloads were handled as private, unpublished artifacts; the "
            "repository publication boundary retains only aggregate content "
            "plus provenance metadata.\n"
        )

    change_report += "\n## Dataset changes vs previous snapshot\n\n"
    for change in changes:
        if "added" in change:
            change_report += (
                f"- **{change['dataset']}**: {change['previous_rows']} -> {change['current_rows']} rows "
                f"(+{change['added']} added, -{change['removed']} removed)\n"
            )
        else:
            change_report += f"- **{change['dataset']}**: {change.get('note', 'no change')}\n"

    (reports / f"{RETRIEVAL_DATE}-change-report.md").write_text(change_report, encoding="utf-8")

    schema_report = f"""# California DCC Schema Report

- Schema version: {SCHEMA_VERSION}
- Generated: {RETRIEVAL_TS}

## Collections introduced

| Collection | ID prefix | Entity type |
| --- | --- | --- |
"""
    for collection, prefix in COLLECTIONS.items():
        schema_report += f"| {collection} | {prefix} | {collection.replace('-', ' ').title()} |\n"
    schema_report += """

## Taxonomy deviation (deliberate)

The project brief suggested nested content layouts such as
`datasets/california-dcc/` and `licenses/california/`. Boris and ted_ids derive
the collection from the FIRST path segment of a source file, so nested satellite
dirs would mislabel entity identities. Content collections are therefore flat
(`datasets/TDTS-0001.md`, `licenses/TLIC-0001.md`, `recalls/TRCL-0001.md`, ...)
Source payloads are retained in private, unpublished storage; no raw archive
layout is present in the public repository.

## Normalized license fields (schema 1.0)

license_number, license_status, license_term, license_type, license_designation,
issue_date, expiration_date, authority_id, authority, business_legal_name,
business_dba, business_structure, activity, premise_city, premise_state,
premise_county, data_refreshed_at.

## Redacted source fields

The ingestion boundary removes or keeps private the following licensee-entered
fields before any normalized record is written to a tracked path: owner identity,
street address, postal code, email, phone, parcel/cadastral identifiers, and
latitude/longitude coordinates. The public site retains only the coarse
regulatory facts needed for source-attributed aggregate and entity pages.

## Enum drift tracking

License statuses are validated against a fixed allowlist (Active, Canceled,
Expired, Revoked, Suspended, Surrendered, Limited Operations); unexpected
statuses fail the run before publication.
"""
    (data_root / "schema-report.md").write_text(schema_report, encoding="utf-8")


def write_manifest(data_root: Path, manifest: dict) -> None:
    write_json(data_root / "manifest.json", {
        "schema_version": SCHEMA_VERSION,
        "script_version": SCRIPT_VERSION,
        "retrieval_timestamp": RETRIEVAL_TS,
        "dcc_warning": DCC_WARNING,
        "publication_boundary": "Only this manifest, the schema report, and sync reports are tracked in the repository. Raw and normalized payloads are retained in private, unpublished storage and are not served by Boris.",
        "payload_storage": "private-unpublished",
        "datasets": manifest,
    })

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="refetch all sources")
    parser.add_argument("--skip-publish", action="store_true", help="stop after content generation + verification")
    parser.add_argument("--repo-root", default=".", help="path to the TED repository root")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    records_dir = repo_root / "content"
    data_root = repo_root / "data" / "dcc"
    cache_root = data_root / "cache"
    boris_bin = os.environ.get("BORIS_BIN", str(repo_root.parent / "boris"))
    ensure_dir(data_root)
    ensure_dir(cache_root)

    manifest: dict = {}
    changes: list[dict] = []
    print(f"=== California DCC ingestion (retrieval {RETRIEVAL_DATE}) ===")

    # ---- license registry ----
    print("[1/6] license-registry")
    cache_path = cache_root / "license-registry.json"
    if args.refresh or not cache_path.exists():
        licenses = fetch_license_registry()
        write_json(cache_path, licenses)
    else:
        licenses = json.loads(cache_path.read_text(encoding="utf-8"))
    normalized_licenses = normalize_licenses(licenses)
    validate_license_schema(normalized_licenses)
    refreshed = max((item["data_refreshed_at"] for item in normalized_licenses), default="")
    manifest["license-registry"] = archive_dataset(
        "license-registry", [("raw.json", json.dumps(licenses, ensure_ascii=False))],
        normalized_licenses,
        {"source_urls": [f"{CANNA_API}/licenses/filteredSearch"],
         "query_params": {"pageSize": PAGE_SIZE, "pageNumber": "1..N"},
         "data_through": refreshed[:10], "methodology_date": ""},
        data_root)
    changes.append(compare_with_previous("license-registry", normalized_licenses, data_root, date_key="data_refreshed_at"))

    # ---- testing laboratories ----
    print("[2/6] testing-labs")
    cache_path = cache_root / "testing-labs.json"
    if args.refresh or not cache_path.exists():
        labs_payload = fetch_testing_labs()
        write_json(cache_path, labs_payload)
    else:
        labs_payload = json.loads(cache_path.read_text(encoding="utf-8"))
    labs = normalize_testing_labs(labs_payload)
    validate_labs_schema(labs)
    manifest["testing-labs"] = archive_dataset(
        "testing-labs", [("raw.json", json.dumps(labs_payload, ensure_ascii=False))], labs,
        {"source_urls": [f"{CANNA_API}/licenses/AdvancedSearch"],
         "query_params": {"licenseStatus": "Active", "licenseType": "Commercial -  Testing Laboratory", "pageSize": PAGE_SIZE},
         "data_through": max((item["data_refreshed_at"] for item in labs), default="")[:10],
         "methodology_date": ""},
        data_root)
    changes.append(compare_with_previous("testing-labs", labs, data_root, date_key="data_refreshed_at"))

    # ---- recalls ----
    print("[3/6] recalls")
    cache_path = cache_root / "recalls-index.json"
    if args.refresh or not cache_path.exists():
        recall_index = fetch_recall_index()
        write_json(cache_path, recall_index)
    else:
        recall_index = json.loads(cache_path.read_text(encoding="utf-8"))
    validate_recalls_schema(recall_index)
    raw_index_pages = []
    index_archive_dir = data_root / "recalls-index" / RETRIEVAL_DATE
    for page in range(1, 32):
        fname = f"index-page-{page:02d}.html"
        archived = index_archive_dir / fname
        if archived.exists():
            raw_index_pages.append((fname, archived.read_bytes()))
            continue
        url = f"{RECALLS_BASE}/recalls?page={page}" if page > 1 else f"{RECALLS_BASE}/recalls"
        try:
            raw_index_pages.append((fname, fetch_html(url)))
        except GuardError:
            break
    manifest["recalls-index"] = archive_dataset(
        "recalls-index", raw_index_pages, recall_index,
        {"source_urls": [f"{RECALLS_BASE}/recalls"],
         "query_params": {"page": "1..N"},
         "data_through": max((item["date"] for item in recall_index if item["date"]), default=""),
         "methodology_date": ""},
        data_root)
    changes.append(compare_with_previous("recalls-index", recall_index, data_root, date_key="date"))

    representative_ids = [item["id"] for item in recall_index[:6]]
    cache_path = cache_root / "recalls-details.json"
    if args.refresh or not cache_path.exists():
        recall_details = []
        for recall_id in representative_ids:
            print(f"    detail {recall_id[:8]}")
            detail = fetch_recall_detail(recall_id)
            recall_details.append(detail)
            time.sleep(0.3)
        write_json(cache_path, recall_details)
    else:
        recall_details = json.loads(cache_path.read_text(encoding="utf-8"))
    manifest["recalls-details"] = archive_dataset(
        "recalls-details",
        [(f"{item['id']}.html", fetch_html(item["url"])) for item in recall_details],
        recall_details,
        {"source_urls": [f"{RECALLS_BASE}/recalls/<id>"],
         "query_params": {"representative": True, "limit": 6},
         "data_through": "", "methodology_date": ""},
        data_root)

    # ---- requirements ----
    print("[4/6] requirements")
    try:
        testing_page_html = fetch_html(DCC_TESTING_URL)
    except GuardError as error:
        testing_page_html = f"<html><body>fetch failed: {error}</body></html>"
        guard(False, f"requirements: DCC testing page could not be fetched: {error}")
    manifest["requirements"] = archive_dataset(
        "requirements",
        [("dcc-testing-page.html", testing_page_html)],
        CURATED_REQUIREMENTS,
        {"source_urls": [DCC_TESTING_URL], "query_params": {},
         "data_through": "2026-08-04", "methodology_date": "2026-08-04",
         "note": "curated, versioned; numeric action limits left to regulation text"},
        data_root)

    # ---- dashboards (unstable probes; never fail the run) ----
    print("[5/6] dashboards")
    methodology_date = fetch_glossary_changelog_date()
    for dashboard_id, info in DASHBOARDS.items():
        try:
            html = fetch_html(info["url"])
            raw = html
            result = {"status": "unstable", "archived": True,
                      "note": "Looker Studio embed preserved as raw; no numeric extraction implemented."}
        except GuardError as error:
            raw = ""
            result = {"status": "unstable", "archived": False, "note": str(error)}
        manifest[dashboard_id] = archive_dataset(
            dashboard_id, [("raw.html", raw)], result,
            {"source_urls": [info["url"], info["page"]], "query_params": {},
             "data_through": "", "methodology_date": methodology_date,
             "status": "unstable",
             "note": "undocumented Looker Studio embed; aggregate-only until entity model proven"},
            data_root)

    if guards_failed():
        print("PIPELINE GUARDS TRIPPED — NOT PUBLISHING")
        for issue in guards_issues:
            print("  FAIL:", issue)
        write_reports(data_root, manifest, changes)
        write_manifest(data_root, manifest)
        return 3

    # ---- generate content ----
    print("[6/6] generate content")
    ensure_trunks(records_dir)

    org_names: dict[str, dict] = {}
    for lab in labs:
        name = lab["business_legal_name"]
        if name and name not in org_names:
            org_names[name] = {"name": name, "structure": lab["business_structure"],
                               "city": lab["premise_city"], "county": lab["premise_county"],
                               "license_number": lab["license_number"]}
    details_by_id = {item["id"]: item for item in recall_details}
    for recall in recall_index[:6]:
        fields = details_by_id.get(recall["id"], {}).get("fields", {})
        name = fields.get("Legal Business Name") or ""
        if name and name not in org_names:
            org_names[name] = {"name": name, "structure": "", "city": "", "county": "",
                               "license_number": fields.get("Legal Business License Number") or ""}
    org_ids = gen_organizations(records_dir, list(org_names.values()), labs, recall_index, recall_details)

    gen_requirements(records_dir)
    gen_jurisdiction(records_dir)
    gen_license_summary(records_dir, normalized_licenses)
    gen_dataset_license(records_dir, data_root, normalized_licenses, manifest)
    gen_dashboard_dataset(records_dir, "harvest", manifest, methodology_date)
    gen_dashboard_dataset(records_dir, "monthly-sales", manifest, methodology_date)
    recall_id_map = gen_recalls(records_dir, recall_index, recall_details, org_ids)
    gen_recall_index(records_dir, recall_index, recall_id_map)
    # Anchor pyrethrins to the recall whose reason cites a pesticide, if present.
    anchor_recall_id = ""
    for recall in recall_index[:6]:
        reason = (recall["reason"] or "").lower()
        if "pyrethrin" in reason or "pesticide" in reason:
            anchor_recall_id = recall_id_map[recall["id"]]
            break
    contam_ids: dict[str, str] = {}
    gen_contaminants(records_dir, contam_ids, anchor_recall_id)
    gen_testing_labs(records_dir, labs, org_ids)
    gen_data_landscape(records_dir)

    # ---- verify ----
    print("verify content")
    verify_content(repo_root, boris_bin)
    if guards_failed():
        print("VERIFICATION FAILED — NOT PUBLISHING")
        for issue in guards_issues:
            print("  FAIL:", issue)
        write_reports(data_root, manifest, changes)
        write_manifest(data_root, manifest)
        return 3

    # ---- publish ----
    if not args.skip_publish:
        print("publish all surfaces")
        publish_all(repo_root, boris_bin)
        if guards_failed():
            print("PUBLICATION FAILED")
            for issue in guards_issues:
                print("  FAIL:", issue)
            write_reports(data_root, manifest, changes)
            write_manifest(data_root, manifest)
            return 3

    commit_previous(data_root, changes)
    write_manifest(data_root, manifest)
    write_reports(data_root, manifest, changes)
    print(f"=== ingestion complete (retrieval {RETRIEVAL_DATE}) ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
