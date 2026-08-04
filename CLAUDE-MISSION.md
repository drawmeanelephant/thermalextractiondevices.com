# Claude Mission & Repository Mandates

## Repository Goal
Maintain and extend the **Thermal Extraction Devices** (`thermalextractiondevices.com`) technical archive using the **Boris** static compiler.

## Core Rules
1. **Engine**: Static site output is rendered by Boris. Do not add JavaScript frameworks or static site generators (Vite, Next, Astro, Eleventy, etc.).
2. **Schema Integrity**: Maintain form-based ID schema (`TED-XXXX`, `TSPEC-XXXX`, `TSAFE-XXXX`, `TREF-XXXX`, `TGDE-XXXX`, `TREL-XXXX`, `TCHG-XXXX`).
3. **Graph Integrity**: All satellites must specify a valid trunk `parent`.
4. **Verification Gate**: `./bin/validate_graph.sh` must succeed clean before any release or commit.
