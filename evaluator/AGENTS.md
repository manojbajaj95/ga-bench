# EVALUATOR GUIDE

## OVERVIEW
Implements LLM-as-a-Judge to grade agent runs based on task rubrics.

## STRUCTURE
```
evaluator/
├── evaluate.py         # Main entry point & logic
└── types.py            # Result models
```

## PROCESS
1. **Read**: Loads agent output from `output/<run_id>/<task>.json`.
2. **Judge**: Calls LLM (`JUDGE_MODEL`) with:
   - Task Prompt
   - Gold Response
   - Agent Response
   - Rubric Criteria
3. **Score**: Binary (Pass/Fail) per criterion.
4. **Report**: Generates `grades.json` and `final.json`.

## CONFIGURATION
- **Model**: `JUDGE_MODEL` in `.env`.
- **Reasoning**: Judge must provide reasoning for every score.

## ANTI-PATTERNS
- **Manual Grading**: Evaluation should be fully automated.
- **Complex logic**: Keep judge logic simple; complexity belongs in the prompt/rubric.
