# System Explorer

A generic skill for turning a system description or source evidence into an
interactive explorer. The repeatable workflow is:

**Frame a question → gather evidence → model entities and relationships → author
scenarios and events → validate → render → inspect → refine.**

Works with software architecture, people and operational processes, agent
workflows, protocols, data pipelines, and other systems with components and
relationships. The model provides domain language; the viewer stays reusable.

## Use the skill

The entry point is [`SKILL.md`](SKILL.md). Keep this folder intact when
installing it in your agent's supported skills location; the scripts, template,
examples, and references are part of the skill.

Example requests:

- “Use system-explorer to visualize this repository's job lifecycle. Show the
  successful path and any failure path supported by the code.”
- “Use system-explorer to turn these onboarding notes into an interactive
  process. Let me inspect owners, handoffs, and document states.”
- “Use system-explorer to explain how these agents delegate work. Distinguish
  documented behavior from inferred behavior.”
- “Update this explorer with the new queue design. Keep entity IDs stable and
  label the model proposed.”

The skill is for creating and maintaining explorers. It does not monitor a
system or execute workflows. A replay follows the authored scenario. Proposed
systems and synthetic teaching examples are explicitly labeled.

## Run the bundled examples

From this directory, using Python 3.10 or later:

```sh
python3 scripts/validate_model.py examples/software-system.json
python3 scripts/render.py examples/software-system.json --output out/software-system.html
python3 scripts/render.py examples/approval-process.json --output out/approval-process.html
```

Open an output HTML file in your browser. It embeds its JSON model and needs no
server, build tool, external assets, or network connection. If your managed
browser blocks local files, serve the output directory locally instead:

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory out
```

Visit `http://127.0.0.1:8765/software-system.html` in the same environment's
browser. This is a local preview, not a published site.

Copy an example to your output directory and edit its model using
`references/model-format.md`. Regenerate HTML after each model change. The
**Download model** button exports the embedded JSON; editing that JSON does not
change an already-generated HTML file until you render again.

## Interaction model

- **Topology**: directed relationships, active transfer highlighting, visible
  entity state, and nested components through **Explore inside**.
- **Sequence**: authored event order for the selected scenario.
- **Inspector**: descriptions, properties/contracts, payloads, state changes,
  source references, and evidence status.
- **Timeline**: select any event, step backward/forward, reset, or play at
  illustrative pacing. Scenario changes reset state.
- **Navigation**: find entities, filter groups, choose scenarios, inspect
  connections, and return to an overview.

Topology shows structural edges even when they have not executed. A selected
scenario shows all participants; entity search and group filters apply to the
sidebar while a scenario is active. In overview mode they also filter the map.
Sequence order does not assert causal order between simultaneous events.

## Scope and limits

The viewer is an original implementation inspired by the interaction pattern
of [Protocol Explorer](https://protocol-explorer-alpha.vercel.app/), inspected
on November 7, 2026. No app source code or art assets were copied. Its protocol
catalog and packet decoders are not included.

Version 1 provides authored traces, finite nested views, and SVG rendering.
It does not infer runtime causality, discover systems automatically, execute
branching or concurrent simulations, subscribe to telemetry, decode binary
packets, or virtualize very large graphs. Use focused overview models with
nested detail for readability. Automated evidence extraction can be added
later while preserving this model contract.

Both bundled examples are illustrative. No repository or business policy was
provided, so they make no claims about the user's actual systems.

## Validation

```sh
python3 -m unittest discover -s tests
python3 tests/browser_smoke.py
```

The first command uses only Python's standard library. The optional browser
check requires Playwright and Chromium in the development environment; the
viewer has no such dependency. It tests both domains, state reconstruction,
scenario switching, inspection, sequence, playback, search, drill-down, mobile,
export, static models, and safe display of untrusted model text.

## Files

- `SKILL.md`: triggers and repeatable agent workflow.
- `references/model-format.md`: version 1 data contract.
- `references/evaluation.md`: acceptance prompts for later skill evaluations.
- `assets/viewer.html`: reusable self-contained viewer template.
- `scripts/validate_model.py`: model and provenance validation.
- `scripts/render.py`: deterministic model-to-HTML generation.
- `examples/`: two domains using the same renderer.
- `tests/`: model, serialization, and browser checks.
