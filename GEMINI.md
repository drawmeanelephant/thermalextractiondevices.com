# Gemini Guidelines for Thermal Extraction Devices

This project uses **Boris** (a compiled Zig static site generator) to build `https://thermalextractiondevices.com`.

## Key Rules
- Read `AGENTS.md` before making structural or content changes.
- `content/` contains the Markdown files.
- `themes/cantilever/` houses the production design.
- Always run `./bin/validate_graph.sh` to check entity IDs and link integrity.
- Never commit `dist/`, `publish/`, or `bin/boris`.
