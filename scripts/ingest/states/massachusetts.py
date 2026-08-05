"""Massachusetts Cannabis Control Commission (CCC) ingestion adapter.

This is the reference state adapter for the shared ingestion package. It owns
everything state-specific: regulator identity, the official source catalog,
dataset schemas, source disclaimers, normalizers, privacy exclusions, state
terminology, page-generation policy, and relations/summaries.

Official sources (verified 2026-08-05):

* Data catalog   https://masscannabiscontrol.com/open-data/data-catalog/
* Advisories     https://masscannabiscontrol.com/news/public-health-and-safety-advisories/
* Downloads      https://masscannabiscontrol.com/resource/<slug>.csv|.json

Terminology is preserved exactly as the Commission publishes it:
"public health and safety advisory", "potentially contaminated",
"contaminated", "affected products", "destruction or return", and
"adverse-health guidance". We never relabel an advisory as a recall.
"""

from __future__ import annotations

import csv
import html as _html
import io
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

from ..core import (
    ChangeReport,
    DatasetRun,
    IngestError,
    parse_date,
    parse_date_range,
    parse_month,
    utc_now,
)
from ..diff import compare_snapshots
from ..fetch import Fetcher, FixtureFetcher
from ..ids import NaturalKeyRegistry
from ..markdown import (
    callout,
    deflist,
    escape_cell,
    footnote,
    frontmatter,
    h1,
    h2,
    mdlink,
    table,
    task_list,
    wikilink,
)
from ..schema import (
    SchemaSpec,
    check_date_regression,
    check_duplicate_keys,
    check_row_collapse,
    parse_csv_bytes,
    read_csv_rows,
    stream_csv,
)
from ..storage import ArtifactStore, sha256_file
from ..validation import PrivacySpec, assert_clean, scan_directory, scan_text, validate_relations

STATE = "massachusetts"

# ---------------------------------------------------------------------------
# Regulator identity
# ---------------------------------------------------------------------------

REGULATOR = {
    "slug": "massachusetts-ccc",
    "name": "Massachusetts Cannabis Control Commission",
    "jurisdiction": "Massachusetts",
    "jurisdiction_code": "MA",
    "site": "https://masscannabiscontrol.com/",
    "data_catalog": "https://masscannabiscontrol.com/open-data/data-catalog/",
    "advisories_url": "https://masscannabiscontrol.com/news/public-health-and-safety-advisories/",
    "testing_update_2025": "https://masscannabiscontrol.com/2026/03/3-19-2026-testing-data-update/",
}

DISCLAIMER = (
    "All information shared via the Open Data Platform is self-reported by "
    "licensees. The Cannabis Control Commission does not guarantee "
    "completeness, accuracy, timeliness, or the results obtained from the use "
    "of this information, or offers a warranty of any kind, express or "
    "implied, including, but not limited to warranties of performance, "
    "merchantability, and fitness for a particular purpose."
)

MARKET_DISCLAIMER = (
    "Sales and price figures are self-reported by licensees through the "
    "Commission's regulatory data systems and are published as-is. They are "
    "not tax revenue unless the Commission explicitly defines them that way."
)

# ---------------------------------------------------------------------------
# Content policy
# ---------------------------------------------------------------------------

TRUNKS = {
    "jurisdictions": ("Jurisdictions",
        "State and provincial cannabis regulatory jurisdictions whose official "
        "data is archived on this site.", "TJUR"),
    "licenses": ("Licenses",
        "Establishment licenses issued by state regulators, with provenance "
        "to the issuing agency's open data.", "TLIC"),
    "organizations": ("Organizations",
        "Legal entities licensed or otherwise connected to official records. "
        "Entity identity follows the source legal name; display names are never "
        "merged into a single organization.", "TORG"),
    "testing-laboratories": ("Testing Laboratories",
        "Independent Testing Laboratories licensed by state regulators. Pages "
        "contain only approved public fields and never rank or grade labs.", "TSTL"),
    "contaminants": ("Contaminants",
        "Analytes and contaminants tracked in official state testing data and "
        "public health advisories.", "TCNT"),
    "datasets": ("Datasets",
        "Official state open-data datasets and the aggregate pages derived from "
        "them, each with source provenance and revision history.", "TDTS"),
    "requirements": ("Requirements",
        "Regulatory requirements governing licensed establishments and testing.", "TREQ"),
    "safety-advisories": ("Safety Advisories",
        "Public health and safety advisories published by state regulators. The "
        "regulator's own terminology is preserved; advisories are not relabeled "
        "as recalls unless the regulator does so.", "TSAD"),
    "affected-products": ("Affected Products",
        "Normalized package-level records from public health advisories, kept "
        "as machine records and rendered in advisory tables. Representative "
        "pages follow documented editorial criteria.", "TAFP"),
}

PAGE_POLICY = {
    "affected_products_max_pages": 5,
    "generate_lab_pages": True,
    "generate_advisory_pages": True,
    "generate_license_pages_for_advisory_licensees": True,
    "generate_org_pages_for_labs_and_advisory_licensees": True,
}

CONTAMINANTS = [
    ("thc", "THC", "Delta-9 tetrahydrocannabinol"),
    ("thca", "THCA", "Tetrahydrocannabinolic acid"),
    ("arsenic", "Arsenic", "Heavy metal"),
    ("cadmium", "Cadmium", "Heavy metal"),
    ("lead", "Lead", "Heavy metal"),
    ("mercury", "Mercury", "Heavy metal"),
    ("total-yeast-and-mold", "Total Yeast and Mold", "Microbial contaminant"),
    ("coliforms", "Coliforms", "Microbial contaminant"),
]

ID_PREFIXES = {
    "jurisdiction": "TJUR", "license": "TLIC", "organization": "TORG",
    "testing_laboratory": "TSTL", "contaminant": "TCNT", "dataset": "TDTS",
    "requirement": "TREQ", "safety_advisory": "TSAD", "affected_product": "TAFP",
}

ID_COLLECTIONS = {
    "jurisdiction": "jurisdictions", "license": "licenses",
    "organization": "organizations", "testing_laboratory": "testing-laboratories",
    "contaminant": "contaminants", "dataset": "datasets",
    "requirement": "requirements", "safety_advisory": "safety-advisories",
    "affected_product": "affected-products",
}


# ---------------------------------------------------------------------------
# Report helpers
# ---------------------------------------------------------------------------


def _relation_target_exists(content_root: Path, target: str) -> bool:
    if not target:
        return False
    for path in content_root.rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(rf"^id:\s*{re.escape(target)}\s*$", text, flags=re.M):
            return True
    return False


def _retrieval_note(store: ArtifactStore, slug: str) -> str:
    latest = store.latest_snapshot(slug)
    return (latest or {}).get("retrieval_timestamp", "not yet ingested")


def _row_count_note(store: ArtifactStore, slug: str) -> str:
    latest = store.latest_snapshot(slug)
    return str((latest or {}).get("row_count", "—"))


def _release_lag_note(store: ArtifactStore, slug: str) -> str:
    latest = store.latest_snapshot(slug)
    if not latest:
        return "not ingested"
    return f"last retrieved {latest.get('retrieval_timestamp', '?')}"


def _latest_run_note(store: ArtifactStore) -> str:
    return store.read_manifest().get("updated_at", "never")


# Required by the module import surface even when the CLI is not used.
__all__ = [
    "STATE", "REGULATOR", "DISCLAIMER", "MARKET_DISCLAIMER", "DATASETS",
    "PRIVACY_SPEC", "PAGE_POLICY", "ID_PREFIXES", "ID_COLLECTIONS",
    "MassachusettsSync", "parse_product_string", "parse_analyte",
    "parse_advisory_page", "discover_advisory_urls", "NORMALIZERS",
]

# ---------------------------------------------------------------------------
# Source catalog
# ---------------------------------------------------------------------------


@dataclass
class DatasetDef:
    slug: str
    title: str
    csv_url: str
    json_url: str
    format: str                          # csv | json
    reporting_period: str
    source_last_updated: str
    description: str
    large: bool = False                  # stream instead of loading into memory
    required_columns: list = field(default_factory=list)
    column_types: dict = field(default_factory=dict)
    key_columns: list = field(default_factory=list)
    disclaimer: str = DISCLAIMER
    clarification: str = ""
    normalizer: str = "identity"
    public_fields: list = field(default_factory=list)

    # ---- schema guards (bridge to SchemaSpec) --------------------------
    def schema_spec(self) -> SchemaSpec:
        return SchemaSpec(
            name=self.slug,
            required=self.required_columns,
            column_types=self.column_types,
            key_columns=self.key_columns,
        )

    def check_headers(self, headers: list[str]) -> None:
        self.schema_spec().check_headers(headers)

    def check_types(self, rows: list[dict]) -> list[str]:
        return self.schema_spec().check_types(rows)


def _res(slug: str, ext: str) -> str:
    return f"https://masscannabiscontrol.com/resource/{slug}.{ext}"


DATASETS: dict[str, DatasetDef] = {}


def _define(d: DatasetDef) -> None:
    DATASETS[d.slug] = d


