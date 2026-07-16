Compress the entire available conversation/context into a durable working state. Read all context, not just recent turns.

## Objective

Create a compact handoff summary that preserves everything needed to resume the work accurately.

## Priority Rules

- Preserve lasting relevance over recency.
- Prefer compression over omission.
- Keep older context unless it is clearly irrelevant, explicitly superseded, or contradicted.
- When unsure, preserve the point in compressed form.
- If information conflicts, note the conflict and follow the most recent explicit correction.
- Do not invent missing information.
- Do not narrate your reasoning process.

## Preserve

Retain:

- Core goals, subgoals, and success criteria
- Important facts, background, terminology, definitions, and examples
- User constraints, preferences, assumptions, and required formats
- Decisions already made, including rationale when stated
- Open questions, unresolved threads, and pending next steps
- Corrections, reversals, rejected approaches, and superseded assumptions
- Durable lessons from exploration, failures, or debugging:
  - root causes
  - fixes
  - failed approaches
  - anti-patterns
  - reusable insights

## Drop or Compress Aggressively

- Conversational filler and acknowledgments
- Repetition
- Low-value back-and-forth
- Intermediate trial-and-error once the durable cause, fix, and lesson are captured
- Details that are no longer actionable or relevant

## Output Format

Use exactly these sections:

1. **Core objective** — one sentence.
2. **Key context** — durable facts, background, terminology, definitions, and examples.
3. **Constraints and preferences** — user requirements, assumptions, formats, and limits.
4. **Decisions made** — include rationale when stated.
5. **Lessons learned** — root causes, fixes, failed approaches, anti-patterns, and reusable insights.
6. **Open questions / unresolved items** — pending tasks, uncertainties, or follow-ups.
7. **Superseded or dropped context** — conflicts, replacements, and intentionally omitted details.
8. **Compressed working state** — minimal summary sufficient to resume work.

## Style

- Be terse but complete.
- Use bullets.
- Prefer precise fragments over prose.
- Preserve reusable state, not a transcript.
