# RAG Upload Workflow

`./scripts/ted-publish.sh` produces complementary raw and resolved Boris RAG
surfaces under `publish/` from one validated content graph:

| Surface | Use | Upload contents |
| --- | --- | --- |
| `publish/rag/` | Canonical raw Boris working export for automation, inspection, and provenance | `working-*.md`; keep `manifest.json` as a local sidecar |
| `publish/rag-bundle/` | Semantically named copy of the raw Boris working export | The semantically named `.md` files only; these retain Boris include markers |
| `publish/rag-resolved/` | Derived working export with `content/includes/` bodies expanded | `working-*.md` plus `manifest.json` when integrity metadata is consumed |
| `publish/rag-resolved-bundle/` | Normal human handoff to ChatGPT, Gemini, Grok, or another chat/RAG tool | The semantically named resolved `.md` files only |
| `publish/rag-complete/` | Raw full-corpus ingestion for systems that preserve directory trees | The complete directory tree; `catalog_meta.json` and `catalog.jsonl` are machine sidecars |

The normal upload choice is `publish/rag-resolved-bundle/`. Its files are
named like:

```text
thermal-extraction-devices-resolved-working-context-01-of-11-affected-products-to-cultivars.md
```

The filename identifies the corpus, pack role, ordinal, and broad content
range. The resolved packs are derived from the raw packs and expand each
validated include body in place. The raw `publish/rag/` bytes and manifest are
never used as an output scratch area; the resolved manifest records the raw
manifest hash, raw pack hashes, resolved pack hashes, and include-resolution
summary. Do not upload either `manifest.json` unless the target pipeline
explicitly consumes integrity metadata.

`publish/rag-bundle/` remains available when a consumer needs the exact Boris
working bytes for provenance or compiler-level inspection. It is not the
recommended consumer upload because Boris working packs intentionally retain
`{{include ...}}` markers. `publish/rag-complete/` is also a raw Boris surface;
the resolved publication currently targets the bounded working export rather
than duplicating the full-corpus tree.

The publish step runs `python3 scripts/audit_rag_includes.py` twice: first to
validate source references and safe include paths, then to fail if any marker
remains in `publish/rag-resolved/`. Missing, malformed, traversal, symlink
escape, and cyclic includes fail the publication before a resolved directory
is replaced. The audit is deterministic and never edits source content.

The pack target defaults to 131,072 bytes (128 KiB), which keeps the current
corpus within a 20-file upload limit. To choose a different deterministic pack
size or corpus label for a release:

```sh
RAG_SPLIT_SIZE=262144 \
RAG_BUNDLE_NAME=thermal-extraction-devices-2026-08 \
RAG_RESOLVED_BUNDLE_NAME=thermal-extraction-devices-2026-08-resolved \
./scripts/ted-publish.sh
```

`RAG_BUNDLE_NAME` and `RAG_RESOLVED_BUNDLE_NAME` are filename labels, not
content or ID namespaces. `RAG_RESOLVED_DIR` and
`RAG_RESOLVED_BUNDLE_DIR` can relocate the derived directories, but each must
remain a sibling of its raw input for the safe staging guard. The complete
export is generated with Boris's explicit `--rag --complete` mode; it is
intentionally separate from the smaller working-context upload set.