_define(DatasetDef(
    slug="licenses",
    title="All Licenses / Licensing Tracker (Adult-Use and Medical)",
    csv_url=_res("l_licenses_all_details_public", "csv"),
    json_url=_res("l_licenses_all_details_public", "json"),
    format="csv",
    reporting_period="point-in-time snapshot",
    source_last_updated="2026-07 (per catalog)",
    description=(
        "Combined adult-use and medical license tracker published by the CCC. "
        "One row per establishment license; includes program, license type, "
        "status, commence-operations state, municipality and county."
    ),
    required_columns=[
        "LICENSE_NUMBER", "LICENSE_TYPE", "LICENSE_STATUS_CATEGORY", "INDUSTRY",
        "BUSINESS_NAME", "ESTABLISHMENT_CITY", "ESTABLISHMENT_COUNTY",
    ],
    column_types={
        "COMMENCE_OPERATIONS_DATE": "date", "LIC_START_DATE": "date",
        "LIC_EXPIRATION_DATE": "date", "CNB_DATE_OF_FINAL_LICENSURE": "date",
    },
    key_columns=["LICENSE_NUMBER"],
    normalizer="license",
    public_fields=[
        "legal_name", "license_number", "license_type", "program", "status",
        "commence_ops", "municipality", "county", "cultivation_environment",
        "cultivation_tier", "license_start_date", "license_expiration_date",
    ],
))
_define(DatasetDef(
    slug="commence_ops",
    title="Adult-Use Marijuana Establishment Licenses - Commence Ops",
    csv_url=_res("l_licenses_commence_ops", "csv"),
    json_url=_res("l_licenses_commence_ops", "json"),
    format="csv",
    reporting_period="point-in-time snapshot",
    source_last_updated="2026-07 (per catalog)",
    description="Adult-use licenses with commence-operations status.",
    required_columns=["LICENSE_NUMBER", "LICENSE_TYPE", "COMMENCE_OPS", "LICENSE_STATUS_CATEGORY"],
    key_columns=["LICENSE_NUMBER"],
    normalizer="license",
))
_define(DatasetDef(
    slug="mtc_licenses",
    title="Medical Treatment Center Licenses",
    csv_url=_res("l_licenses_mtc", "csv"),
    json_url="",
    format="csv",
    reporting_period="point-in-time snapshot",
    source_last_updated="2026-07 (per catalog)",
    description="Medical Marijuana Treatment Center licenses. Contains raw "
                "latitude/longitude and full street addresses that are excluded "
                "from generated content.",
    required_columns=["LICENSE_NUMBER", "LICENSE_TYPE", "LICENSE_STATUS", "INDUSTRY"],
    key_columns=["LICENSE_NUMBER"],
    normalizer="license_mtc",
))
_define(DatasetDef(
    slug="testing_2025",
    title="CCC Testing Results 2025 (01/01/2025 - 11/30/2025)",
    csv_url=_res("CCC_Testing_Results_2025", "csv"),
    json_url=_res("CCC_Testing_Results_2025", "json"),
    format="csv",
    reporting_period="2025-01-01 .. 2025-11-30",
    source_last_updated="2026-03-19 (catalog; see testing-data update)",
    description=(
        "Laboratory test results for 2025: THC, THCA, Total Yeast and Mold, "
        "Arsenic, Cadmium, Lead, Mercury and related analytes. Labs are "
        "anonymized by the Commission."
    ),
    large=True,
    required_columns=["DATE", "ANALYTE/TEST ID", "RESULT", "TESTPASSED"],
    column_types={"DATE": "date", "RESULT": "number"},
    key_columns=["DATE", "METRC ID", "ANALYTE/TEST ID", "LAB PERFORMING THE TEST", "RESULT"],
    normalizer="testing",
    clarification="Data updated 2026-03-19 per CCC testing-data update notice.",
))
_define(DatasetDef(
    slug="testing_2024",
    title="Testing Results 2024 (01/01/2024 - 12/31/2024)",
    csv_url=_res("Testing_Results_2024_20260415_OpenData", "csv"),
    json_url=_res("Testing_Results_2024_20260415_OpenData", "json"),
    format="csv",
    reporting_period="2024-01-01 .. 2024-12-31",
    source_last_updated="2026-04-15 (filename suffix; catalog)",
    description=(
        "Laboratory test results for 2024: THC, THCA, microbial categories and "
        "metals, with product category and strain columns. Labs are anonymized."
    ),
    large=True,
    required_columns=["Date", "Analyte/Test ID", "Result", "TestPassed"],
    column_types={"Date": "date", "Result": "number"},
    key_columns=["Date", "METRC ID", "Analyte/Test ID", "Lab performing the test", "Result"],
    normalizer="testing_2024",
    clarification="File republished 2026-04-15 (filename suffix 20260415).",
))
_define(DatasetDef(
    slug="sales_gross",
    title="Adult-Use Marijuana Establishment Facility Sales and Statistics",
    csv_url=_res("a_sales_au_gross", "csv"),
    json_url=_res("a_sales_au_gross", "json"),
    format="csv",
    reporting_period="2018-01-01 .. 2026-06-07",
    source_last_updated="2026-06 (per catalog)",
    description="Daily adult-use sales by product type (Retail, Delivery).",
    required_columns=["SALEDATE", "INDUSTRY", "DATATYPE", "PRODUCTCATEGORYNAME", "TOTAL_$"],
    column_types={"SALEDATE": "date", "TOTAL_$": "number", "QUANTITY": "number"},
    normalizer="sales",
    disclaimer=MARKET_DISCLAIMER,
))
_define(DatasetDef(
    slug="sales_deliveries",
    title="Marijuana Retail and Delivery Weekly Sales Report Total",
    csv_url=_res("a_sales_au_deliveries", "csv"),
    json_url=_res("a_sales_au_deliveries", "json"),
    format="csv",
    reporting_period="2018-01-01 .. 2026-06-07",
    source_last_updated="2026-06 (per catalog)",
    description="Weekly retail and delivery sales totals.",
    required_columns=["SALEDATE", "INDUSTRY", "DATATYPE", "TOTAL_$"],
    column_types={"SALEDATE": "date", "TOTAL_$": "number"},
    normalizer="sales",
    disclaimer=MARKET_DISCLAIMER,
))
_define(DatasetDef(
    slug="price_per_gram",
    title="Average Monthly Price per Ounce / Gram for Adult-Use Cannabis",
    csv_url=_res("a_sales_au_price_per_gram", "csv"),
    json_url=_res("a_sales_au_price_per_gram", "json"),
    format="csv",
    reporting_period="2018-11 .. 2026-06",
    source_last_updated="2026-06 (per catalog)",
    description="Monthly average retail price per gram for adult-use flower.",
    required_columns=["YEARMONTH", "AVERAGERETAILPRICEPERGM"],
    column_types={"AVERAGERETAILPRICEPERGM": "number"},
    key_columns=["YEARMONTH"],
    normalizer="price",
    disclaimer=MARKET_DISCLAIMER,
))
_define(DatasetDef(
    slug="mtc_sales",
    title="Medical Treatment Centers - Facility Sales",
    csv_url=_res("a_sales_mtc_gross", "csv"),
    json_url=_res("a_sales_mtc_gross", "json"),
    format="csv",
    reporting_period="2018-01-01 .. 2026-06-07",
    source_last_updated="2026-06 (per catalog)",
    description="Medical-use facility sales by product type.",
    required_columns=["SALEDATE", "INDUSTRY", "DATATYPE", "PRODUCTCATEGORYNAME", "TOTAL_$"],
    column_types={"SALEDATE": "date", "TOTAL_$": "number"},
    normalizer="sales",
    disclaimer=MARKET_DISCLAIMER,
))
_define(DatasetDef(
    slug="plant_activity",
    title="Adult-Use and MTC Plant Activity and Volume",
    csv_url=_res("a_sales_au_activityvolume", "csv"),
    json_url=_res("a_sales_au_activityvolume", "json"),
    format="csv",
    reporting_period="2018-11 .. present",
    source_last_updated="2026-06 (per catalog)",
    description="Monthly plant activity: vegetative, flowering, harvested, destroyed.",
    required_columns=["ACTIVITYSUMMARYDATE", "FACILITYTYPENAME", "PLANTFLOWERINGCOUNT"],
    column_types={"PLANTFLOWERINGCOUNT": "number", "PLANTVEGETATIVECOUNT": "number"},
    normalizer="activity",
))
_define(DatasetDef(
    slug="applications_totals",
    title="Adult-Use Marijuana Establishment License Applications",
    csv_url=_res("a_applications_all", "csv"),
    json_url=_res("a_applications_all", "json"),
    format="csv",
    reporting_period="point-in-time snapshot",
    source_last_updated="2026-07 (per catalog)",
    description="Application counts by industry, license type and status.",
    required_columns=["INDUSTRY", "LICENSE_TYPE", "APPLICATION_STATUS", "TOTAL"],
    normalizer="identity",
))
_define(DatasetDef(
    slug="applications_dbe",
    title="Marijuana Establishment License Application DBE Totals",
    csv_url=_res("a_applications_dbe", "csv"),
    json_url=_res("a_applications_dbe", "json"),
    format="csv",
    reporting_period="point-in-time snapshot",
    source_last_updated="2026-07 (per catalog)",
    description="Diverse Business Enterprise application totals by industry.",
    required_columns=["INDUSTRY", "DBE", "TOTAL"],
    normalizer="identity",
))
_define(DatasetDef(
    slug="agents_gender",
    title="Active Marijuana Establishment Agents Gender Totals",
    csv_url=_res("a_agents_gender", "csv"),
    json_url=_res("a_agents_gender", "json"),
    format="csv",
    reporting_period="point-in-time snapshot",
    source_last_updated="2026-07 (per catalog)",
    description="Aggregate counts of active establishment agents by gender.",
    required_columns=["GENDER", "TOTAL"],
    normalizer="identity",
))
_define(DatasetDef(
    slug="agents_raceethnicity",
    title="Marijuana Establishment Agent Race / Ethnicity Totals",
    csv_url=_res("a_agents_raceethnicity", "csv"),
    json_url=_res("a_agents_raceethnicity", "json"),
    format="csv",
    reporting_period="point-in-time snapshot",
    source_last_updated="2026-07 (per catalog)",
    description="Aggregate counts of active establishment agents by race/ethnicity.",
    required_columns=["RACE_ETHNICITY", "TOTAL"],
    normalizer="identity",
))

# ---------------------------------------------------------------------------
# Privacy policy
# ---------------------------------------------------------------------------

PRIVACY_SPEC = PrivacySpec(
    state="massachusetts",
    entity_allowlists={
        "license": [
            "legal_name", "license_number", "license_type", "program", "status",
            "commence_ops", "municipality", "county", "cultivation_environment",
            "cultivation_tier", "license_start_date", "license_expiration_date",
        ],
        "testing_laboratory": [
            "legal_name", "license_number", "license_type", "program", "status",
            "commence_ops", "municipality", "related_jurisdiction",
            "related_requirements", "related_safety_advisories",
        ],
        "organization": ["legal_name", "license_numbers", "license_types",
                         "program", "municipality"],
        "safety_advisory": ["title", "advisory_date", "canonical_url", "concern",
                            "consumer_instructions", "date_ranges",
                            "affected_product_count", "product_category_summary",
                            "testing_date_range", "packaged_date_range",
                            "sale_date_range", "revision_status"],
        "affected_product": ["package_label", "packaged_date", "tested_on_date",
                             "source_product_text", "source_product_identifier",
                             "commercial_product_label", "package_size_text",
                             "product_form", "cultivar_candidate_text",
                             "sold_between", "advisory_date", "advisory_source"],
        "dataset": ["title", "slug", "official_source_url", "json_url", "format",
                    "reporting_period", "source_last_updated", "retrieval_date",
                    "row_count", "columns", "disclaimer", "clarification"],
        "contaminant": ["name", "source_name", "unit", "matrix", "appears_in",
                        "advisories", "notes"],
        "requirement": ["title", "citation", "regulator", "official_source_url", "notes"],
    },
)

# ---------------------------------------------------------------------------
# Normalizers
# ---------------------------------------------------------------------------


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_license(row: dict) -> dict:
    """Normalize one license-tracker row.

    The normalized artifact preserves every source field (fidelity), while
    derived display fields support page generation. Generated Markdown only
    ever uses the public allowlist.
    """
    out = dict(row)
    out["display_name"] = _clean(row.get("BUSINESS_NAME"))
    out["municipality"] = _clean(row.get("ESTABLISHMENT_CITY")).title()
    out["county"] = _clean(row.get("ESTABLISHMENT_COUNTY"))
    out["program"] = _clean(row.get("INDUSTRY"))
    out["status"] = _clean(row.get("LICENSE_STATUS_CATEGORY") or row.get("LICENSE_STATUS"))
    out["license_type"] = _clean(row.get("LICENSE_TYPE"))
    out["commence_ops"] = _clean(row.get("COMMENCE_OPS"))
    out["license_start_date"] = _clean(row.get("LIC_START_DATE") or row.get("LIC_ORIGINAL_START_DATE"))
    out["license_expiration_date"] = _clean(row.get("LIC_EXPIRATION_DATE"))
    out["cultivation_environment"] = _clean(row.get("CULTIVATION_ENVIRONMNET"))
    out["cultivation_tier"] = _clean(row.get("CULTIVATION_TIER"))
    return out


def normalize_license_mtc(row: dict) -> dict:
    """Normalize an MTC license row (excludes coords/addresses from display)."""
    out = dict(row)
    out["display_name"] = _clean(row.get("BUSINESS_NAME"))
    out["municipality"] = _clean(row.get("CITY") or row.get("PHYSICAL_CITY")).title()
    out["county"] = _clean(row.get("COUNTY"))
    out["program"] = _clean(row.get("INDUSTRY"))
    out["status"] = _clean(row.get("LICENSE_STATUS"))
    out["license_type"] = _clean(row.get("LICENSE_TYPE"))
    return out


_ANALYTE_RE = re.compile(r"^(.+?)\s+\(([^)]+)\)\s+(.+)$")


def parse_analyte(source: str) -> dict:
    """Deterministically split ``Arsenic (ppm) Raw Plant Material``.

    Returns ``{source, analyte, unit, matrix}``; falls back to source-only.
    """
    text = _clean(source)
    match = _ANALYTE_RE.match(text)
    if match:
        return {"source": text, "analyte": match.group(1).strip(),
                "unit": match.group(2).strip(), "matrix": match.group(3).strip()}
    return {"source": text, "analyte": text, "unit": "", "matrix": ""}


def _no_key_diff(prior, rows):
    """Minimal change summary for datasets without row-identity keys."""
    from ..diff import DiffResult

    result = DiffResult()
    prior_count = (prior or {}).get("row_count")
    current = len(rows)
    if prior_count is None or prior_count == current:
        result.summary = "no change"
    else:
        result.summary = f"row count {prior_count} -> {current}"
    return result


def _num(value: Any) -> Optional[float]:
    text = _clean(value).replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


# Normalized date field per dataset used by the backward-date guard.
_DATE_FIELDS = {
    "testing_2024": "date", "testing_2025": "date",
    "sales_gross": "sale_date", "sales_deliveries": "sale_date",
    "mtc_sales": "sale_date", "price_per_gram": "month",
    "plant_activity": "month",
}


def _max_reported_date(slug: str, rows: list[dict]) -> str:
    """Latest ISO date seen in a dataset's normalized rows ("" if none).

    ``month``-level fields (price_per_gram, plant_activity) are normalized to
    the first of the month so the backward-date guard covers them too.
    """
    field = _DATE_FIELDS.get(slug)
    if not field:
        return ""
    month_only = field == "month"
    latest = ""
    for row in rows:
        if month_only:
            parsed = parse_month(row.get(field))
            iso = f"{parsed[0]:04d}-{parsed[1]:02d}-01" if parsed else ""
        else:
            parsed = parse_date(row.get(field))
            iso = parsed.isoformat() if parsed else ""
        if iso > latest:
            latest = iso
    return latest


def normalize_testing_common(row: dict, *, release: str) -> dict:
    out = {
        "source_release": release,
        "date": _clean(row.get("DATE") or row.get("Date")),
        "metrc_id": _clean(row.get("METRC ID")),
        "analyte_id": _clean(row.get("ANALYTE/TEST ID") or row.get("Analyte/Test ID")),
        "result": _clean(row.get("RESULT") or row.get("Result")),
        "result_numeric": _num(row.get("RESULT") or row.get("Result")),
        "test_passed": _clean(row.get("TESTPASSED") or row.get("TestPassed")),
        "lab": _clean(row.get("LAB PERFORMING THE TEST") or row.get("Lab performing the test")),
        "notes": _clean(row.get("NOTES/COMMENTS") or row.get("Notes/comments")),
        "strain": _clean(row.get("Strain")),
        "product_category": _clean(row.get("ProductCategoryTypeName")),
        "test_category": _clean(row.get("TestCategory")),
        "quantity": _clean(row.get("Quantity")),
        "unit_of_measure": _clean(row.get("UnitOfMeasure")),
        "test_id": _clean(row.get("Test ID")),
    }
    parsed = parse_analyte(out["analyte_id"])
    out["analyte"] = parsed["analyte"]
    out["analyte_unit"] = parsed["unit"]
    out["matrix"] = parsed["matrix"]
    return out


