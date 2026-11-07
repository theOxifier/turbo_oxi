# Skill acceptance prompts

Use these when evaluating the skill in a fresh chat. Evaluate the agent's
workflow as well as the rendered interface. No prompt requires a specific
protocol or technology.

| Prompt | Expected behavior |
| --- | --- |
| “Visualize this codebase's background job path. Let me inspect transfers.” | Reads relevant code and config; cites evidence; models a manageable path; emits JSON and HTML; checks clickable transfers. |
| “Make this purchasing process explorable: requester → manager → finance, with a revision loop.” | Models people, decisions, artifacts, and handoffs; uses the same renderer without network labels or invented timings. |
| “Explain how these three agents delegate a task; the callback is undocumented.” | Models supported transfers and local actions; labels the undocumented callback inferred or unknown; distinguishes evidence from authored examples. |
| “Here is a component inventory. No behavior is known.” | Produces a useful static explorer with no fabricated scenarios; playback is disabled. |
| “Show a proposed redesign and the current system.” | Uses clearly labeled perspectives and stable IDs; does not present proposed transfers as current facts. |
| “Update the existing explorer with this new evidence.” | Edits the JSON model, preserves IDs, updates sources and evidence, validates, and regenerates the HTML. |
| “The system has 400 services.” | Starts with the exploration question and a focused or nested overview; does not render a single unreadable wall of nodes. |
| “Just write a short paragraph about TCP.” | Does not invoke the explorer workflow unless interactive visualization is requested or materially useful. |

For each generated explorer check:

1. The intended question can be answered through inspection and scenario steps.
2. Every observed claim resolves to a source and every uncertain claim stays visible.
3. Events reference real relationships or entities and payloads are appropriately labeled.
4. Backward selection reconstructs state and scenario changes clear prior state.
5. Model text is displayed as text; model data cannot execute code.
6. The artifact and model remain usable without the original reference site.
7. Validation results and any untested interactions are accurately reported.
