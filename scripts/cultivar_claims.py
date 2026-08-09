"""Cultivar identity: claim vocabulary, validation, name normalization.

This module implements the provenance-aware cultivar identity model for the
Thermal Extraction Devices archive. Its purpose is to let the repository
represent breeder claims, aliases, lineage claims, seed-bank listings, product
labels, and unresolved identity *without* pretending the cannabis naming
ecosystem is perfectly consistent.

Design notes
------------

* The published Boris graph only supports four relation kinds
  (``relates_to``, ``implements``, ``depends_on``, ``supersedes``). The rich
  claim vocabulary in this module therefore lives in a machine-readable
  registry (``metadata/cultivar-claims.jsonl``) that is validated against the
  content tree and exported for RAG / machine consumers. See
  ``docs/cultivar-identity-model.md``.
* Every claim carries a source (name, role, optional retrieval date and URL),
  a human-readable status, and optional wording/notes. No numeric confidence
  scores are fabricated; the archive has no principled scoring model.
* A source saying "this is Blue Dream" is a *claim*. The claim kinds below
  preserve the distinction between an assertion and the assertion's subject.
"""

from __future__ import annotations

import json
import re
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any, Iterable

# ---------------------------------------------------------------------------
# Relationship vocabulary
# ---------------------------------------------------------------------------

#: Allowed claim kinds. Keys are the machine vocabulary; values are the
#: semantic definition used for documentation and rendering.
CLAIM_KINDS: dict[str, str] = {
    "alias_of": (
        "Evidence-backed identity: subject and object are treated as the same "
        "genetic object in this archive."
    ),
    "claimed_alias_of": (
        "A source claims subject and object refer to the same genetic object; "
        "the archive does not merge them on the source's word alone."
    ),
    "bred_by": (
        "Evidence-backed origin: subject cultivar was bred by object breeder."
    ),
    "claimed_bred_by": (
        "A source claims subject cultivar was bred by object breeder."
    ),
    "lineage_parent": (
        "Evidence-backed lineage: subject has object as a parent."
    ),
    "claimed_lineage_parent": (
        "A source claims subject has object as a parent."
    ),
    "sold_by": (
        "Evidence-backed: subject cultivar or seed listing is sold by object "
        "seller."
    ),
    "listed_by": (
        "Evidence-backed: subject cultivar or seed listing is listed by object "
        "seed bank / catalog."
    ),
    "seed_source": (
        "Evidence-backed: subject seed stock originates from object seed "
        "source / breeder."
    ),
    "product_claims_cultivar": (
        "A product record's label carries the subject cultivar name; object is "
        "the cultivar entity the label refers to."
    ),
    "batch_claims_cultivar": (
        "A laboratory report's submitted sample carried the subject cultivar "
        "name; object is the cultivar entity the label refers to."
    ),
    "possibly_same_as": (
        "Unresolved identity: subject may be the same genetic object as "
        "object. The archive does not merge them."
    ),
    "historically_associated_with": (
        "Documented historical association between subject and object without "
        "an identity claim."
    ),
    "source_disagrees_with": (
        "Two retained claims conflict. Unlike other kinds, subject and object "
        "are claim IDs (not content entities): subject is one side of the "
        "dispute and object the other; both claims remain in the registry."
    ),
}

#: Source roles. Different sources are authoritative for different things; the
#: role is recorded per claim and is never flattened into a single
#: credibility bucket.
SOURCE_TYPES: dict[str, str] = {
    "breeder": (
        "First-party breeder: strong evidence for its own breeding and release "
        "claims."
    ),
    "seed_bank": (
        "Seed bank / catalog: strong evidence that it listed or sold a "
        "cultivar under a given name."
    ),
    "producer": (
        "Licensed producer: strong evidence for the label it placed on its own "
        "product."
    ),
    "testing_laboratory": (
        "Testing laboratory: strong evidence for what the submitted "
        "sample/report called the product."
    ),
    "regulator": (
        "Regulator: strong evidence for licensed product/report metadata "
        "within its system."
    ),
    "community": (
        "Community database: useful discovery or historical context, weaker "
        "identity authority."
    ),
    "database": (
        "Aggregated database: useful discovery context, weaker identity "
        "authority."
    ),
    "forum": (
        "Forum discussion: useful historical context, weaker identity "
        "authority."
    ),
    "archive": (
        "This repository's own curated record: secondary attribution that "
        "inherits the page's stated provenance."
    ),
}

