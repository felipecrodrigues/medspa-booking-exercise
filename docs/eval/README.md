# Agent quality evaluation

## Purpose and scope

This directory stores one evidence-linked evaluation record per agent run as JSON Lines (JSONL). The format follows the run, quality-dimension, metric-observation, and evidence concepts in `docs/ontology/extensions/exercise-evaluation.ttl`. Each record assesses the agent's **input** and **output**; it is not an implementation score unless the evaluated run actually implemented something.

The initial contract is **schema version `1.0`** and **rubric version `1.0`**. Increment the schema version for incompatible record-shape changes and the rubric version when rating definitions or anchors change. Keep existing records intact; append one record per run.

## Rating rubric (version 1.0)

Rate every listed dimension with an integer from 1 to 5. Apply these anchors consistently to each dimension, interpreting the evidence in light of that dimension's definition:

| Score | Anchor |
|---|---|
| 1 | Unusable or materially wrong; fails the dimension's purpose. |
| 2 | Weak; substantial errors or omissions require major correction. |
| 3 | Usable but has material gaps that require meaningful follow-up. |
| 4 | Strong; accurate and useful with only minor gaps. |
| 5 | Accurate, complete, actionable, and evidence-grounded for the dimension; no material gaps. |

### Input dimensions

- `objective_acceptance_clarity`: Is the task goal, expected result, and success criteria clear?
- `context_constraint_completeness`: Does the input provide or identify the relevant context, sources, constraints, and boundaries?
- `actionability`: Can the agent proceed usefully from the requested steps and available references without guessing at material instructions?

### Output dimensions

- `correctness_grounding`: Is the result accurate against the supplied task and authoritative evidence, without unsupported claims?
- `requirement_coverage`: Does it address the requested deliverables and constraints, including explicit exclusions?
- `actionability`: Is the result specific and usable for the next intended step?
- `uncertainty_evidence_handling`: Does it distinguish facts from assumptions, surface uncertainty, and connect judgments to evidence?

Score each dimension independently. Set each overall input/output score to the unweighted arithmetic mean of that rating's dimension scores, rounded to one decimal place (round half up). Include an overall rationale explaining the score and its main strengths or limitations; dimension rationales do not replace it. A strong overall mean must not conceal a material issue: describe such issues in the relevant dimension and overall rationale.

## JSONL record contract

Each non-empty line in `agent-quality.jsonl` is exactly one JSON object. Do not wrap records in an array or include comments. Required fields:

| Field | Meaning |
|---|---|
| `schema_version`, `rubric_version` | Version strings for this record shape and rating definitions. |
| `run_id` | Stable, unique identifier for this agent run. |
| `role`, `phase` | The agent's assigned role and the phase it performed (for example, `PLAN` and `planning`). |
| `model`, `variant` | Exact provider/model identifier and configured variant. Use JSON `null` when the value is unknown or unobserved; do not guess. |
| `evidence.session_id` | OpenChamber session containing the evaluated run. |
| `evidence.input_message_id`, `evidence.output_message_id` | OpenChamber message IDs for the exact input prompt and evaluated output. |
| `ratings.input`, `ratings.output` | Rating objects with an `overall_score`, an `overall_rationale`, and a `dimensions` object containing every applicable dimension. |
| Dimension entry | An integer `score`, a concise evidence-based `rationale`, and an `evidence` array of references/observations supporting the judgment. Cite message IDs and, where useful, repository paths/sections or test/command artifacts. |
| `unavailable_metrics` | Array of unavailable metric objects. Each has a `name`, a JSON `value` of `null`, and a specific `reason`. Use an empty array only when no expected metrics are unavailable. |

Never infer token counts, costs, or latency. When they were not observed, include each applicable metric in `unavailable_metrics` with `value: null` and explain why it is unavailable. Use explicit units in metric names where relevant (for example, `cost_usd` or `latency_ms`).

For schema version 1.0, `evidence.input_message_id` identifies the initial task prompt. If the run also received follow-up steering prompts, keep this primary field unchanged and cite each relevant follow-up message ID in the `evidence` array of the applicable input-dimension rating(s). This preserves the record shape while retaining provenance for the complete input.

Before appending, confirm the record has all required dimension ratings and evidence, model/variant unknowns are `null` rather than invented, and unavailable metrics include reasons. Validate that the file parses as JSONL (one valid JSON object per line).