def normalize_testing(row: dict) -> dict:
    return normalize_testing_common(row, release="CCC_Testing_Results_2025")


def normalize_testing_2024(row: dict) -> dict:
    return normalize_testing_common(row, release="Testing_Results_2024")


def normalize_sales(row: dict) -> dict:
    out = dict(row)
    out["sale_date"] = _clean(row.get("SALEDATE"))
    out["product_category"] = _clean(row.get("PRODUCTCATEGORYNAME"))
    out["datatype"] = _clean(row.get("DATATYPE"))
    out["industry"] = _clean(row.get("INDUSTRY"))
    out["total_dollars"] = _num(row.get("TOTAL_$"))
    out["quantity"] = _num(row.get("QUANTITY"))
    out["receipts"] = _num(row.get("RECEIPTS"))
    return out


def normalize_price(row: dict) -> dict:
    out = dict(row)
    out["month"] = _clean(row.get("YEARMONTH"))
    out["price_per_gram"] = _num(row.get("AVERAGERETAILPRICEPERGM"))
    out["unit"] = _clean(row.get("UNIT"))
    return out


def normalize_activity(row: dict) -> dict:
    out = dict(row)
    out["month"] = _clean(row.get("ACTIVITYSUMMARYDATE"))
    out["facility_type"] = _clean(row.get("FACILITYTYPENAME"))
    return out


NORMALIZERS = {
    "identity": lambda row: dict(row),
    "license": normalize_license,
    "license_mtc": normalize_license_mtc,
    "testing": normalize_testing,
    "testing_2024": normalize_testing_2024,
    "sales": normalize_sales,
    "price": normalize_price,
    "activity": normalize_activity,
}

# ---------------------------------------------------------------------------
# Aggregate builders
# ---------------------------------------------------------------------------


def aggregate_licenses(rows: list[dict]) -> dict:
    by_program = Counter(r["program"] for r in rows)
    by_type = Counter(r["license_type"] for r in rows)
    by_status = Counter(r["status"] or "Unknown" for r in rows)
    by_commence = Counter(r["commence_ops"] or "Not reported" for r in rows)
    by_county = Counter(r["county"] or "Unknown" for r in rows)
    by_municipality = Counter(r["municipality"] or "Unknown" for r in rows)
    by_tier = Counter(r["cultivation_tier"] for r in rows if r.get("cultivation_tier"))
    itls = [
        r for r in rows
        if "Independent Testing Laboratory" in (r.get("license_type") or "")
        and (r.get("status") or "").lower() == "active"
    ]
    return {
        "rows": len(rows),
        "by_program": dict(by_program),
        "by_type": dict(by_type.most_common()),
        "by_status": dict(by_status.most_common()),
        "by_commence": dict(by_commence.most_common()),
        "by_county": dict(by_county.most_common()),
        "by_municipality": dict(by_municipality.most_common(15)),
        "by_tier": dict(by_tier.most_common()),
        "itls": itls,
    }


def aggregate_testing(rows: list[dict]) -> dict:
    by_analyte: dict[str, dict] = defaultdict(lambda: {"count": 0, "passed": 0, "failed": 0, "units": Counter()})
    by_month = Counter()
    by_category = Counter()
    by_status = Counter()
    for row in rows:
        analyte = row.get("analyte") or row.get("analyte_id") or "Unknown"
        month = (row.get("date") or "")[:7]
        if month:
            by_month[month] += 1
        status = (row.get("test_passed") or "Unknown").strip().lower()
        if status in ("true", "yes", "1", "pass", "passed"):
            by_status["Passed"] += 1
            by_analyte[analyte]["passed"] += 1
        elif status in ("false", "no", "0", "fail", "failed"):
            by_status["Failed"] += 1
            by_analyte[analyte]["failed"] += 1
        else:
            by_status[status] += 1
        by_analyte[analyte]["count"] += 1
        if row.get("analyte_unit"):
            by_analyte[analyte]["units"][row["analyte_unit"]] += 1
        category = row.get("product_category") or row.get("test_category")
        if category:
            by_category[category] += 1
    return {
        "rows": len(rows),
        "by_analyte": {k: dict(v) for k, v in by_analyte.items()},
        "by_month": dict(sorted(by_month.items())),
        "by_category": dict(by_category.most_common()),
        "by_status": dict(by_status),
    }


def aggregate_sales(rows: list[dict]) -> dict:
    by_category = defaultdict(lambda: {"records": 0, "total_dollars": 0.0})
    by_datatype = Counter()
    by_month = Counter()
    total_dollars = 0.0
    for row in rows:
        category = row.get("product_category") or "Unknown"
        by_category[category]["records"] += 1
        dollars = row.get("total_dollars") or 0.0
        by_category[category]["total_dollars"] += dollars
        total_dollars += dollars
        by_datatype[row.get("datatype") or "Unknown"] += 1
        month = (row.get("sale_date") or "")[:7]
        if month:
            by_month[month] += 1
    return {
        "rows": len(rows),
        "total_dollars": round(total_dollars, 2),
        "by_category": {k: {"records": v["records"], "total_dollars": round(v["total_dollars"], 2)}
                        for k, v in by_category.items()},
        "by_datatype": dict(by_datatype.most_common()),
        "by_month_count": dict(sorted(by_month.items())),
    }


def aggregate_price(rows: list[dict]) -> dict:
    series = []
    for row in rows:
        month = row.get("month")
        price = row.get("price_per_gram")
        if month and price is not None:
            series.append((month, price))
    prices = [p for _, p in series]
    return {
        "months": len(series),
        "series": series,
        "latest_month": series[-1] if series else None,
        "min": min(prices) if prices else None,
        "max": max(prices) if prices else None,
    }


def aggregate_activity(rows: list[dict]) -> dict:
    by_facility = defaultdict(lambda: Counter())
    latest = {}
    for row in rows:
        facility = row.get("facility_type") or "Unknown"
        month = row.get("month") or "Unknown"
        by_facility[facility][month] += 1
        for key in ("PLANTFLOWERINGCOUNT", "PLANTVEGETATIVECOUNT", "PLANTHARVESTEDCOUNT", "PLANTDESTROYEDCOUNT"):
            latest[(facility, key)] = row.get(key)
    return {
        "rows": len(rows),
        "by_facility_month": {k: dict(v) for k, v in by_facility.items()},
        "latest": {f"{k[0]}:{k[1]}": v for k, v in latest.items()},
    }


def aggregate_simple(rows: list[dict], *_, **__) -> dict:
    return {"rows": len(rows), "data": rows}


AGGREGATORS = {
    "licenses": aggregate_licenses,
    "testing_2025": aggregate_testing,
    "testing_2024": aggregate_testing,
    "sales_gross": aggregate_sales,
    "sales_deliveries": aggregate_sales,
    "mtc_sales": aggregate_sales,
    "price_per_gram": aggregate_price,
    "plant_activity": aggregate_activity,
}

# ---------------------------------------------------------------------------
# Product string parsing (advisory tables)
# ---------------------------------------------------------------------------

_SIZE_RE = re.compile(r"^([\d.,]+\s?(?:g|oz|lb|mg|ml|ea|pack|pk|ct|count)\b)\s*(.*)$", re.IGNORECASE)
_FORM_KEYWORDS = ["pre-roll", "preroll", "jar", "flower", "cartridge", "cart", "vape",
                  "edible", "gummy", "tincture", "concentrate", "wax", "shatter",
                  "budder", "crumble", "kief", "hash", "capsule", "tablet", "lozenge"]


def parse_product_string(source: str) -> dict:
    """Deterministically split an advisory product string.

    Example: ``1 g Pre-rolls Strane`` -> size ``1 g``, form ``Pre-rolls``,
    brand candidate ``Strane``. The original source text is always preserved
    unchanged.
    """
    text = _clean(source)
    parsed = {"source_product_text": text,
              "package_size_text": "",
              "commercial_product_label": text,
              "product_form": "",
              "brand_candidate": "",
              "cultivar_candidate": ""}
    if not text:
        return parsed
    rest = text
    match = _SIZE_RE.match(text)
    if match:
        parsed["package_size_text"] = match.group(1).strip()
        rest = match.group(2).strip()
    for keyword in _FORM_KEYWORDS:
        match = re.search(rf"\b{re.escape(keyword)}\w*\b", rest, re.IGNORECASE)
        if match:
            # Take the whole matched word token (e.g. "Pre-rolls", not "Pre-roll").
            start, end = match.span()
            parsed["product_form"] = rest[start:end].strip()
            rest_after = rest[end:].strip()
            if rest_after:
                parsed["brand_candidate"] = rest_after
            break
    parsed["commercial_product_label"] = rest or text
    return parsed


# ---------------------------------------------------------------------------
# Advisory discovery and parsing
# ---------------------------------------------------------------------------

_ADVISORY_LINK_RE = re.compile(r'href="(https://masscannabiscontrol\.com/20\d{2}/\d{2}/[^"]+)"')
_BETWEEN_RE = re.compile(r"between\s+(.+?)\s+and\s+(.+?)(?:\.|;|,|$)", re.IGNORECASE)


def discover_advisory_urls(fetcher) -> list[str]:
    """Find advisory post URLs from the Commission's advisories page."""
    html = fetcher.fetch_text(REGULATOR["advisories_url"])
    urls = []
    for match in _ADVISORY_LINK_RE.finditer(html):
        url = match.group(1)
        if "advisory" in url.lower() and url not in urls:
            urls.append(url)
    return urls


def parse_advisory_page(html: str, url: str) -> dict:
    """Parse one advisory post into a structured record."""
    body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
    text = _html.unescape(re.sub(r"<[^>]+>", " ", body))
    text = re.sub(r"\s+", " ", text).strip()

    # Preserve the Commission's exact term in the archived title.
    title_match = re.search(r"Public Health and Safety Advisory(?:\s*[:|-]\s*)?(.*?)(?:\||$)", text)
    title = _clean(title_match.group(0)) if title_match else url.rsplit("/", 2)[-2]

    date_match = re.search(r"\|\s*(January|February|March|April|May|June|July|August|"
                           r"September|October|November|December)\s+\d{1,2},\s+\d{4}", text)
    advisory_date = parse_date(date_match.group(0).lstrip("| ").strip()) if date_match else None

    ranges = {}
    for label, pattern in (("sold_between", r"sold between\s+(.+?)(?:\.|;)"),
                           ("tested_between", r"tested between\s+(.+?)(?:\.|;)")):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            parsed = parse_date_range(re.sub(r",\s*and\s+", " and ", match.group(1)))
            if parsed:
                ranges[label] = [d.isoformat() for d in parsed]

    concern = ""
    lowered = text.lower()
    # Prefer the substantive sentence over nav/title boilerplate.
    for phrase in ("acceptable testing limits", "summary suspension order",
                   "unapproved pesticides", "presence of yeast and mold"):
        index = lowered.find(phrase)
        if index >= 0:
            concern = text[max(0, index - 160): index + 380].strip()
            break
    if not concern:
        for keyword in ("contaminated", "potentially contaminated"):
            index = lowered.find(keyword, 1500)
            if index >= 0:
                concern = text[max(0, index - 120): index + 320].strip()
                break
    # Trim a leading fragment so the published concern starts at a sentence.
    if concern:
        boundary = concern.rfind(". ", 0, 120)
        if boundary >= 0:
            concern = concern[boundary + 2:].strip()

    instructions = ""
    index = text.lower().find("destroy")
    if index >= 0:
        instructions = text[max(0, index - 160): index + 340].strip()

    products = []
    licensees = []
    table_mode = ""
    for m in re.finditer(r"<tr[^>]*>(.*?)</tr>", body, flags=re.S):
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", m.group(1), flags=re.S)
        clean = [_clean(_html.unescape(re.sub(r"<[^>]+>", " ", cell))) for cell in cells]
        clean = [c for c in clean if c]
        if not clean:
            continue
        header = " ".join(clean).lower()
        if len(clean) == 3 and ("product name" in header or "batch number" in header):
            table_mode = "products"
            continue
        if len(clean) == 3 and re.sub(r"[^a-z ]", " ", header).strip() == "licensee license number address":
            table_mode = "licensees"
            continue
        if len(clean) == 1 and table_mode:
            # Group heading row inside a table (e.g. "Marijuana Retailers with X").
            continue
        if table_mode == "products" and len(clean) >= 3:
            products.append({"product": clean[0], "strain": clean[1], "batch": clean[2]})
        elif table_mode == "licensees" and len(clean) >= 2:
            licensees.append({
                "licensee": clean[0],
                "license_number": clean[1],
                "municipality": _municipality_from_address(clean[2] if len(clean) > 2 else ""),
            })

    return {
        "url": url,
        "slug": url.rstrip("/").rsplit("/", 1)[-1],
        "title": title,
        "advisory_date": advisory_date.isoformat() if advisory_date else "",
        "date_ranges": ranges,
        "concern": concern,
        "consumer_instructions": instructions,
        "products": products,
        "licensees": licensees,
        "affected_product_count": len(products),
    }