#: Human-readable status vocabulary. No numeric confidence scores are used;
#: the archive does not have a principled scoring model.
STATUSES: frozenset[str] = frozenset({
    "verified",
    "well_supported",
    "claimed",
    "conflicting",
    "tentative",
    "unresolved",
    "historical",
})

CLAIM_ID_RE = re.compile(r"^[A-Z0-9]+(?:-[A-Z0-9]+)*$")

#: Epistemic templates used by :func:`render_claim_context`. Claimed kinds use
#: "claims", evidence-backed kinds use "states", so machine-retrieved context
#: never confuses "Seed Bank X claims Y" with "Y is definitively true".
_RENDER_TEMPLATES: dict[str, str] = {
    "alias_of": "{subject} is treated as the same genetic object as {object}",
    "claimed_alias_of": "{subject} is claimed to be an alias of {object}",
    "bred_by": "{subject} was bred by {object}",
    "claimed_bred_by": "{subject} is claimed to have been bred by {object}",
    "lineage_parent": "{subject} has lineage parent {object}",
    "claimed_lineage_parent": "{subject} is claimed to have lineage parent {object}",
    "sold_by": "{subject} is sold by {object}",
    "listed_by": "{subject} is listed by {object}",
    "seed_source": "{subject} traces seed stock to {object}",
    "product_claims_cultivar": "product record {subject} is labeled as {object}",
    "batch_claims_cultivar": "batch report {subject} was labeled as {object}",
    "possibly_same_as": "{subject} may be the same genetic object as {object} (unresolved)",
    "historically_associated_with": "{subject} is historically associated with {object}",
}

# ---------------------------------------------------------------------------
# Name normalization (matching / discovery only)
# ---------------------------------------------------------------------------


def normalize_name(name: str) -> str:
    """Surface-level normalization for matching and discovery only.

    * case folding
    * Unicode normalization (NFC)
    * whitespace collapsing
    * punctuation variant folding (any non-alphanumeric character acts as a
      separator)

    Meaningful tokens are preserved: numbers, phenotype markers, hash
    numbers, breeder prefixes, ``BX``, ``F1``, ``F2``, ``Auto``, ``Fast``.

    This function does **not** resolve abbreviations or aliases: ``gg4`` and
    ``gorilla glue 4`` normalize to different keys, and connecting them
    requires an evidence-backed ``alias_of`` / ``claimed_alias_of`` record in
    the claim registry. Canonical display names are never rewritten; this
    normalization exists only for lookup keys.
    """
    folded = unicodedata.normalize("NFC", str(name)).casefold()
    separated = "".join(ch if ch.isalnum() else " " for ch in folded)
    return " ".join(separated.split())


# ---------------------------------------------------------------------------
# Claim registry loading and validation
# ---------------------------------------------------------------------------


def load_claims(path: Path) -> list[dict[str, Any]]:
    """Load a JSONL claim registry. Each non-blank line is one claim object."""
    claims: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                claim = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"{path}:{line_no}: invalid JSON: {error}"
                ) from error
            if not isinstance(claim, dict):
                raise ValueError(f"{path}:{line_no}: claim must be a JSON object")
            claims.append(claim)
    return claims


