#!/usr/bin/env python3
"""DCC licensed-cannabis data sync for Thermal Extraction Devices.

Fetches the California Department of Cannabis Control (DCC) unified license
search registry, snapshots a configurable segment to data/dcc/, and generates
Boris-compliant Markdown satellite records under a content collection.

API endpoints (discovered from https://search.cannabis.ca.gov/config.js):
  CANNA_API  https://as-dcc-pub-cann-w-p-002.azurewebsites.net
  FUNC_API   https://fa-dcc-pub-vip-cann-ww-p-001.azurewebsites.net
  Licenses   GET {CANNA_API}/licenses/filteredSearch?pageSize=N&pageNumber=M
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

CANNA_API = "https://as-dcc-pub-cann-w-p-002.azurewebsites.net"
DEFAULT_PAGE_SIZE = 1000

# Order matters: more specific keywords first.
BUSINESS_TYPE_KEYWORDS = [
    ("Testing Laboratory", ["testing laboratory", "testing lab"]),
    ("Retailer", ["retailer"]),
    ("Distributor", ["distributor"]),
    ("Microbusiness", ["microbusiness"]),
    ("Manufacturing", ["manufacturer"]),
    ("Cultivation", ["cultivation"]),
    ("Event Organizer", ["event"]),
]


class ApiError(Exception):
    pass


def fetch_json(url: str, retries: int = 3) -> dict | list:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0 (TED archive sync)", "Accept": "application/json"}
            )
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.load(response)
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as error:
            last_error = error
            if attempt < retries:
                time.sleep(2 * attempt)
    raise ApiError(f"request failed after {retries} attempts: {url}: {last_error}")


def clean(value):
    if value is None:
        return ""
    text = str(value).strip()
    if text.upper() in ("DATA NOT AVAILABLE", "N/A"):
        return ""
    return text


def fetch_licenses(page_size: int = DEFAULT_PAGE_SIZE, quiet: bool = False) -> list[dict]:
    """Paginate the DCC license registry.

    The API ignores the `page` parameter and honors `pageNumber` (0- or
    1-indexed page indicator used by the search UI). Each page returns at
    most the first `page_size` rows of the filtered result set.
    """
    licenses: list[dict] = []
    page = 1
    while True:
        url = f"{CANNA_API}/licenses/filteredSearch?pageSize={page_size}&pageNumber={page}"
        payload = fetch_json(url)
        meta = payload.get("metadata", {})
        batch = payload.get("data", [])
        licenses.extend(batch)
        if not quiet:
            print(f"  page {page}/{meta.get('totalPages')}: {len(batch)} records (total {meta.get('totalCount')})")
        if page >= int(meta.get("totalPages") or 1) or not batch:
            break
        page += 1
        time.sleep(0.25)
    # Deduplicate defensively (API may shift between pages).
    seen: dict[int, dict] = {}
    for record in licenses:
        seen[int(record["id"])] = record
    return list(seen.values())


def business_type_of(license_type: str) -> str:
    lowered = license_type.lower()
    for name, keywords in BUSINESS_TYPE_KEYWORDS:
        if any(keyword in lowered for keyword in keywords):
            return name
    return "Other"


def filter_segment(licenses: list[dict], status: str = "", business_type: str = "",
                   county: str = "", license_type: str = "", max_licenses: int = 0) -> list[dict]:
    result = []
    for record in licenses:
        # Status matches are case-insensitive substrings (e.g. "active",
        # "limited" matches "Limited Operations").
        if status and status.lower() not in clean(record.get("licenseStatus")).lower():
            continue
        if business_type and business_type_of(clean(record.get("licenseType"))) != business_type:
            continue
        if county and clean(record.get("premiseCounty")).lower() != county.lower():
            continue
        if license_type and clean(record.get("licenseType")).lower() != license_type.lower():
            continue
        result.append(record)
        if max_licenses and len(result) >= max_licenses:
            break
    return result


def write_snapshot(licenses: list[dict], cache_dir: Path, label: str) -> tuple[Path, Path]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    json_path = cache_dir / f"licenses-{label}.json"
    csv_path = cache_dir / f"licenses-{label}.csv"
    json_path.write_text(json.dumps(licenses, indent=2, ensure_ascii=False), encoding="utf-8")
    fields = [
        "id", "licenseNumber", "licenseStatus", "licenseStatusDate", "licenseTerm",
        "licenseType", "licenseDesignation", "issueDate", "expirationDate",
        "licensingAuthorityId", "licensingAuthority", "businessLegalName",
        "businessDbaName", "businessOwnerName", "businessStructure", "activity",
        "premiseStreetAddress", "premiseCity", "premiseState", "premiseCounty",
        "premiseZipCode", "businessEmail", "businessPhone", "parcelNumber",
        "premiseLatitude", "premiseLongitude", "dataRefreshedDate",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for record in licenses:
            writer.writerow({key: clean(record.get(key)) for key in fields})
    return json_path, csv_path


def next_form_id(records_dir: Path, prefix: str) -> int:
    """Next free form-ID number, honoring existing filenames AND frontmatter ids."""
    highest = 0
    pattern = re.compile(rf"^{prefix}-(\d{{4}})$")
    if records_dir.is_dir():
        for path in records_dir.glob("*.md"):
            stem_match = pattern.match(path.stem.upper())
            if stem_match:
                highest = max(highest, int(stem_match.group(1)))
            text = path.read_text(encoding="utf-8")
            id_match = re.search(r"^id:\s*[^/]+/([A-Z]+-\d{4})", text, re.M)
            if id_match:
                fm_match = pattern.match(id_match.group(1))
                if fm_match:
                    highest = max(highest, int(fm_match.group(1)))
    return highest + 1


def summarize(group: list[dict]) -> dict:
    statuses = Counter(clean(record.get("licenseStatus")) or "Unknown" for record in group)
    license_types = Counter(clean(record.get("licenseType")) or "Unknown" for record in group)
    active = [record for record in group if clean(record.get("licenseStatus")).lower() == "active"]
    counties = Counter(clean(record.get("premiseCounty")) or "Unknown" for record in active)
    return {
        "total": len(group),
        "statuses": statuses,
        "license_types": license_types,
        "counties": counties,
        "active": active,
    }


def fmt_int(value: int) -> str:
    return f"{value:,}"


def build_record(category: str, group: list[dict], form_id: str, snapshot_label: str, single: bool = False) -> str:
    summary = summarize(group)
    refreshed = max((clean(record.get("dataRefreshedDate")) for record in group), default="")[:10]
    status_lines = "\n".join(
        f"| {name or 'Unknown'} | {fmt_int(count)} |" for name, count in sorted(summary["statuses"].items(), key=lambda item: -item[1])
    )
    type_lines = "\n".join(
        f"| {name} | {fmt_int(count)} |" for name, count in sorted(summary["license_types"].items(), key=lambda item: -item[1])
    )
    county_lines = "\n".join(
        f"| {name} | {fmt_int(count)} |" for name, count in summary["counties"].most_common(12)
    )
    title = f"California Cannabis Licensing — {category}"
    slug_cat = re.sub(r"[^a-z0-9]+", "-", category.lower()).strip("-")
    if single:
        summary_text = (
            f"Department of Cannabis Control license registry segment snapshot "
            f"({fmt_int(summary['total'])} records; {snapshot_label.replace('-', ' ').title()})."
        )
    else:
        summary_text = (
            f"Department of Cannabis Control licensed-{slug_cat} establishment registry snapshot "
            f"({fmt_int(summary['total'])} records, {snapshot_label})."
        )
    tags_slug = slug_cat
    active_sorted = sorted(
        summary["active"],
        key=lambda record: (
            not clean(record.get("premiseCounty")),
            not clean(record.get("premiseCity")),
            clean(record.get("premiseCounty")),
            clean(record.get("premiseCity")),
            clean(record.get("licenseNumber")),
        ),
    )
    sample = active_sorted[:12]
    if sample:
        business_lines = "\n".join(
            f"| {clean(record.get('licenseNumber')) or '—'} | {clean(record.get('businessDbaName')) or clean(record.get('businessLegalName')) or '—'} | "
            f"{clean(record.get('premiseCity')) or '—'} | {clean(record.get('premiseCounty')) or '—'} |"
            for record in sample
        )
    else:
        business_lines = "| — | — | — | — |"

    return f"""---
