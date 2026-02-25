# TASKS & RUBRICS GUIDE

## OVERVIEW
Defines the benchmarks. Tasks are JSON files combining a prompt, a gold response (reference), and a rubric for grading.

## STRUCTURE
```
tasks/
├── types.py            # Pydantic models: Task, Rubric
├── helpers.py          # Loader: load_tasks(dir)
├── examples/           # Simple/Factual tasks (no world)
└── worlds/             # Agentic tasks (requires World server)
```

## TASK FORMAT
```json
{
  "id": "uuid",
  "domain": "category",
  "prompt": "Action + Output Format",
  "gold_response": "Expected summary (reference for judge)",
  "rubric": [
    { "criteria": "Did it find X?" },
    { "criteria": "Did it delete Y?" },
    { "criteria": "Did it report Z?" }
  ]
}
```

## WRITING RULES
- **Scope**: Be specific ("emails in spam", not "emails").
- **Output**: MANDATE output format in prompt ("Return JSON list...").
- **Verifiability**: Judge sees **ONLY** agent response. Agent must **STATE** what it did.
- **Gold Response**: Write what a *perfect* agent would say.

## ANTI-PATTERNS
- **Vague Prompts**: "Fix the issue" (Bad) vs "Find error in X and fix it" (Good).
- **Hidden State Rubrics**: "Database has row X" (Judge can't see DB).
- **Over-constrained**: "Use tool X" (Let agent decide strategy).
