# Decision-Ready Analysis Patterns

Use this reference only when the skill being authored will produce metrics, dashboards, analytical summaries, experiments, or stakeholder-facing reports.

## Core Principle

Analysis without a decision is just arithmetic.

Design the skill so it answers:

1. What decision is this analysis supporting?
2. What would change if the answer is X versus Y?
3. What metric definition or comparison contract must be locked first?

## Metric Contract Pattern

Before a skill computes or summarizes a KPI, capture:

1. Business question
2. Entity and grain
3. Numerator
4. Denominator
5. Filters and exclusions
6. Time window and timezone
7. Source of truth
8. Known caveats

If the skill automates metrics without these fields, it should explicitly surface ambiguity instead of pretending precision.

## Chart Selection Pattern

Choose visuals by question:

- trend -> line chart
- ranked comparison -> sorted bar chart
- distribution -> histogram or box plot
- relationship -> scatter plot
- funnel -> funnel chart
- cohort retention -> cohort heatmap or table

Teach the skill to reject decorative charts that do not change the decision.

## Decision Brief Pattern

When the output is stakeholder facing, prefer this structure:

1. Decision question
2. Short answer
3. Evidence with baseline
4. Confidence and why
5. Caveats
6. Recommended next action

This keeps report-oriented skills from dumping raw computations without a usable conclusion.

## Analytical Pitfalls Worth Encoding

- changing KPI definitions across periods
- comparing unequal windows
- showing percentages without counts
- post-hoc segment hunting
- causal claims from observational data
- failing to quantify uncertainty

When relevant, store these as a checklist in `references/` rather than bloating `SKILL.md`.
