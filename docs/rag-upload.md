# RAG Upload Workflow

`./scripts/ted-publish.sh` produces three complementary Boris RAG surfaces
under `publish/` from one validated content graph:

| Surface | Use | Upload contents |
| --- | --- | --- |
| `publish/rag/` | Canonical Boris working export for automation and inspection | `working-*.md`; keep `manifest.json` as a local sidecar |
| `publish/rag-bundle/` | Human handoff to ChatGPT, Gemini, Grok, or another chat/RAG tool | The semantically named `.md` files only |
| `publish/rag-complete/` | Full-corpus ingestion for systems that preserve directory trees | The complete directory tree; `catalog_meta.json` and `catalog.jsonl` are machine sidecars |

The normal upload choice is `publish/rag-bundle/`. Its files are named like:

```text
thermal-extraction-devices-working-context-01-of-11-affected-products-to-cultivars.md
```

The filename identifies the corpus, pack role, ordinal, and broad content
range. The bytes are copied unchanged from Boris's working pack; only the
manifest's `upload_files[].path` and document `pack` references are rewritten
to match the semantic names. Do not upload `manifest.json` unless the target
pipeline explicitly consumes integrity metadata.

The pack target defaults to 131,072 bytes (128 KiB), which keeps the current
corpus within a 20-file upload limit. To choose a different deterministic pack
size or corpus label for a release:

```sh
RAG_SPLIT_SIZE=262144 \
RAG_BUNDLE_NAME=thermal-extraction-devices-2026-08 \
./scripts/ted-publish.sh
```

`RAG_BUNDLE_NAME` is a filename label, not a content or ID namespace. The
complete export is generated with Boris's explicit `--rag --complete` mode;
it is intentionally separate from the smaller working-context upload set.
