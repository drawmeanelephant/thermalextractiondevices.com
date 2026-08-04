# Thermal Extraction Devices Archive

Thermal Extraction Devices (`thermalextractiondevices.com`) is a static technical archive compiled by [Boris](https://github.com/drawmeanelephant/boris) using the Trunk/Satellite graph model and deployed to Cloudflare Pages at [https://thermalextractiondevices.com](https://thermalextractiondevices.com).

---

## Production Deployment

* **Source of Record**: `drawmeanelephant/thermalextractiondevices.com`
* **Compiler**: [Boris](https://github.com/drawmeanelephant/boris) (CI tracks the `afterparty` branch)
* **Production Theme**: Cantilever (`themes/cantilever/`)
* **Output Path**: `dist/cantilever/`
* **Host**: Cloudflare Pages (`thermalextractiondevices-com`)
* **Public URL**: [https://thermalextractiondevices.com](https://thermalextractiondevices.com)

---

## Quick Start & Operating Commands

Build the primary site and serve it locally:

```sh
./preview.sh
```

The default output is written to `dist/cantilever/` and the server listens on `http://localhost:8000`.

Run the complete local validation gate:

```sh
./bin/validate_graph.sh
```

Primary build and publishing scripts:

* `./scripts/ted-build.sh`: Runs the production HTML build.
* `./scripts/ted-publish.sh`: Exports HTML, IR, RAG, Context, sitemap, and `llms.txt` artifacts.

---

## Repository Layout

```text
content/                    # Source Markdown corpus
themes/cantilever/         # Primary production theme and templates
metadata/id-policy.json    # Canonical identity rules
metadata/id-map.jsonl      # Legacy-to-canonical migration map
scripts/ted_ids.py         # ID migration and validation helper
scripts/ted-build.sh       # Production HTML build script
scripts/ted-publish.sh     # HTML, IR, RAG, Context, and llms publishing script
bin/validate_graph.sh      # Graph integrity and publication gate
```

Generated outputs under `dist/`, `publish/`, `site/`, and local compiler binaries (`bin/boris*`) are build artifacts and must not be committed to git.
