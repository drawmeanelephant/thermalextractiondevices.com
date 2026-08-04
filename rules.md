# Thermal Extraction Devices — Project Rules

1. **Static Site Build System**:
   - Compiler: Boris (Zig)
   - Input: `content/`
   - Output: `dist/cantilever/`
   - Theme: `themes/cantilever/`

2. **Frontmatter Constraints**:
   - Allowed fields: `id`, `title`, `parent`, `status`, `tags`, `relations`.
   - Do not use arbitrary or unsupported frontmatter keys.

3. **Validation & Deployment**:
   - Run `./bin/validate_graph.sh` to check graph diagnostics and IDs.
   - Cloudflare Pages deploys `dist/cantilever` via GitHub Actions (`.github/workflows/deploy.yml`).