id: law-and-use/{form_id}
title: "{title}"
parent: law-and-use
status: published
tags: ["law", "california", "licensing", "{tags_slug}"]
relations: []
summary: "{summary_text}"
---

# {title}

## Regulatory Context

California's licensed cannabis market is administered by the Department of Cannabis Control (DCC), formed in 2021 to consolidate the Bureau of Cannabis Control (BCC), CalCannabis Cultivation Licensing (CCL), and the Manufactured Cannabis Safety Branch (MCSB). Licenses are issued per premises and must be renewed; statuses are reported in the DCC Cannabis Unified License Search registry.

This record is a data snapshot of the {category} segment of the registry, captured from the DCC public license search API. It does not constitute legal advice.

## License Status Distribution

| License Status | License Count |
| --- | --- |
{status_lines}

## License Types in Category

| License Type | License Count |
| --- | --- |
{type_lines}

## Active Establishments by County (Top Counties)

| County | Active Licenses |
| --- | --- |
{county_lines}

## Notable Active Licensed Businesses (Sample)

| License Number | Business (DBA / Legal Name) | City | County |
| --- | --- | --- | --- |
{business_lines}

## Source

- Data source: DCC Cannabis Unified License Search — https://search.cannabis.ca.gov
- Registry refresh date: {refreshed}
- Snapshot file: `data/dcc/licenses-{snapshot_label}.csv`
"""


TITLE_PREFIX = "California Cannabis Licensing — "


def existing_category_records(records_dir: Path) -> dict[str, tuple[str, str]]:
    """Map category -> (filename, form_id) for records previously generated by this tool.

    Recognizes records by their title prefix, so re-runs overwrite in place
    instead of allocating duplicate form IDs.
    """
    found: dict[str, tuple[str, str]] = {}
    if not records_dir.is_dir():
        return found
    for path in records_dir.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        title_match = re.search(r"^title:\s*\"?" + re.escape(TITLE_PREFIX) + r"([^\"]+?)\"?\s*$", text, re.M)
        id_match = re.search(r"^id:\s*[^/]+/([A-Z]+-\d{4})", text, re.M)
        if title_match and id_match:
            category = title_match.group(1)
            found[category] = (path.name, id_match.group(1))
    return found


def build_single_record(licenses: list[dict], records_dir: Path, prefix: str,
                        snapshot_label: str, record_title: str) -> list[tuple[str, str]]:
    """Emit ONE summary record for the whole filtered segment.

    Uses a form-ID filename (e.g. TLAW-0009.md) so the repo's identity
    allocation policy stays deterministic, and is idempotent by title.
    """
    title = record_title or f"California Cannabis Licensing — {snapshot_label.replace('-', ' ').title()} Segment"
    category = title[len(TITLE_PREFIX):] if title.startswith(TITLE_PREFIX) else snapshot_label
    existing = existing_category_records(records_dir)
    previous = existing.get(category)
    if previous:
        filename, form_id = previous
    else:
        form_id = f"{prefix}-{next_form_id(records_dir, prefix):04d}"
        filename = f"{form_id}.md"
    body = build_record(category, licenses, form_id, snapshot_label, single=True)
    return [(filename, body)]


def generate_records(licenses: list[dict], records_dir: Path, prefix: str,
                     snapshot_label: str) -> list[tuple[str, str]]:
    """Group the segment by business-type category and emit one record per category.

    Idempotent: existing records generated by this tool (identified by their
    title prefix) are overwritten in place, reusing their form IDs.
    """
    by_category: dict[str, list[dict]] = defaultdict(list)
    for record in licenses:
        by_category[business_type_of(clean(record.get("licenseType")) or "")].append(record)

    existing = existing_category_records(records_dir)
    records: list[tuple[str, str]] = []
    form_number = next_form_id(records_dir, prefix)
    for category in sorted(by_category):
        group = by_category[category]
        previous = existing.get(category)
        if previous:
            filename, form_id = previous
        else:
            filename = f"{prefix}-{form_number:04d}.md"
            form_id = f"{prefix}-{form_number:04d}"
        body = build_record(category, group, form_id, snapshot_label)
        records.append((filename, body))
        if not previous:
            form_number += 1
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=Path("data/dcc"), help="raw snapshot output dir")
    parser.add_argument("--records-dir", type=Path, default=Path("content/law-and-use"))
    parser.add_argument("--prefix", default="TLAW")
    parser.add_argument("--status", default="", help="segment filter: license status (case-insensitive)")
    parser.add_argument("--business-type", default="", help="segment filter: Retailer/Distributor/Manufacturing/Cultivation/...")
    parser.add_argument("--county", default="", help="segment filter: premise county")
    parser.add_argument("--license-type", default="", help="segment filter: exact license type string")
    parser.add_argument("--max-licenses", type=int, default=0, help="cap segment size (0 = unlimited)")
    parser.add_argument("--one-record", action="store_true", help="emit a single summary record for the filtered segment")
    parser.add_argument("--record-title", default="", help="record title for --one-record mode")
    parser.add_argument("--refresh", action="store_true", help="force refetch even if a cached full snapshot exists")
    parser.add_argument("--no-records", action="store_true", help="skip markdown record generation")
    args = parser.parse_args()

    full_path = args.cache_dir / "licenses-all.json"
    if args.refresh or not full_path.exists():
        print("Fetching full DCC license registry...")
        all_licenses = fetch_licenses()
        args.cache_dir.mkdir(parents=True, exist_ok=True)
        full_path.write_text(json.dumps(all_licenses, ensure_ascii=False), encoding="utf-8")
        print(f"  cached {len(all_licenses)} records -> {full_path}")
    else:
        print(f"Loading cached full registry ({full_path})...")
        all_licenses = json.loads(full_path.read_text(encoding="utf-8"))

    segment = filter_segment(
        all_licenses,
        status=args.status,
        business_type=args.business_type,
        county=args.county,
        license_type=args.license_type,
        max_licenses=args.max_licenses,
    )
    label_parts = [args.status, args.business_type, args.county, args.license_type]
    label = "-".join(part.lower().replace(" ", "-") for part in label_parts if part) or "all"
    json_path, csv_path = write_snapshot(segment, args.cache_dir, label)
    print(f"Segment ({label}): {len(segment)} records -> {csv_path}")

    if not args.no_records:
        if args.one_record:
            records = build_single_record(segment, args.records_dir, args.prefix, label, args.record_title)
        else:
            records = generate_records(segment, args.records_dir, args.prefix, label)
        for filename, body in records:
            target = args.records_dir / filename
            target.write_text(body, encoding="utf-8")
            print(f"  wrote {target}")
        print(f"Generated {len(records)} record(s); trunk links to add:")
        for filename, body in records:
            title_line = body.splitlines()[2]
            title = title_line.split('title: "', 1)[1].rstrip('"')
            print(f"  - [{title}]({filename})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
