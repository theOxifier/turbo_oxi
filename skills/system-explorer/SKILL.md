---
name: system-explorer
description: Build repeatable interactive explorers for architecture, processes, workflows, protocols, dependencies, and data flows from source evidence. Use when a user wants to click into a system, trace handoffs or transfers, inspect components and payloads, or replay a scenario. Produces a portable HTML explorer and editable JSON model.
---

# System Explorer

Turn evidence about a system into an interactive model people can inspect.
Apply the same workflow to services, people, teams, agents, physical equipment,
process stages, protocols, or documents. Domain terminology belongs in the model,
not in custom viewer code.

## Deliverables

Produce these together in the user's chosen output directory:

- `model.json`: editable, versioned source of truth.
- `explorer.html`: self-contained interactive map, sequence view, inspector,
  scenario selector, and event playback. Opens without a server or dependencies.
- A brief handoff in chat: scope, evidence, unresolved questions, validation,
  and links to the model and explorer.

Use bundled scripts and template. Do not build a bespoke app for every request.
Read `references/model-format.md` before constructing a model. Use
`examples/software-system.json` or `examples/approval-process.json` as a shape
reference, never as facts about the user's system.

## 1. Establish the exploration question

Identify the system, audience, boundary, and one question to answer, such as
“What happens when a job fails?” or “Who receives this request next?” Infer
routine choices from context. Ask one concise question only if missing scope
would materially change the model; continue independent evidence gathering.

Choose a manageable first view: typically 5–15 entities and 1–3 scenarios.
These are readability targets, not validator limits. For larger systems, choose
an overview and use `parent_id` for nested subsystems. Expand details on demand.
Do not inventory an entire repository before producing a useful first slice.

## 2. Gather evidence

Inspect the supplied code, docs, diagrams, configuration, logs, or user narrative.
Use connected sources only within their existing access rules. Record stable
source IDs, file paths and line references, URLs, and relevant revision/date.
Do not send architecture or private inputs to the public reference app.

Separate entity existence, persistent relationships, and events in a scenario.
A dependency does not prove a transfer happened. A diagram does not prove live
behavior. Distinguish current and proposed systems in `perspective`; label
observed, inferred, illustrative, proposed, and unknown claims with `evidence`.
“Observed” means supported by the cited evidence, not automatically observed
in production. State exactly what code, documentation, or trace supports it.

Do not invent payload contents, timings, sizes, protocols, error paths, or
ownership. Use symbolic/synthetic examples and label them illustrative.
If evidence supports only static structure, leave `scenarios` empty.
For a teaching example, mark the model illustrative throughout.

## 3. Normalize the model

Use the version 1 contract in `references/model-format.md`:

- **Entities**: things with identity and inspectable details.
- **Relationships**: directed dependencies, transfers, responsibilities, or handoffs.
- **Scenarios**: explicit paths through a system, including alternatives or failures.
- **Events**: ordered actions on a relationship or a single entity.
- **Sources and evidence**: provenance and uncertainty visible in the inspector.

Keep IDs stable across revisions; avoid deriving identity from array position.
Use readable labels and domain-specific kinds. Entity and relationship
`properties` carry domain facts without modifying the renderer. Use scenario
`payload` to illustrate a transfer and `state_changes` for explicit, inspectable
state transitions. The viewer replays authored events; it is not a runtime engine.

Use `group` for a lane/layer/team and `parent_id` for drill-down. Add optional
`x`/`y` only if the automatic layout obscures the story. Model relationships
between visible peers at each level; the viewer does not invent aggregated edges.
Describe abstractions and omitted internals in entity descriptions.

Readability matters: concise labels, meaningful edge verbs, short event summaries,
clear outcomes. Do not encode a general workflow as network packets or require
IP addresses, ports, or bytes.

## 4. Generate and refine

From the skill directory, run:

```sh
python3 scripts/validate_model.py /absolute/output/model.json
python3 scripts/render.py /absolute/output/model.json --output /absolute/output/explorer.html
```

Use the actual skill directory as the command's working directory. Scripts use
only Python's standard library. No package installation, account, hosting,
telemetry, external fonts, CDN, or API keys are needed for generated explorers.

The viewer supports topology/sequence switching, nested component exploration,
search and group filtering, clickable entities and relationships, scenario
selection, clickable event rows, previous/next/reset, playback speed, visible
state, evidence inspection, and downloading the embedded model.

If the user requests richer rendering or hosting, preserve the model contract.
Follow the relevant website/deployment skill for that additional work; do not
publish or broaden access merely to deliver an explorer.

## 5. Verify before handing off

Validate references, IDs, hierarchy, evidence, event order, and state targets
with the validator. Open the generated HTML in an available browser and check:

1. Initial overview is readable, including labels and overlapping relationships.
2. Clicking an entity or edge opens the corresponding details and evidence.
3. Selecting a scenario and event updates map, sequence, inspector, and state.
4. Back/reset restores previous state; switching scenarios clears prior state.
5. Search, group filtering, nested navigation, and keyboard controls behave.
6. A small viewport remains usable; the browser console has no errors.

Exercise at least one handoff/transfer and any modeled failure alternative.
Check a static model if that is what the evidence supports. If browser testing
is blocked, identify the exact unverified interaction; do not imply it passed.

Run `python3 -m unittest discover -s tests` after changing the renderer or validator.
The bundled `tests/browser_smoke.py` additionally exercises both examples with
Playwright if available; it is a development check, not an output dependency.

## 6. Iterate without losing provenance

On new evidence, edit the existing model, keep stable IDs, update evidence and
scenario descriptions, rerun validation, and regenerate. Do not silently promote
an inference to an observed fact. If comparing current and proposed behavior,
produce separately labeled models unless the user requests a comparison UI.

In the final handoff, explain the question the model answers, which inputs were
used, what remains inferred or missing, and which checks passed. Link the HTML
and JSON. Do not claim global skill installation when only a local skill folder
or downloadable package was created.