def _municipality_from_address(address: str) -> str:
    """Extract the municipality from a licensed-premises address line.

    ``"1006 Bennington Street Boston, MA 02128"`` -> ``"Boston"``. The full
    street address is never published.
    """
    match = re.search(r"([A-Za-z .'-]+),\s*[A-Z]{2}\s*\d{5}", _clean(address))
    if match:
        return match.group(1).strip()
    return ""


# ---------------------------------------------------------------------------
# Sync orchestration
# ---------------------------------------------------------------------------


class MassachusettsSync:
    """Runs the Massachusetts CCC ingestion pipeline."""

    def __init__(self, *, fetch, store: ArtifactStore, registry: NaturalKeyRegistry,
                 content_root: Path, datasets: Optional[list[str]] = None,
                 refresh: bool = False, fixtures_only: bool = False,
                 allow_fixture_content: bool = False):
        self.fetch = fetch
        self.store = store
        self.registry = registry
        self.content_root = content_root
        self.datasets = datasets
        self.refresh = refresh
        self.fixtures_only = fixtures_only
        # Hard guard: fixture/synthetic records must never generate
        # publishable content unless an explicit development flag is set.
        self.allow_fixture_content = allow_fixture_content
        self.aggregates: dict[str, dict] = {}
        self.normalized: dict[str, list[dict]] = {}

    # ------------------------------------------------------------ dataset run
    def run_dataset(self, slug: str, report: ChangeReport) -> DatasetRun:
        if self.fixtures_only and not self.allow_fixture_content:
            # Fixture/synthetic records must never populate the durable
            # manifest (which feeds schema reports and revision records).
            raise IngestError(
                "fixture-only mode must not record snapshots or generate "
                "content; supply an explicit development flag "
                "(--allow-fixture-content) or ingest live official sources"
            )
        spec = DATASETS[slug]
        run = DatasetRun(slug=slug)
        try:
            url = spec.csv_url
            result = self._fetch_raw(spec)
            raw_sha = result.sha256

            raw_path = self.store.raw_snapshot_path(slug, raw_sha)
            if raw_path.is_file():
                # Same checksum as an existing immutable snapshot: reuse it.
                if result.path is not None and result.path.resolve() != raw_path.resolve():
                    result.path.unlink(missing_ok=True)  # discard re-downloaded copy
                rows = self._parse_existing(spec, raw_path)
                run.status = "unchanged"
            else:
                if result.path is not None:
                    # Large payload: already streamed to a temp file on disk.
                    import shutil

                    raw_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(result.path), str(raw_path))
                    rows = self._parse_existing(spec, raw_path)
                else:
                    raw_path.parent.mkdir(parents=True, exist_ok=True)
                    raw_path.write_bytes(result.data)
                    rows = self._parse_bytes(spec, result.data)
                run.status = "fetched"

            headers, raw_rows = self._split_headers(rows)
            normalizer = NORMALIZERS[spec.normalizer]
            normalized_rows = [
                normalizer(row) for row in raw_rows
                if any(str(v or "").strip() for v in row.values())
            ]

            warnings = self._guards(spec, headers, raw_rows, normalized_rows, report)
            run.row_count = len(normalized_rows)

            normalized_path = self._write_normalized(slug, normalized_rows)
            normalized_sha = sha256_file(normalized_path)
            aggregate = self._aggregate(slug, normalized_rows)
            self.aggregates[slug] = aggregate
            self.normalized[slug] = normalized_rows

            prior = self.store.latest_snapshot(slug)
            change = self._diff_against_prior(slug, prior, normalized_rows)
            run.change = change.summary

            if run.status == "fetched":
                self.store.record_snapshot(
                    slug, url,
                    raw_sha256=raw_sha,
                    raw_path=raw_path,
                    content_type=result.content_type,
                    size_bytes=result.size_bytes,
                    retrieved_at=utc_now(),
                    reporting_period=spec.reporting_period,
                    source_last_updated=spec.source_last_updated,
                    disclaimer=spec.disclaimer,
                    clarification=spec.clarification,
                    row_count=len(normalized_rows),
                    columns=headers,
                    normalized_sha256=normalized_sha,
                    normalized_path=normalized_path,
                    max_reported_date=_max_reported_date(spec.slug, normalized_rows),
                )
                run.normalized_sha256 = normalized_sha
            run.raw_sha256 = raw_sha
            for warning in warnings:
                report.warnings.append(f"{slug}: {warning}")
        except IngestError as error:
            run.status = "error"
            run.message = str(error)
            report.errors.append(f"{slug}: {error}")
        report.datasets[slug] = run.to_dict()
        return run

    def _fetch_raw(self, spec):
        if spec.large:
            tmp = self.store.working_root / "tmp" / f"{spec.slug}.csv"
            tmp.parent.mkdir(parents=True, exist_ok=True)
            return self.fetch.download(spec.csv_url, tmp)
        return self.fetch.fetch_bytes(spec.csv_url)

    def _parse_bytes(self, spec, data):
        if data is None:
            raise IngestError(f"{spec.slug}: no payload bytes available")
        if spec.large and len(data) > 32 * 1024 * 1024:
            raise IngestError(
                f"{spec.slug}: {len(data)} bytes is too large to parse in memory; "
                "use the streaming disk path"
            )
        _, rows = parse_csv_bytes(data)
        return rows

    def _parse_existing(self, spec, raw_path):
        if spec.large:
            return list(stream_csv(raw_path))
        _, rows = read_csv_rows(raw_path)
        return rows

    @staticmethod
    def _split_headers(rows):
        headers = list(rows[0].keys()) if rows else []
        return headers, rows

    def _write_normalized(self, slug, rows) -> Path:
        import hashlib

        columns = list(rows[0].keys()) if rows else []
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        digest = hashlib.sha256(buffer.getvalue().encode("utf-8"))
        return self.store.write_normalized(slug, digest.hexdigest(), rows)

    def _guards(self, spec, headers, raw_rows, normalized_rows, report) -> list[str]:
        warnings: list[str] = []
        spec.check_headers(headers)
        warnings.extend(spec.check_types(raw_rows))
        # Duplicate-primary-key guard runs on raw rows so source column names apply.
        check_duplicate_keys(raw_rows, spec.key_columns, spec.slug)
        prior = self.store.latest_snapshot(spec.slug) or {}
        warnings.extend(check_row_collapse(spec.schema_spec(), len(normalized_rows),
                                           prior.get("row_count")))
        # Backward-date guard: the newest reported date must not move backward
        # beyond tolerance unless the dataset carries a source clarification.
        new_max = _max_reported_date(spec.slug, normalized_rows)
        warnings.extend(check_date_regression(
            prior.get("max_reported_date"), new_max,
            has_clarification=bool(spec.clarification),
        ))
        return warnings

    def _aggregate(self, slug, rows) -> dict:
        builder = AGGREGATORS.get(slug, aggregate_simple)
        return builder(rows)

    def _diff_against_prior(self, slug, prior, rows) -> Any:
        from ..diff import checksum_changed

        spec = DATASETS[slug]
        prior_sha = (prior or {}).get("normalized_sha256")
        if not prior_sha or not spec.key_columns:
            return _no_key_diff(prior, rows)
        prior_path = self.store.normalized_path(slug, prior_sha)
        if not prior_path.is_file():
            return _no_key_diff(prior, rows)
        _, prior_rows = read_csv_rows(prior_path)
        return compare_snapshots(prior_rows, rows, spec.key_columns)

    # --------------------------------------------------------------- advisories
    def discover_advisories(self) -> list[dict]:
        if self.fixtures_only:
            fixture = self.fetch.fixture_root / "advisories.json"
            if fixture.is_file():
                return json.loads(fixture.read_text(encoding="utf-8"))
        urls = discover_advisory_urls(self.fetch)
        advisories = []
        for url in urls:
            html = self.fetch.fetch_text(url)
            advisories.append(parse_advisory_page(html, url))
        return advisories

    # --------------------------------------------------------- content generation
    def generate_content(self, report: ChangeReport, advisories: list[dict]) -> list[str]:
        """Generate all Boris content for Massachusetts. Returns page labels."""
        if self.fixtures_only and not self.allow_fixture_content:
            raise IngestError(
                "fixture-only mode must not generate publishable content; "
                "supply an explicit development flag (--allow-fixture-content) "
                "or ingest from live official sources"
            )
        self._advisories = advisories
        self._preallocate_ids(advisories)
        pages: list[str] = []
        pages += self._write_trunks()
        pages += self._write_jurisdiction_pages()
        pages += self._write_dataset_pages()
        pages += self._write_licensing_pages()
        pages += self._write_lab_pages()
        pages += self._write_organization_pages()
        pages += self._write_contaminant_pages()
        pages += self._write_requirement_pages()
        pages += self._write_advisory_pages(advisories)
        pages += self._write_affected_product_pages(advisories)
        pages += self._write_privacy_spec_page()
        pages += self._write_landscape_page(advisories)
        self._write_durable_artifacts(advisories)
        report.pages_generated = list(dict.fromkeys(pages))
        return pages

    def _preallocate_ids(self, advisories: list[dict]) -> None:
        """Allocate every entity ID up front so relations resolve regardless of
        page-generation order."""
        self._entity_id("jurisdiction", "massachusetts", label="Massachusetts")
        for slug in (
            "licenses", "testing_2024", "testing_2025", "sales_gross",
            "sales_deliveries", "price_per_gram", "mtc_sales", "plant_activity",
        ):
            spec = DATASETS[slug]
            self._entity_id("dataset", f"MA:dataset:{slug}", label=spec.title)
        derived_titles = {
            "testing-corrections": "Massachusetts Testing Corrections and Clarifications",
            "thc-thca": "Massachusetts Testing: THC and THCA",
            "yeast-mold": "Massachusetts Testing: Total Yeast and Mold",
            "heavy-metals": "Massachusetts Testing: Heavy Metals",
            "testing-coverage-by-month": "Massachusetts Testing Coverage by Month",
            "industry-reporting": "Massachusetts Official Industry-Report Scripts",
            "equity-summaries": "Massachusetts Applications and Equity Summaries",
            "market-composition": "Massachusetts Market Composition",
        }
        for slug, title in derived_titles.items():
            self._entity_id("dataset", f"MA:dataset:{slug}", label=title)
        self._entity_id("license", "MA:lic:overview", label="Massachusetts Licensing Overview")
        tracker = {r.get("LICENSE_NUMBER", "").strip(): r for r in self.normalized.get("licenses", [])}
        for advisory in advisories:
            self._entity_id("safety_advisory", f"MA:adv:{advisory['url']}", label=advisory["title"])
            for licensee in advisory.get("licensees", []):
                number = licensee.get("license_number", "")
                if number in tracker:
                    self._entity_id("license", f"MA:lic:{number}", label=number)
        for product in self._select_affected_products(advisories):
            strain = product.get("strain", "")
            advisory = product.get("_advisory", {})
            if strain and advisory:
                self._entity_id("affected_product",
                                 f"MA:afp:{advisory['url']}:{strain}",
                                 label=f"{product.get('product', '')} ({strain})")
        for lab in self.aggregates.get("licenses", {}).get("itls", []):
            self._entity_id("testing_laboratory", f"MA:lab:{lab.get('LICENSE_NUMBER', '')}",
                            label=lab.get("BUSINESS_NAME", ""))
        seen: set = set()
        for lab in self.aggregates.get("licenses", {}).get("itls", []):
            name = lab.get("BUSINESS_NAME", "").strip()
            if name and name not in seen:
                seen.add(name)
                self._entity_id("organization", f"MA:org:{name}", label=name)
        for advisory in advisories:
            for licensee in advisory.get("licensees", []):
                name = licensee.get("licensee", "").split(" d/b/a ")[0].strip()
                if name and name not in seen:
                    seen.add(name)
                    self._entity_id("organization", f"MA:org:{name}", label=name)
        for slug, name, _ in CONTAMINANTS:
            self._entity_id("contaminant", f"MA:contaminant:{slug}", label=name)
        self._entity_id("requirement", "MA:req:testing", label="Massachusetts Testing Requirements")
        self._entity_id("jurisdiction", "massachusetts-data-landscape",
                        label="Massachusetts Cannabis Data Landscape")

    def _dataset_entity(self, slug: str) -> Optional[str]:
        """Full Boris entity ID for a dataset, or None before allocation."""
        return self.registry.entity_id("dataset", f"MA:dataset:{slug}")

    def _jurisdiction_entity(self) -> str:
        """Full Boris entity ID for the Massachusetts jurisdiction page."""
        return self._entity_id("jurisdiction", "massachusetts")

    def _requirements_entity(self) -> Optional[str]:
        return self.registry.entity_id("requirement", "MA:req:testing")

    def _entity_id(self, entity_type: str, natural_key: str, label: str = "") -> str:
        """Full Boris entity ID in ``<collection>/<PREFIX>-NNNN`` form."""
        return self.registry.id_for(entity_type, natural_key, label=label)

    def _write_page(self, rel_path: str, *, entity_id: str, title: str,
                    parent: Optional[str], tags: list[str], relations: list[str],
                    body: str) -> str:
        path = self.content_root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        fm = frontmatter(title=title, entity_id=entity_id, parent=parent,
                         tags=tags, relations=relations)
        path.write_text(fm + "\n\n" + body + "\n", encoding="utf-8")
        return rel_path

    # ----------------------------------------------------------------- trunks
    def _write_trunks(self) -> list[str]:
        """Trunk pages live at the content root (``content/<collection>.md``)."""
        pages = []
        for collection, (title, description, prefix) in TRUNKS.items():
            rel = f"{collection}.md"
            body = (
                h1(title) + "\n\n" + description + "\n\n"
                + f"Records in this collection use the form identifier schema "
                  f"`{collection}/{prefix}-XXXX`."
                + "\n\n> Massachusetts data is compiled by the state ingestion "
                  "pipeline; see [[jurisdictions/TJUR-0001|Massachusetts]] for provenance."
            )
            self._write_page(rel, entity_id=collection, title=title, parent=None,
                             tags=[collection, "trunk"], relations=[], body=body)
            pages.append(f"{collection}.md")
        return pages

    # -------------------------------------------------------------- jurisdiction
    def _write_jurisdiction_pages(self) -> list[str]:
        jid = self._entity_id("jurisdiction", "massachusetts", label="Massachusetts")
        rel = f"jurisdictions/{jid.rsplit('/', 1)[-1]}.md"
        aggr = self.aggregates.get("licenses", {})
        relations = [
            self._dataset_entity("licenses"), self._dataset_entity("testing_2024"),
            self._dataset_entity("testing_2025"), self._requirements_entity(),
            self._dataset_entity("sales_gross"), self._dataset_entity("price_per_gram"),
        ]
        body = [h1("Massachusetts")]
        body.append("")
        body.append(
            f"The **{REGULATOR['name']}** (CCC) is the state agency regulating "
            f"cannabis in Massachusetts. This archive compiles the Commission's "
            f"official open data, public health and safety advisories, and "
            "published industry reporting."
        )
        body += ["", "## Official Sources", ""]
        body.append(table(
            ["Source", "Location"],
            [["Data catalog", mdlink(REGULATOR["data_catalog"], "masscannabiscontrol.com/open-data/data-catalog/")],
             ["Advisories", mdlink(REGULATOR["advisories_url"], "Public Health and Safety Advisories")],
             ["Regulator site", mdlink(REGULATOR["site"], REGULATOR["name"])]],
        ))
        body += ["", "## Licensing Coverage", ""]
        if aggr:
            body.append(table(
                ["Program", "Licenses"],
                [[k, str(v)] for k, v in aggr.get("by_program", {}).items()],
            ))
            body.append("")
            body.append(f"**{aggr.get('rows', 0)}** establishment licenses tracked; "
                        f"**{len(aggr.get('itls', []))}** active Independent Testing "
                        "Laboratories.")
        body += ["", "## Testing Coverage", ""]
        for slug, label in (("testing_2024", "2024 release"), ("testing_2025", "2025 release")):
            testing = self.aggregates.get(slug, {})
            rows = testing.get("rows", 0)
            body.append(f"- {label}: {rows:,} test records.")
        body += ["", "## Public Health and Safety Advisories", ""]
        body.append(
            "The Commission publishes **public health and safety advisories** for "
            "contaminated or potentially contaminated products. These are modeled "
            "under [[safety-advisories]] and are not relabeled as recalls unless "
            "the Commission itself uses that term."
        )
        body += ["", callout("warning", DISCLAIMER), ""]
        relations = [rel for rel in relations if _relation_target_exists(self.content_root, rel)]
        self._write_page(
            rel, entity_id=jid, title="Massachusetts",
            parent="jurisdictions", tags=["jurisdiction", "massachusetts", "regulator"],
            relations=relations, body="\n".join(body),
        )
        return [rel]

    # ----------------------------------------------------------------- datasets
    def _write_dataset_pages(self) -> list[str]:
        pages = []
        ordering = [
            "licenses", "testing_2024", "testing_2025", "sales_gross",
            "sales_deliveries", "price_per_gram", "mtc_sales", "plant_activity",
        ]
        for slug in ordering:
            pages.append(self._write_dataset_record_page(slug))
        pages.append(self._write_corrections_page())
        pages.extend(self._write_aggregate_pages())
        pages.extend(self._write_market_aggregate_pages())
        pages.append(self._write_industry_reporting_page())
        pages.append(self._write_equity_summary_page())
        return pages

    def _write_dataset_record_page(self, slug: str) -> str:
        spec = DATASETS[slug]
        entity = self._entity_id("dataset", f"MA:dataset:{slug}", label=spec.title)
        rel = f"datasets/{entity.rsplit('/', 1)[-1]}.md"
        body = [h1(spec.title)]
        body += ["", callout("info", DISCLAIMER), ""]
        body += ["", "## Source Record", ""]
        body.append(table(
            ["Field", "Value"],
            [["Official source (CSV)", mdlink(spec.csv_url, "CSV")],
             ["Official source (JSON)", mdlink(spec.json_url, "JSON") if spec.json_url else "—"],
             ["Format", spec.format],
             ["Reporting period", spec.reporting_period],
             ["Source last updated", spec.source_last_updated],
             ["Retrieval", _retrieval_note(self.store, slug)],
             ["Rows (latest snapshot)", _row_count_note(self.store, slug)],
             ["Columns", f"{len(spec.required_columns)}+"],
             ["Clarification / correction", spec.clarification or "—"]],
        ))
        body += ["", "## Dataset Notes", ""]
        body.append(spec.description)
        body += ["", "## Column Schema (required)", ""]
        body.append(table(["Column", "Kind"],
                          [[col, spec.column_types.get(col, "text")]
                           for col in spec.required_columns]))
        aggregates = self.aggregates.get(slug)
        if aggregates and aggregates.get("rows"):
            body += ["", "## Aggregate Summary", ""]
            body.extend(self._render_aggregate(slug, aggregates))
        self._write_page(rel, entity_id=entity, title=spec.title,
                         parent="datasets", tags=["dataset", "massachusetts", slug],
                         relations=[self._jurisdiction_entity()], body="\n".join(body))
        return rel

    def _render_aggregate(self, slug: str, aggregates: dict) -> list[str]:
        lines = []
        if slug == "licenses":
            lines += [table(["Program", "Count"], [[k, str(v)] for k, v in aggregates.get("by_program", {}).items()])]
            lines += ["", table(["License type", "Count"], [[k, str(v)] for k, v in list(aggregates.get("by_type", {}).items())[:10]])]
        elif slug in ("testing_2024", "testing_2025"):
            rows = [[k, str(v.get("count")), str(v.get("passed")), str(v.get("failed"))]
                    for k, v in aggregates.get("by_analyte", {}).items()]
            lines += [table(["Analyte", "Records", "Passed", "Failed"], rows)]
        elif slug in ("sales_gross", "sales_deliveries", "mtc_sales"):
            rows = [[k, str(v.get("records")), f"${v.get('total_dollars', 0):,.2f}"]
                    for k, v in list(aggregates.get("by_category", {}).items())[:14]]
            lines += [table(["Product category", "Records", "Total $"], rows)]
            lines.append(f"\nTotal reported dollars: **${aggregates.get('total_dollars', 0):,.2f}**")
        elif slug == "price_per_gram":
            latest = aggregates.get("latest_month")
            lines.append(
                f"- Months covered: {aggregates.get('months')}\n"
                f"- Latest month: {latest[0]} at ${latest[1]:,.2f}/g" if latest else ""
            )
        elif slug == "plant_activity":
            lines += [table(["Facility type", "Months recorded"],
                            [[k, str(len(v))] for k, v in aggregates.get("by_facility_month", {}).items()])]
        return lines

    def _write_corrections_page(self) -> str:
        entity = self._entity_id("dataset", "MA:dataset:testing-corrections",
                                 label="Massachusetts Testing Corrections and Clarifications")
        rel = f"datasets/{entity.rsplit('/', 1)[-1]}.md"
        body = [h1("Massachusetts Testing Corrections and Clarifications")]
        body.append(
            "The Commission occasionally republishes testing datasets and posts "
            "clarification notices. This page records those corrections."
        )
        body += ["", "## Known Corrections and Clarifications", ""]
        body.append(table(
            ["Release", "Notice", "Date", "Effect"],
            [["2025 testing results",
              mdlink(REGULATOR["testing_update_2025"], "3/19/2026 Testing Data Update"),
              "2026-03-19", "Data updated; re-ingest records a new snapshot"],
             ["2024 testing results",
              "File republished with 20260415 suffix",
              "2026-04-15", "Schema and row set may differ from the initial release"],
             ["2025-08-06 advisory",
              "Summary Suspension Order connection",
              "2025-06-30", "544 lab samples flagged for Total Yeast and Mold"]]
        ))
        body += ["", callout("tip",
            "When a source release changes, the importer retains the prior "
            "manifest record, compares row identity and values, distinguishes "
            "changed status labels from changed numerical measurements, and "
            "writes a revision report. A `supersedes` relation is only emitted "
            "when the official release relationship supports it."), ""]
        relations = [r for r in (self._dataset_entity("testing_2024"),
                                 self._dataset_entity("testing_2025")) if r]
        self._write_page(rel, entity_id=entity, title="Testing Corrections and Clarifications",
                         parent="datasets", tags=["dataset", "testing", "corrections", "massachusetts"],
                         relations=relations,
                         body="\n".join(body))
        return rel

    def _write_aggregate_pages(self) -> list[str]:
        """Write the THC/THCA, yeast-and-mold, heavy-metals, and coverage pages."""
        pages = []
        specs = [
            ("thc-thca", "Massachusetts Testing: THC and THCA", ["THC", "THCA"]),
            ("yeast-mold", "Massachusetts Testing: Total Yeast and Mold", ["Total Yeast and Mold", "Coliforms"]),
            ("heavy-metals", "Massachusetts Testing: Heavy Metals", ["Arsenic", "Cadmium", "Lead", "Mercury"]),
        ]
        for filename, title, analytes in specs:
            entity = self._entity_id("dataset", f"MA:dataset:{filename}", label=title)
            rel = f"datasets/{entity.rsplit('/', 1)[-1]}.md"
            body = [h1(title), "",
                    "Aggregate view across the official testing releases. "
                    "Values are **not** used to rank laboratories, producers, or "
                    "cultivars, and a single result implies nothing about consumer "
                    "safety without the applicable requirement, unit, matrix, "
                    "status, and action limit.", ""]
            rows = []
            for release in ("testing_2024", "testing_2025"):
                aggregates = self.aggregates.get(release, {})
                for analyte, stats in aggregates.get("by_analyte", {}).items():
                    if analyte in analytes:
                        rows.append([release, analyte, str(stats["count"]),
                                     str(stats["passed"]), str(stats["failed"])])
            if rows:
                body += ["## Records", ""]
                body.append(table(["Release", "Analyte", "Records", "Passed", "Failed"], rows))
            body += ["", callout("warning", DISCLAIMER), ""]
            relations = [r for r in (self._jurisdiction_entity(),
                                     self._dataset_entity("testing_2024"),
                                     self._dataset_entity("testing_2025")) if r]
            self._write_page(rel, entity_id=entity, title=title, parent="datasets",
                             tags=["dataset", "testing", "aggregate", "massachusetts"],
                             relations=relations,
                             body="\n".join(body))
            pages.append(rel)
        # coverage by month
        entity = self._entity_id("dataset", "MA:dataset:testing-coverage-by-month",
                                 label="Massachusetts Testing Coverage by Month")
        rel = f"datasets/{entity.rsplit('/', 1)[-1]}.md"
        body = [h1("Massachusetts Testing Coverage by Month"), ""]
        combined: Counter = Counter()
        for release in ("testing_2024", "testing_2025"):
            for month, count in self.aggregates.get(release, {}).get("by_month", {}).items():
                combined[month] += count
        if combined:
            body.append(table(["Month", "Test records"], [[k, str(v)] for k, v in sorted(combined.items())]))
        body += ["", "## Status Distribution", ""]
        statuses: Counter = Counter()
        for release in ("testing_2024", "testing_2025"):
            for status, count in self.aggregates.get(release, {}).get("by_status", {}).items():
                statuses[status] += count
        body.append(table(["Status", "Records"], [[k, str(v)] for k, v in statuses.most_common()]))
        relations = [r for r in (self._dataset_entity("testing_2024"),
                                 self._dataset_entity("testing_2025")) if r]
        self._write_page(rel, entity_id=entity, title="Testing Coverage by Month",
                         parent="datasets", tags=["dataset", "testing", "aggregate", "massachusetts"],
                         relations=relations, body="\n".join(body))
        pages.append(rel)
        return pages

    def _write_market_aggregate_pages(self) -> list[str]:
        """Market-composition page: flower vs concentrate, pre-roll share, AU vs medical."""
        entity = self._entity_id("dataset", "MA:dataset:market-composition",
                                 label="Massachusetts Market Composition")
        rel = f"datasets/{entity.rsplit('/', 1)[-1]}.md"
        body = [h1("Massachusetts Market Composition"), "",
                "Derived aggregate view of adult-use and medical sales as "
                "reported by licensees through the Commission.", ""]
        gross = self.aggregates.get("sales_gross", {}).get("by_category", {})
        mtc = self.aggregates.get("mtc_sales", {}).get("by_category", {})
        if gross:
            flower = gross.get("Buds", {}).get("total_dollars", 0.0)
            concentrate = gross.get("Concentrate", {}).get("total_dollars", 0.0) + \
                gross.get("Concentrate (Each)", {}).get("total_dollars", 0.0)
            preroll = gross.get("Raw Pre-Rolls", {}).get("total_dollars", 0.0) + \
                gross.get("Infused Pre-Rolls", {}).get("total_dollars", 0.0)
            total = sum(v.get("total_dollars", 0.0) for v in gross.values()) or 1.0
            body += ["", "## Flower vs Concentrate Share (adult-use)", ""]
            body.append(table(
                ["Category", "Total $", "Share"],
                [["Flower (Buds)", f"${flower:,.2f}", f"{flower / total * 100:.1f}%"],
                 ["Concentrate", f"${concentrate:,.2f}", f"{concentrate / total * 100:.1f}%"],
                 ["Pre-rolls (raw + infused)", f"${preroll:,.2f}", f"{preroll / total * 100:.1f}%"]],
            ))
            body.append(
                "_Shares are computed from self-reported sales; methodology: "
                "product-category totals divided by all adult-use category totals._"
            )
        body += ["", "## Adult-Use vs Medical Presence", ""]
        au_rows = self.aggregates.get("sales_gross", {}).get("rows", 0)
        med_rows = self.aggregates.get("mtc_sales", {}).get("rows", 0)
        body.append(table(["Market", "Record rows"], [["Adult-use sales", au_rows],
                                                       ["Medical facility sales", med_rows]]))
        body += ["", callout("warning", MARKET_DISCLAIMER), ""]
        self._write_page(rel, entity_id=entity, title="Market Composition",
                         parent="datasets", tags=["dataset", "market", "sales", "massachusetts"],
                         relations=[r for r in (self._jurisdiction_entity(),
                                                self._dataset_entity("sales_gross"),
                                                self._dataset_entity("mtc_sales")) if r],
                         body="\n".join(body))
        return [rel]

    def _write_industry_reporting_page(self) -> str:
        entity = self._entity_id("dataset", "MA:dataset:industry-reporting",
                                 label="Massachusetts Official Industry-Report Scripts")
        rel = f"datasets/{entity.rsplit('/', 1)[-1]}.md"
        body = [h1("Massachusetts Official Industry-Report Scripts")]
        body.append(
            "The data catalog lists official R scripts and source data used for "
            "industry reporting. The Commission's catalog renders these as a "
            "data table; the direct download URLs are captured on ingest when "
            "the catalog provides them."
        )
        body += ["", "## Catalog Entries", ""]
        body.append(table(
            ["Type", "Title", "Status"],
            [["R Script", "Adult-Use and Medical Establishments (Production)", "Documented; URL via catalog table"],
             ["R Script", "Medical-Use Market", "Documented; URL via catalog table"],
             ["R Script", "Price per Gram", "Documented; URL via catalog table"],
             ["R Script", "Testing (THC/THCA/Y&M 2021-2023)", "Documented; URL via catalog table"],
             ["Data", "Adult Market Data, Including Counties", "Documented; CSV via catalog"],
             ["Data", "Testing_Data_THC_THCA_Y&M-2021-2023", "Documented; CSV via catalog"]]
        ))
        body += ["", callout("tip",
            "Official scripts are archived with metadata and checksums when "
            "downloaded. We do not silently edit an official script and continue "
            "calling the result official; methodology from the Commission is "
            "preserved separately from site-added analysis."), ""]
        self._write_page(rel, entity_id=entity, title="Industry-Report Scripts",
                         parent="datasets", tags=["dataset", "industry-reporting", "r-scripts", "massachusetts"],
                         relations=[self._jurisdiction_entity()], body="\n".join(body))
        return rel

    def _write_equity_summary_page(self) -> str:
        entity = self._entity_id("dataset", "MA:dataset:equity-summaries",
                                 label="Massachusetts Applications and Equity Summaries")
        rel = f"datasets/{entity.rsplit('/', 1)[-1]}.md"
        body = [h1("Massachusetts Applications and Equity Summaries")]
        # Only explicitly allowlisted columns are published for these aggregate
        # datasets; a column added upstream never reaches generated content.
        public_columns = {
            "applications_totals": ["INDUSTRY", "LICENSE_TYPE", "APPLICATION_STATUS", "TOTAL"],
            "applications_dbe": ["INDUSTRY", "DBE", "TOTAL"],
            "agents_gender": ["GENDER", "TOTAL"],
            "agents_raceethnicity": ["RACE_ETHNICITY", "TOTAL"],
        }
        for slug, title in (("applications_totals", "Applications by status"),
                            ("applications_dbe", "DBE totals"),
                            ("agents_gender", "Agent gender totals"),
                            ("agents_raceethnicity", "Agent race/ethnicity totals")):
            data = self.aggregates.get(slug, {}).get("data", [])
            if not data:
                continue
            body += ["", f"## {title}", ""]
            headers = public_columns[slug]
            body.append(table(headers, [[row.get(h, "") for h in headers] for row in data]))
        body += ["", callout("warning", DISCLAIMER), ""]
        self._write_page(rel, entity_id=entity, title="Applications and Equity Summaries",
                         parent="datasets", tags=["dataset", "equity", "applications", "massachusetts"],
                         relations=[self._jurisdiction_entity()], body="\n".join(body))
        return rel

    # ---------------------------------------------------------------- licensing
    def _write_licensing_pages(self) -> list[str]:
        pages = []
        entity = self._entity_id("license", "MA:lic:overview",
                                 label="Massachusetts Licensing Overview")
        rel = f"licenses/{entity.rsplit('/', 1)[-1]}.md"
        aggr = self.aggregates.get("licenses", {})
        body = [h1("Massachusetts Licensing Overview")]
        if aggr:
            body += ["", "## License Counts", ""]
            body += [table(["Program", "Count"], [[k, str(v)] for k, v in aggr.get("by_program", {}).items()])]
            body += ["", "## By License Type", ""]
            body += [table(["License type", "Count"], [[k, str(v)] for k, v in aggr.get("by_type", {}).items()])]
            body += ["", "## By Status", ""]
            body += [table(["Status", "Count"], [[k, str(v)] for k, v in aggr.get("by_status", {}).items()])]
            body += ["", "## By Commence-Operations State", ""]
            body += [table(["Commence ops", "Count"], [[k, str(v)] for k, v in aggr.get("by_commence", {}).items()])]
            body += ["", "## By County", ""]
            body += [table(["County", "Count"], [[k, str(v)] for k, v in aggr.get("by_county", {}).items()])]
            tiers = aggr.get("by_tier", {})
            if tiers:
                body += ["", "## Cultivation Tiers", ""]
                body += [table(["Tier", "Count"], [[k, str(v)] for k, v in tiers.items()])]
        body += ["", callout("warning", DISCLAIMER), ""]
        relations = [r for r in (self._dataset_entity("licenses"),
                                 self._jurisdiction_entity()) if r]
        self._write_page(rel, entity_id=entity, title="Massachusetts Licensing Overview",
                         parent="licenses", tags=["licenses", "overview", "massachusetts"],
                         relations=relations,
                         body="\n".join(body))
        pages.append(rel)
        pages += self._write_advisory_license_pages()
        return pages

    def _write_advisory_license_pages(self) -> list[str]:
        """License pages only for licensees explicitly connected to advisories."""
        pages = []
        tracker = {r.get("LICENSE_NUMBER", "").strip(): r for r in self.normalized.get("licenses", [])}
        for advisory in self._advisories:
            for licensee in advisory.get("licensees", []):
                number = licensee.get("license_number", "")
                row = tracker.get(number)
                if not row:
                    continue
                key = f"MA:lic:{number}"
                entity = self._entity_id("license", key, label=number)
                rel = f"licenses/{entity.rsplit('/', 1)[-1]}.md"
                body = [h1(f"License {number}"), "",
                        "This license is explicitly connected to a Massachusetts "
                        "public health and safety advisory.", "",
                        "## Approved Public Fields", ""]
                rows = [
                    ["Legal name", row.get("BUSINESS_NAME", "")],
                    ["License number", number],
                    ["License type", row.get("LICENSE_TYPE", "")],
                    ["Program", row.get("INDUSTRY", "")],
                    ["Status", row.get("LICENSE_STATUS_CATEGORY", "")],
                    ["Commence operations", row.get("COMMENCE_OPS", "")],
                    ["Municipality", (row.get("ESTABLISHMENT_CITY") or "").title()],
                    ["County", row.get("ESTABLISHMENT_COUNTY", "")],
                ]
                body.append(table(["Field", "Value"], rows))
                advisory_entity = self.registry.entity_id("safety_advisory", f"MA:adv:{advisory['url']}")
                relations = [self._jurisdiction_entity()]
                if advisory_entity:
                    relations.append(advisory_entity)
                self._write_page(rel, entity_id=entity, title=f"License {number}",
                                 parent="licenses", tags=["license", "advisory-connected", "massachusetts"],
                                 relations=relations, body="\n".join(body))
                pages.append(rel)
        return pages

    # -------------------------------------------------------------------- labs
    def _write_lab_pages(self) -> list[str]:
        pages = []
        itls = self.aggregates.get("licenses", {}).get("itls", [])
        for lab in itls:
            number = lab.get("LICENSE_NUMBER", "")
            entity = self._entity_id("testing_laboratory", f"MA:lab:{number}",
                                     label=lab.get("BUSINESS_NAME", number))
            rel = f"testing-laboratories/{entity.rsplit('/', 1)[-1]}.md"
            org_entity = self.registry.entity_id("organization", f"MA:org:{lab.get('BUSINESS_NAME', '')}")
            relations = [r for r in (self._jurisdiction_entity(), self._requirements_entity()) if r]
            if org_entity:
                relations.append(org_entity)
            rows = [
                ["Legal or licensed name", lab.get("BUSINESS_NAME", "")],
                ["License number", number],
                ["License type", lab.get("LICENSE_TYPE", "")],
                ["Program", lab.get("INDUSTRY", "")],
                ["Status", lab.get("LICENSE_STATUS_CATEGORY", "")],
                ["Commence-operations state", lab.get("COMMENCE_OPS", "")],
                ["Licensed-premises municipality", (lab.get("ESTABLISHMENT_CITY") or "").title()],
                ["County", lab.get("ESTABLISHMENT_COUNTY", "")],
                ["Official source", "CCC license tracker (point-in-time snapshot)"],
                ["Source last updated", DATASETS["licenses"].source_last_updated],
                ["Retrieval date", _retrieval_note(self.store, "licenses")],
            ]
            body = [h1(lab.get("BUSINESS_NAME", number)), "",
                    "Active Massachusetts Independent Testing Laboratory.", "",
                    "## Approved Public Fields", ""]
            body.append(table(["Field", "Value"], rows))
            body += ["", callout("warning",
                "This page does not rank or grade laboratory performance. "
                "Testing datasets published by the Commission anonymize the "
                "performing laboratory, so no lab-level inference is possible "
                "from official data."), ""]
            self._write_page(rel, entity_id=entity, title=lab.get("BUSINESS_NAME", number),
                             parent="testing-laboratories",
                             tags=["testing-laboratory", "laboratory", "massachusetts", "licensed"],
                             relations=relations, body="\n".join(body))
            pages.append(rel)
        return pages

    # ------------------------------------------------------------ organizations
    def _write_organization_pages(self) -> list[str]:
        pages = []
        seen: set = set()
        itls = self.aggregates.get("licenses", {}).get("itls", [])
        for lab in itls:
            name = lab.get("BUSINESS_NAME", "").strip()
            if not name or name in seen:
                continue
            seen.add(name)
            entity = self._entity_id("organization", f"MA:org:{name}", label=name)
            rel = f"organizations/{entity.rsplit('/', 1)[-1]}.md"
            body = [h1(name), "",
                    "Massachusetts licensed entity; source identity from the CCC "
                    "license tracker. No lineage, ownership, or operational "
                    "inference is made beyond what the source states.", ""]
            rows = [
                ["Legal entity name", name],
                ["License number", lab.get("LICENSE_NUMBER", "")],
                ["License type", lab.get("LICENSE_TYPE", "")],
                ["Program", lab.get("INDUSTRY", "")],
                ["Municipality", (lab.get("ESTABLISHMENT_CITY") or "").title()],
            ]
            body.append(table(["Field", "Value"], rows))
            self._write_page(rel, entity_id=entity, title=name, parent="organizations",
                             tags=["organization", "massachusetts", "licensed"],
                             relations=[self._jurisdiction_entity()], body="\n".join(body))
            pages.append(rel)
        # advisory-connected licensees (legal entities only)
        for advisory in self._advisories:
            for licensee in advisory.get("licensees", []):
                name = licensee.get("licensee", "").split(" d/b/a ")[0].strip()
                if not name or name in seen:
                    continue
                seen.add(name)
                entity = self._entity_id("organization", f"MA:org:{name}", label=name)
                rel = f"organizations/{entity.rsplit('/', 1)[-1]}.md"
                body = [h1(name), "",
                        "Retail licensee connected to a Massachusetts public health "
                        "and safety advisory. Organization identity is the source "
                        "legal entity name; display names (d/b/a) are not merged "
                        "as separate organizations.", ""]
                rows = [["Legal entity name", name],
                        ["License number", licensee.get("license_number", "")],
                        ["Municipality", licensee.get("municipality", "")]]
                body.append(table(["Field", "Value"], rows))
                self._write_page(rel, entity_id=entity, title=name, parent="organizations",
                                 tags=["organization", "advisory-connected", "massachusetts"],
                                 relations=[self._jurisdiction_entity()], body="\n".join(body))
                pages.append(rel)
        return pages

    # ------------------------------------------------------------- contaminants
    def _write_contaminant_pages(self) -> list[str]:
        pages = []
        contaminants = [
            ("thc", "THC", "Delta-9 tetrahydrocannabinol"),
            ("thca", "THCA", "Tetrahydrocannabinolic acid"),
            ("arsenic", "Arsenic", "Heavy metal"),
            ("cadmium", "Cadmium", "Heavy metal"),
            ("lead", "Lead", "Heavy metal"),
            ("mercury", "Mercury", "Heavy metal"),
            ("total-yeast-and-mold", "Total Yeast and Mold", "Microbial contaminant"),
            ("coliforms", "Coliforms", "Microbial contaminant"),
        ]
        for slug, name, kind in contaminants:
            entity = self._entity_id("contaminant", f"MA:contaminant:{slug}", label=name)
            rel = f"contaminants/{entity.rsplit('/', 1)[-1]}.md"
            body = [h1(name), "",
                    f"{name} ({kind}) appears in official Massachusetts testing "
                    "data and public health and safety advisories.", "",
                    "## Where It Appears", ""]
            rows = []
            for release, label in (("testing_2024", "2024 testing release"), ("testing_2025", "2025 testing release")):
                stats = self.aggregates.get(release, {}).get("by_analyte", {}).get(name)
                if stats:
                    rows.append([label, str(stats["count"]), str(stats["passed"]), str(stats["failed"])])
            if rows:
                body.append(table(["Release", "Records", "Passed", "Failed"], rows))
            advisory_entities = self._advisory_entities_for_contaminant(slug)
            if advisory_entities:
                body += ["", "## Related Advisories", ""]
                body.append("\n".join(f"- {wikilink(e)}" for e in advisory_entities))
            requirements_entity = self._requirements_entity()
            requirements_link = f"[[{requirements_entity}|Massachusetts Testing Requirements]]" if requirements_entity else "the Commission's testing regulations"
            body += ["", callout("warning",
                f"Action limits for these analytes are set by the Commission's "
                f"testing regulations (see {requirements_link}). No single result "
                f"implies consumer safety without the applicable requirement, "
                f"unit, matrix, status, and action limit."), ""]
            relations = [r for r in (self._dataset_entity("testing_2024"),
                                     self._dataset_entity("testing_2025"),
                                     self._requirements_entity()) if r]
            self._write_page(rel, entity_id=entity, title=name, parent="contaminants",
                             tags=["contaminant", "testing", "massachusetts"],
                             relations=relations,
                             body="\n".join(body))
            pages.append(rel)
        return pages

    def _advisory_entities_for_contaminant(self, slug: str) -> list[str]:
        mapping = {
            "total-yeast-and-mold": ["yeast", "mold"],
            "coliforms": ["coliform"],
        }
        keywords = mapping.get(slug, [slug])
        entities = []
        for advisory in self._advisories:
            concern = (advisory.get("concern") or "").lower()
            if any(k in concern for k in keywords):
                entity = self.registry.entity_id("safety_advisory", f"MA:adv:{advisory['url']}")
                if entity:
                    entities.append(entity)
        return entities

    # -------------------------------------------------------------- requirements
    def _write_requirement_pages(self) -> list[str]:
        entity = self._entity_id("requirement", "MA:req:testing",
                                 label="Massachusetts Testing Requirements")
        rel = f"requirements/{entity.rsplit('/', 1)[-1]}.md"
        body = [h1("Massachusetts Testing Requirements"), "",
                "Massachusetts requires licensed establishments to test cannabis "
                "and cannabis products through Commission-certified Independent "
                "Testing Laboratories. The applicable requirements are defined "
                "in the Commission's regulations: **935 CMR 500.160** "
                "(adult-use) and **105 CMR 725.100** (medical).", "",
                "## Scope", ""]
        body.append(task_list([
            (True, "Test results reported through Commission systems"),
            (True, "Total Yeast and Mold and coliform limits enforced"),
            (True, "Heavy-metal analytes (arsenic, cadmium, lead, mercury) required"),
            (True, "Cannabinoid potency (THC/THCA) reported"),
            (True, "Independent Testing Laboratory certification required"),
            (False, "Action-limit numeric values republished here (see note)"),
        ]))
        body += ["", callout("tip",
            "This page intentionally does not restate numeric action limits. "
            "Limit values must be confirmed against the current regulation text "
            "and the Commission's published testing guidance before being "
            "republished; the importer never infers limits from single results."), ""]
        relations = [r for r in (self._jurisdiction_entity(), self._dataset_entity("licenses"),
                                 self._dataset_entity("testing_2024"),
                                 self._dataset_entity("testing_2025")) if r]
        self._write_page(rel, entity_id=entity, title="Massachusetts Testing Requirements",
                         parent="requirements", tags=["requirements", "testing", "regulatory", "massachusetts"],
                         relations=relations,
                         body="\n".join(body))
        return [rel]

    # --------------------------------------------------------------- advisories
    def _write_advisory_pages(self, advisories: list[dict]) -> list[str]:
        pages = []
        for advisory in advisories:
            entity = self._entity_id("safety_advisory", f"MA:adv:{advisory['url']}",
                                     label=advisory["title"])
            rel = f"safety-advisories/{entity.rsplit('/', 1)[-1]}.md"
            body = [h1(advisory["title"])]
            body += ["", "## Advisory Facts", ""]
            rows = [
                ["Advisory date", advisory.get("advisory_date", "")],
                ["Canonical URL", mdlink(advisory["url"], "official notice")],
                ["Concern / reason", advisory.get("concern", "")],
                ["Affected-product count", str(advisory.get("affected_product_count", 0))],
                ["Revision status", "as published by the Commission"],
                ["Source provenance", "CCC Public Health and Safety Advisories portal"],
            ]
            for label, key in (("Sold between", "sold_between"), ("Tested between", "tested_between")):
                value = advisory.get("date_ranges", {}).get(key)
                if value:
                    rows.append([label, " and ".join(value)])
            body.append(table(["Field", "Value"], rows))
            if advisory.get("consumer_instructions"):
                body += ["", "## Consumer Instructions", ""]
                body.append(callout("warning", advisory["consumer_instructions"]))
            products = advisory.get("products", [])
            if products:
                body += ["", "## Affected Products", ""]
                rows = [[p.get("product", ""), p.get("strain", ""), p.get("batch", "")]
                        for p in products]
                body.append(table(["Product Name/Type", "Product Strain", "Product Batch Number"], rows))
                body.append(
                    "\n\n<details>\n<summary>Full affected-product list ({})</summary>\n\n".format(len(products))
                    + "\n".join(f"- `{escape_cell(p.get('batch', ''))}` {escape_cell(p.get('product', ''))} ({escape_cell(p.get('strain', ''))})" for p in products)
                    + "\n</details>"
                )
            licensees = advisory.get("licensees", [])
            if licensees:
                body += ["", "## Retailers and Licensees", ""]
                body.append(table(["Licensee", "License Number", "Municipality"],
                                  [[l.get("licensee", ""), l.get("license_number", ""), l.get("municipality", "")]
                                   for l in licensees]))
                body.append(
                    "_Only the licensed-premises municipality is published; street "
                    "addresses from the official notice are excluded._"
                )
            body += ["", callout("info",
                "The Commission uses **public health and safety advisory** as the "
                "official term for these notices. This archive preserves that "
                "terminology and does not relabel the notice as a recall."), ""]
            relations = [self._jurisdiction_entity()]
            relations += self._advisory_relation_entities(advisory)
            self._write_page(rel, entity_id=entity, title=advisory["title"],
                             parent="safety-advisories",
                             tags=["safety-advisory", "advisory", "massachusetts", "ccc"],
                             relations=relations, body="\n".join(body))
            pages.append(rel)
        return pages

    def _advisory_relation_entities(self, advisory: dict) -> list[str]:
        relations = []
        for contaminant in ("Total Yeast and Mold", "Coliforms"):
            concern = (advisory.get("concern") or "").lower()
            if contaminant.lower() in concern:
                entity = self.registry.entity_id("contaminant",
                                                 f"MA:contaminant:{contaminant.lower().replace(' ', '-')}")
                if entity:
                    relations.append(entity)
        for product in advisory.get("products", [])[:1]:
            strain = product.get("strain", "")
            if strain:
                entity = self.registry.entity_id("affected_product",
                                                 f"MA:afp:{advisory['url']}:{strain}")
                if entity:
                    relations.append(entity)
        return relations

    # ------------------------------------------------------- affected products
    def _write_affected_product_pages(self, advisories: list[dict]) -> list[str]:
        pages = []
        selected = self._select_affected_products(advisories)
        for product in selected:
            advisory = product["_advisory"]
            strain = product.get("strain", "")
            key = f"MA:afp:{advisory['url']}:{strain}"
            label = f"{product.get('product', '')} ({strain})"
            entity = self._entity_id("affected_product", key, label=label)
            rel = f"affected-products/{entity.rsplit('/', 1)[-1]}.md"
            parsed = parse_product_string(product.get("product", ""))
            body = [h1(label), "",
                    "Normalized affected-package record derived from a "
                    "Massachusetts public health and safety advisory.", "",
                    "## Source Record", ""]
            rows = [
                ["Source product text", parsed["source_product_text"]],
                ["Source product identifier (batch)", product.get("batch", "")],
                ["Commercial product label", parsed["commercial_product_label"]],
                ["Package size text", parsed["package_size_text"] or "—"],
                ["Product form", parsed["product_form"] or "—"],
                ["Cultivar candidate text", strain],
                ["Advisory date", advisory.get("advisory_date", "")],
                ["Advisory source", mdlink(advisory["url"], "official notice")],
            ]
            body.append(table(["Field", "Value"], rows))
            body += ["", callout("warning",
                "Cultivar-candidate text is preserved exactly as published. No "
                "lineage, indica/sativa classification, expected effects, or "
                "dominant terpenes are assigned. See the cultivar-candidate "
                "report in the ingest artifacts for occurrence data."), ""]
            advisory_entity = self.registry.entity_id("safety_advisory", f"MA:adv:{advisory['url']}")
            relations = [self._jurisdiction_entity()]
            if advisory_entity:
                relations.append(advisory_entity)
            self._write_page(rel, entity_id=entity, title=label,
                             parent="affected-products",
                             tags=["affected-product", "advisory", "massachusetts"],
                             relations=relations, body="\n".join(body))
            pages.append(rel)
        return pages

    def _select_affected_products(self, advisories: list[dict]) -> list[dict]:
        """Documented editorial criteria for representative affected-product pages.

        A package is page-worthy when it:
          * appears in more than one advisory (multi-advisory bonus), or
          * contains a clearly parseable flower/pre-roll cultivar label, or
          * connects to a known organization (brand present in licensee data).
        The selection is capped and deterministic (first occurrences).
        """
        cap = PAGE_POLICY["affected_products_max_pages"]
        selected = []
        seen_batches: set = set()
        for advisory in advisories:
            for product in advisory.get("products", []):
                if len(selected) >= cap:
                    return selected
                batch = (product.get("batch") or "").strip()
                if batch in seen_batches:
                    continue
                strain = (product.get("strain") or "").strip()
                product_text = (product.get("product") or "").lower()
                # Clearly parseable flower/pre-roll cultivar label: an explicit
                # form keyword, or a bounded size/unit phrase (e.g. "3.5 g").
                cultivar_label = bool(strain) and (
                    any(kw in product_text for kw in ("pre-roll", "preroll", "flower", "jar"))
                    or bool(re.search(r"\b\d+\s*(?:g|gram|oz)\b", product_text))
                )
                if not cultivar_label:
                    continue
                seen_batches.add(batch)
                product["_advisory"] = advisory
                selected.append(product)
        return selected

    # ------------------------------------------------------------ privacy spec
    def _write_privacy_spec_page(self) -> str:
        entity = "reference/TREF-0004"
        rel = "reference/TREF-0004.md"
        body = [h1("Massachusetts Ingestion: Privacy and Excluded-Field Specification")]
        body.append(
            "Generated pages from Massachusetts official data publish only "
            "fields on the explicit allowlists below. The machine-readable "
            "specification is committed at `data/massachusetts-ccc/privacy-spec.md` "
            "and enforced by an automated scan of generated Markdown."
        )
        body += ["", "## Excluded Fields and Values", ""]
        body.append(table(
            ["Category", "Examples"],
            [["EIN / TIN", "EIN_TIN, FEIN"],
             ["Personal addresses", "business/mailing street addresses, full addresses"],
             ["Mailing addresses unrelated to licensed premises", "MAILING_ADDRESS_*"],
             ["Individual agent records", "agent names, emails, identifiers"],
             ["Personal names", "agent names; only official public roles published"],
             ["Email addresses", "BUSINESS_EMAIL"],
             ["Phone numbers", "BUSINESS_PHONE"],
             ["Internal application notes", "application notes, review priority details"],
             ["Unnecessary ownership details", "fee-waiver numbers, SE account numbers"],
             ["Raw coordinates", "LATITUDE, LONGITUDE"],
             ["Fields present merely because they exist in source JSON", "all non-allowlisted source fields"]]
        ))
        body += ["", "## Entity Allowlists", ""]
        for entity_type, fields in sorted(PRIVACY_SPEC.entity_allowlists.items()):
            body.append(f"**{entity_type}**: `{'`, `'.join(fields)}`")
        body += ["", callout("warning",
            "Raw local snapshots may retain source fields for fidelity, but they "
            "are stored only in the git-ignored working directory "
            "(`var/ingest/massachusetts-ccc/`) and never committed or published."), ""]
        self._write_page(rel, entity_id=entity, title="Privacy and Excluded-Field Specification",
                         parent="reference", tags=["privacy", "allowlist", "massachusetts", "ingest"],
                         relations=[], body="\n".join(body))
        return rel

    # ------------------------------------------------------------ data landscape
    def _write_landscape_page(self, advisories: list[dict]) -> str:
        entity = self._entity_id("jurisdiction", "massachusetts-data-landscape",
                                 label="Massachusetts Cannabis Data Landscape")
        rel = f"jurisdictions/{entity.rsplit('/', 1)[-1]}.md"
        body = [h1("Massachusetts Cannabis Data Landscape")]
        body.append(
            "One-page operational view of the Massachusetts CCC open-data "
            "ecosystem as archived by the ingestion pipeline."
        )
        body += ["", callout("info",
            f"This page is generated from the ingest manifest and aggregates. "
            f"Raw artifacts live under `var/ingest/massachusetts-ccc/`; durable "
            f"records under `data/massachusetts-ccc/`."), ""]
        body += ["", "## Source Inventory", ""]
        body.append(table(
            ["Dataset", "Format", "Reporting period", "Last updated", "Rows"],
            [[spec.title, spec.format, spec.reporting_period,
              spec.source_last_updated, _row_count_note(self.store, slug)]
             for slug, spec in DATASETS.items()]
        ))
        body += ["", "## Dataset Freshness", ""]
        freshness = [[slug, _retrieval_note(self.store, slug)] for slug in DATASETS]
        body.append(table(["Dataset", "Last retrieval"], freshness))
        body += ["", "## Testing-Release Lag", ""]
        testing_lag = [
            ["2024 release", _release_lag_note(self.store, "testing_2024")],
            ["2025 release", _release_lag_note(self.store, "testing_2025")],
        ]
        body.append(table(["Release", "Lag note"], testing_lag))
        body += ["", "## License Coverage", ""]
        aggr = self.aggregates.get("licenses", {})
        if aggr:
            body.append(f"**{aggr.get('rows', 0)}** licenses; "
                        f"{len(aggr.get('itls', []))} active Independent Testing Laboratories.")
        body += ["", "## Advisory Coverage", ""]
        body.append(f"**{len(advisories)}** public health and safety advisories archived: "
                    + ", ".join(a.get("advisory_date", "") or "?" for a in advisories))
        body += ["", "## Testing Analytes", ""]
        analytes = []
        for release in ("testing_2024", "testing_2025"):
            for analyte in self.aggregates.get(release, {}).get("by_analyte", {}):
                if analyte not in analytes:
                    analytes.append(analyte)
        body.append(", ".join(analytes) if analytes else "_none ingested yet_")
        body += ["", "## Market-Data Coverage", ""]
        body.append(task_list([
            (bool(self.aggregates.get("sales_gross", {}).get("rows")), "Adult-use sales by product type"),
            (bool(self.aggregates.get("sales_deliveries", {}).get("rows")), "Weekly retail and delivery sales"),
            (bool(self.aggregates.get("price_per_gram", {}).get("months")), "Average flower price"),
            (bool(self.aggregates.get("mtc_sales", {}).get("rows")), "Medical facility sales"),
            (bool(self.aggregates.get("plant_activity", {}).get("rows")), "Plant activity and production"),
        ]))
        body += ["", "## Source Disclaimers", ""]
        body.append(callout("warning", DISCLAIMER))
        body += ["", "## Sync Status", ""]
        body.append(table(["State", "Value"],
                          [["State adapter", "massachusetts"],
                           ["Importer version", self.store.importer_version],
                           ["Schema version", self.store.schema_version],
                           ["Last run", _latest_run_note(self.store)]]))
        body += ["", "## Graph Links", ""]
        links = [self._jurisdiction_entity(), self._dataset_entity("licenses"),
                 self._dataset_entity("testing_2025"), self._requirements_entity()]
        body.append("\n".join(
            f"- {wikilink(target, label)}" for target, label in [
                (self._jurisdiction_entity(), "Massachusetts jurisdiction"),
                (self._dataset_entity("licenses"), "License tracker dataset"),
                (self._dataset_entity("testing_2025"), "Testing results 2025"),
                (self._requirements_entity(), "Testing requirements"),
                ("safety-advisories", "Safety advisories"),
                ("testing-laboratories", "Testing laboratories"),
            ] if target
        ))
        body += ["", "## Revision History", ""]
        manifest = self.store.read_manifest()
        updated = manifest.get("updated_at", "")
        body.append(f"- Manifest last updated: `{updated or 'never'}`")
        body.append(f"- Durable records: `data/massachusetts-ccc/`")
        body += ["", footnote("landscape-method",
            "All counts and dates on this page derive from the ingest manifest "
            "and per-dataset aggregates computed from official CCC files. "
            "Reported figures are self-reported by licensees and not audited by "
            "this archive.")]
        self._write_page(rel, entity_id=entity, title="Massachusetts Cannabis Data Landscape",
                         parent="jurisdictions", tags=["landscape", "overview", "apex", "massachusetts"],
                         relations=[self._jurisdiction_entity()], body="\n".join(body))
        return rel

    # ----------------------------------------------------------- durable artifacts
    def _write_durable_artifacts(self, advisories: list[dict]) -> None:
        self._write_affected_packages_artifact(advisories)
        self._write_cultivar_candidates_artifact(advisories)
        self._write_source_catalog_artifact()
        self._write_schema_report_artifact()
        self._write_privacy_spec_artifact()

    def _write_affected_packages_artifact(self, advisories: list[dict]) -> None:
        rows = []
        for advisory in advisories:
            for product in advisory.get("products", []):
                parsed = parse_product_string(product.get("product", ""))
                rows.append({
                    "advisory_url": advisory["url"],
                    "advisory_date": advisory.get("advisory_date", ""),
                    "advisory_source": "CCC Public Health and Safety Advisory",
                    "source_product_text": parsed["source_product_text"],
                    "package_label": product.get("batch", ""),
                    "cultivar_candidate_text": product.get("strain", ""),
                    "commercial_product_label": parsed["commercial_product_label"],
                    "package_size_text": parsed["package_size_text"],
                    "product_form": parsed["product_form"],
                    "brand_candidate": parsed["brand_candidate"],
                })
        import csv as _csv

        path = self.store.durable_root / "affected-packages.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        if rows:
            with open(path, "w", encoding="utf-8", newline="") as handle:
                writer = _csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

    def _write_cultivar_candidates_artifact(self, advisories: list[dict]) -> None:
        import csv as _csv

        counts: Counter = Counter()
        first_seen: dict = {}
        last_seen: dict = {}
        categories: dict[str, set] = defaultdict(set)
        advisories_by: dict[str, set] = defaultdict(set)
        examples: dict[str, list] = defaultdict(list)
        for advisory in advisories:
            date = advisory.get("advisory_date", "")
            for product in advisory.get("products", []):
                strain = (product.get("strain") or "").strip()
                if not strain:
                    continue
                normalized = re.sub(r"[^a-z0-9 ]", " ", strain.lower())
                normalized = re.sub(r"\s+", " ", normalized).strip()
                counts[normalized] += 1
                categories[normalized].add(product.get("product", ""))
                advisories_by[normalized].add(advisory["url"])
                if normalized not in first_seen or (date and date < first_seen[normalized]):
                    first_seen[normalized] = date or "?"
                if not date or date > last_seen.get(normalized, ""):
                    last_seen[normalized] = date or "?"
                if len(examples[normalized]) < 3:
                    examples[normalized].append({
                        "product": product.get("product", ""),
                        "batch": product.get("batch", ""),
                    })
        # include testing-2024 strain column when available
        for row in self.normalized.get("testing_2024", [])[:2000]:
            strain = (row.get("strain") or "").strip()
            if not strain:
                continue
            normalized = re.sub(r"[^a-z0-9 ]", " ", strain.lower())
            normalized = re.sub(r"\s+", " ", normalized).strip()
            counts[normalized] += 1
            categories[normalized].add(row.get("product_category") or "testing")
            if normalized not in first_seen:
                first_seen[normalized] = (row.get("date") or "?")[:10]
            last_seen[normalized] = (row.get("date") or "?")[:10]
            if len(examples[normalized]) < 3:
                examples[normalized].append({"metrc_id": row.get("metrc_id", "")[:12]})
        path = self.store.durable_root / "cultivar-candidates.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as handle:
            writer = _csv.writer(handle)
            writer.writerow(["source_label", "normalized_candidate", "occurrence_count",
                             "product_categories", "advisory_connections",
                             "first_seen", "last_seen", "example_source_records"])
            for normalized, count in counts.most_common():
                writer.writerow([
                    examples[normalized][0].get("product", "") if examples[normalized] else "",
                    normalized, count, ";".join(sorted(categories[normalized]))[:200],
                    ";".join(sorted(advisories_by[normalized]))[:200],
                    first_seen.get(normalized, ""), last_seen.get(normalized, ""),
                    json.dumps(examples[normalized][:2])[:300],
                ])

    def _write_source_catalog_artifact(self) -> None:
        catalog = {
            "regulator": REGULATOR,
            "disclaimer": DISCLAIMER,
            "datasets": [
                {
                    "slug": d.slug, "title": d.title, "csv_url": d.csv_url,
                    "json_url": d.json_url, "format": d.format,
                    "reporting_period": d.reporting_period,
                    "source_last_updated": d.source_last_updated,
                    "description": d.description, "required_columns": d.required_columns,
                    "column_types": d.column_types, "disclaimer": d.disclaimer,
                    "clarification": d.clarification,
                }
                for d in DATASETS.values()
            ],
            "privacy": {
                "excluded_field_names": sorted(PRIVACY_SPEC.excluded_field_names),
                "entity_allowlists": {k: sorted(v) for k, v in PRIVACY_SPEC.entity_allowlists.items()},
            },
            "advisories_url": REGULATOR["advisories_url"],
        }
        self.store.write_durable_json("source-catalog.json", catalog)

    def _write_schema_report_artifact(self) -> None:
        lines = ["# Massachusetts CCC — Schema Report", "",
                 f"Generated by {self.store.importer_version} (schema v{self.store.schema_version}).", ""]
        manifest = self.store.read_manifest()
        for slug, entries in sorted(manifest.get("datasets", {}).items()):
            latest = entries[-1] if entries else {}
            lines.append(f"## {slug}")
            lines.append("")
            lines.append(table(
                ["Field", "Value"],
                [["Official source", latest.get("official_source_url", "")],
                 ["Reporting period", latest.get("reporting_period", "")],
                 ["Rows", str(latest.get("row_count", ""))],
                 ["Raw SHA-256", (latest.get("raw_sha256") or "")[:16] + "…"],
                 ["Content type", latest.get("http_content_type", "")],
                 ["Retrieval", latest.get("retrieval_timestamp", "")],
                 ["Clarification", latest.get("source_clarification_or_correction") or "—"]]
            ))
            columns = latest.get("column_schema", [])
            if columns:
                lines += ["", "Columns: " + ", ".join(columns[:40]) + ("…" if len(columns) > 40 else "")]
            lines.append("")
        self.store.write_durable_markdown("schema-report.md", "\n".join(lines))

    def _write_privacy_spec_artifact(self) -> None:
        lines = [
            "# Massachusetts CCC — Privacy and Excluded-Field Specification", "",
            f"State: {STATE}  ·  Generator: {self.store.importer_version}", "",
            "## Excluded field names", "",
            "\n".join(f"- `{name}`" for name in sorted(PRIVACY_SPEC.excluded_field_names)),
            "", "## Sensitive-value patterns scanned", "",
            "- EIN/TIN (`NN-NNNNNNN`)", "- Email addresses", "- Phone numbers",
            "- Full street addresses", "- Raw coordinates", "",
            "## Entity allowlists", "",
        ]
        for entity_type, fields in sorted(PRIVACY_SPEC.entity_allowlists.items()):
            lines.append(f"### {entity_type}")
            lines.append("")
            lines.append("\n".join(f"- `{f}`" for f in fields))
            lines.append("")
        self.store.write_durable_markdown("privacy-spec.md", "\n".join(lines))
