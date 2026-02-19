import json
import os
from pathlib import Path

from langchain.chat_models import init_chat_model
from loguru import logger
from pydantic import BaseModel

from agents.types import TokenUsage
from .types import EvalResult, FinalSummary, JudgmentResult, TaskGrade

JUDGE_PROMPT = """\
You are an expert evaluator. Judge whether the agent's response satisfies the following criterion.

Criterion: {criterion}

Question asked to the agent:
{question}

Agent's response:
{response}

Reference (gold) answer:
{reference}

Return score=true if the criterion is satisfied, false otherwise. Explain your reasoning briefly.
"""

_JUDGE_MODEL = os.getenv("JUDGE_MODEL", "anthropic:claude-haiku-4-5-20251001")


class _JudgeOutput(BaseModel):
    reasoning: str
    score: bool


def llm_as_judge(
    prompt: str,
    agent_output: str,
    rubric: list[str],
    gold_response: str = "",
) -> EvalResult:
    """Evaluate agent_output against each rubric criterion using an LLM judge."""
    model = init_chat_model(_JUDGE_MODEL).with_structured_output(
        _JudgeOutput, include_raw=True
    )

    judgments = []
    for criterion in rubric:
        logger.debug("Judging criterion: {}", criterion[:80])
        content = JUDGE_PROMPT.format(
            criterion=criterion,
            question=prompt,
            response=agent_output,
            reference=gold_response,
        )
        result = model.invoke([{"role": "user", "content": content}])
        parsed: _JudgeOutput = result["parsed"]
        mark = "PASS" if parsed.score else "FAIL"
        logger.info("[{}] {}", mark, criterion[:80])
        judgments.append(JudgmentResult(
            criterion=criterion,
            score=parsed.score,
            comment=parsed.reasoning,
        ))

    return EvalResult(
        judgments=judgments,
        passed=sum(1 for j in judgments if j.score),
        total=len(judgments),
    )


def evaluate_run(run_id: str, output_base: str = "output") -> None:
    """Evaluate all tasks in a run, then write grades.json and final.json."""
    run_dir = Path(output_base) / run_id
    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")

    _SKIP = {"manifest.json", "grades.json", "final.json"}
    task_files = sorted(
        f for f in run_dir.glob("*.json")
        if f.name not in _SKIP and not f.name.endswith(".eval.json")
    )

    logger.info("Evaluating run: {}", run_id)
    logger.info("Tasks to evaluate: {}", len(task_files))

    grades: list[TaskGrade] = []

    for i, task_file in enumerate(task_files, 1):
        task_result = json.loads(task_file.read_text())
        logger.info("Task {}/{} [{}]: {}", i, len(task_files), task_result["domain"], task_result["prompt"][:80])

        eval_result = llm_as_judge(
            prompt=task_result["prompt"],
            agent_output=task_result["agent_response"],
            rubric=task_result["rubric"],
            gold_response=task_result["gold_response"],
        )

        # Save per-task eval
        eval_file = run_dir / f"{task_result['task_id']}.eval.json"
        eval_file.write_text(json.dumps({
            "task_id": task_result["task_id"],
            **eval_result.model_dump(),
        }, indent=2))

        score = eval_result.passed / eval_result.total if eval_result.total else 0.0
        usage = TokenUsage(**task_result["token_usage"])
        grades.append(TaskGrade(
            task_id=task_result["task_id"],
            domain=task_result["domain"],
            prompt=task_result["prompt"],
            score=score,
            passed=eval_result.passed,
            total=eval_result.total,
            token_usage=usage,
            time_taken=task_result["time_taken"],
        ))
        logger.success("Task scored {:.0%} ({}/{})", score, eval_result.passed, eval_result.total)

    # grades.json
    grades_file = run_dir / "grades.json"
    grades_file.write_text(json.dumps(
        {"run_id": run_id, "grades": [g.model_dump() for g in grades]},
        indent=2,
    ))

    # final.json
    n = len(grades)
    total_input = sum(g.token_usage.input_tokens for g in grades)
    total_output = sum(g.token_usage.output_tokens for g in grades)
    total_tokens = sum(g.token_usage.total_tokens for g in grades)

    final = FinalSummary(
        run_id=run_id,
        num_tasks=n,
        avg_score=round(sum(g.score for g in grades) / n, 4) if n else 0.0,
        avg_time_taken=round(sum(g.time_taken for g in grades) / n, 3) if n else 0.0,
        total_token_usage=TokenUsage(
            input_tokens=total_input,
            output_tokens=total_output,
            total_tokens=total_tokens,
        ),
        avg_token_usage=TokenUsage(
            input_tokens=round(total_input / n) if n else 0,
            output_tokens=round(total_output / n) if n else 0,
            total_tokens=round(total_tokens / n) if n else 0,
        ),
    )
    (run_dir / "final.json").write_text(final.model_dump_json(indent=2))

    logger.success(
        "Score: {:.0%}  ({}/{} criteria passed)",
        final.avg_score,
        sum(g.passed for g in grades),
        sum(g.total for g in grades),
    )
    logger.info("Tokens: {} total  ({} in / {} out)", total_tokens, total_input, total_output)
    logger.info("Time:   {}s avg per task", final.avg_time_taken)
    logger.info("Results: {}/", run_dir)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m evaluator.evaluate <run_id>")
        sys.exit(1)
    evaluate_run(sys.argv[1])