def validate_claims(
    claims: Iterable[dict[str, Any]],
    entity_ids: set[str],
) -> list[str]:
    """Validate claims against the vocabulary and the content entity graph.

    Returns a list of human-readable problems (empty == all good). Does not
    raise; callers decide how to surface problems.
    """
    problems: list[str] = []
    seen: set[str] = set()

    # First pass: collect declared claim IDs so that
    # ``source_disagrees_with`` records can reference other claims.
    claim_ids: set[str] = {
        claim["claim_id"] for claim in claims if claim.get("claim_id")
    }

    for claim in claims:
        claim_id = claim.get("claim_id", "")
        where = f"claim {claim_id!r}" if claim_id else "unnamed claim"

        if not claim_id:
            problems.append(f"{where}: missing claim_id")
        elif not CLAIM_ID_RE.fullmatch(claim_id):
            problems.append(
                f"{where}: claim_id {claim_id!r} must match {CLAIM_ID_RE.pattern}"
            )
        if claim_id and claim_id in seen:
            problems.append(f"{where}: duplicate claim_id")
        seen.add(claim_id)

        kind = claim.get("kind")
        if kind not in CLAIM_KINDS:
            problems.append(
                f"{where}: unknown kind {kind!r}; allowed: "
                + ", ".join(sorted(CLAIM_KINDS))
            )

        subject = claim.get("subject")
        if not subject:
            problems.append(f"{where}: missing subject")
        obj = claim.get("object")
        if not obj:
            problems.append(f"{where}: missing object")
        object_is_entity = claim.get("object_is_entity") is True

        if kind == "source_disagrees_with":
            # subject/object are claim IDs, not content entities.
            if object_is_entity:
                problems.append(
                    f"{where}: source_disagrees_with references claim IDs; "
                    "object_is_entity must not be true"
                )
            if subject and subject not in claim_ids:
                problems.append(
                    f"{where}: subject {subject!r} is not a known claim ID"
                )
            if obj and obj not in claim_ids:
                problems.append(
                    f"{where}: object {obj!r} is not a known claim ID"
                )
        else:
            if subject and subject not in entity_ids:
                problems.append(
                    f"{where}: subject {subject!r} is not a content entity ID"
                )
            if object_is_entity and obj not in entity_ids:
                problems.append(
                    f"{where}: object {obj!r} declared as an entity but is not "
                    "a content entity ID"
                )
        if subject and obj and subject == obj:
            problems.append(f"{where}: self-referential claim")

        status = claim.get("status")
        if status not in STATUSES:
            problems.append(
                f"{where}: unknown status {status!r}; allowed: "
                + ", ".join(sorted(STATUSES))
            )

        source = claim.get("source")
        if not isinstance(source, dict):
            problems.append(f"{where}: missing source object")
        else:
            if not source.get("name"):
                problems.append(f"{where}: source.name is required")
            source_type = source.get("type")
            if source_type not in SOURCE_TYPES:
                problems.append(
                    f"{where}: unknown source.type {source_type!r}; allowed: "
                    + ", ".join(sorted(SOURCE_TYPES))
                )
            retrieved = source.get("retrieved")
            if retrieved:
                try:
                    date.fromisoformat(str(retrieved))
                except ValueError:
                    problems.append(
                        f"{where}: source.retrieved {retrieved!r} is not an "
                        "ISO-8601 date"
                    )
            url = source.get("url")
            if url and not str(url).startswith(("http://", "https://")):
                problems.append(f"{where}: source.url must be http(s)")

    return problems


# ---------------------------------------------------------------------------
# Epistemic rendering for machine retrieval / RAG
# ---------------------------------------------------------------------------


def render_claim_context(
    claim: dict[str, Any],
    claims_by_id: dict[str, dict[str, Any]] | None = None,
) -> str:
    """Render one claim as retrieval-ready context.

    The output keeps epistemic language: who said it, in what role, when it
    was retrieved, and the claim's status. A retrieval system can therefore
    distinguish *"Seed Bank X claims Y"* from *"Y is definitively true."*

    ``claims_by_id`` is optional; when provided, ``source_disagrees_with``
    records are resolved to the two conflicting claims so the rendered
    context names the disputed entity and both attributions.
    """
    kind = claim.get("kind", "unknown")
    source = claim.get("source") or {}
    source_name = source.get("name") or "unknown source"
    source_type = source.get("type") or "unknown role"
    retrieved = source.get("retrieved")
    retrieved_clause = f", retrieved {retrieved}" if retrieved else ""
    wording = claim.get("wording")
    wording_clause = f" Wording: {wording!r}." if wording else ""
    status = claim.get("status", "unresolved")

    if kind == "source_disagrees_with":
        lookup = claims_by_id or {}
        side_a = lookup.get(claim.get("subject"))
        side_b = lookup.get(claim.get("object"))
        if side_a is not None and side_b is not None:
            entity = side_a.get("subject") or side_b.get("subject") or "?"
            statement = (
                f"the attribution of {entity} is disputed between claim "
                f"{side_a.get('claim_id')} ({side_a.get('object')}) and claim "
                f"{side_b.get('claim_id')} ({side_b.get('object')})"
            )
        else:
            statement = (
                f"claim {claim.get('subject', '?')} disagrees with claim "
                f"{claim.get('object', '?')}"
            )
    else:
        template = _RENDER_TEMPLATES.get(
            kind, "{subject} {kind} {object}".format(
                subject="{subject}", kind=kind, object="{object}"
            )
        )
        statement = template.format(
            subject=claim.get("subject", "?"),
            object=claim.get("object", "?"),
        )

    return (
        f"Per {source_name} ({source_type}{retrieved_clause}): {statement}. "
        f"Status: {status}.{wording_clause}"
    )
