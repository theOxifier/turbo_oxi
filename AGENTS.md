# Working in turbo_oxi

This repository hosts reusable personal skills. Put each skill in
`skills/<skill-name>/` with `SKILL.md` as its entry point. Retain scripts,
templates, references, and examples alongside the skill. Update the root README
catalog when adding or renaming a skill.

Keep workflows generic. Domain examples belong in example data, not hardcoded
renderer behavior. Preserve stable model IDs and evidence when updating an
explorer. Do not commit credentials, private architecture, local absolute paths,
Python caches, or generated per-project output.

For System Explorer, run from `skills/system-explorer/`:

```sh
python3 -m unittest discover -s tests
python3 scripts/validate_model.py examples/software-system.json
python3 scripts/validate_model.py examples/approval-process.json
python3 scripts/render.py examples/software-system.json --output out/software-system.html
python3 scripts/render.py examples/approval-process.json --output out/approval-process.html
```

If changing the viewer, also run `python3 tests/browser_smoke.py` when Playwright
and Chromium are available. It is a development dependency, not a runtime
requirement for generated explorers. Report any unverified interactions.
