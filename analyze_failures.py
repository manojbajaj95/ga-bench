#!/usr/bin/env python3
"""Extract and analyze failed evaluations from a benchmark run."""

import json
import sys
from pathlib import Path


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def analyze_failure(eval_path: Path, task_id: str) -> dict:
    """Analyze a single failed evaluation to determine the failure type."""
    eval_data = load_json(eval_path)
    
    judgments = eval_data.get("judgments", [])
    
    # Check if all criteria failed (potential wrong failure)
    all_failed = all(j.get("score") == False for j in judgments)
    some_passed = any(j.get("score") == True for j in judgments)
    
    analysis = {
        "task_id": task_id,
        "passed": eval_data.get("passed", 0),
        "total": eval_data.get("total", 0),
        "failure_type": None,
        "reason": None,
        "criteria_analysis": []
    }
    
    for j in judgments:
        criterion = j.get("criterion", "")
        score = j.get("score", False)
        comment = j.get("comment", "")
        
        analysis["criteria_analysis"].append({
            "criterion": criterion[:100] + "..." if len(criterion) > 100 else criterion,
            "passed": score,
            "comment": comment
        })
    
    # Analyze failure patterns
    if all_failed and not some_passed:
        # Check for common wrong failure patterns
        failure_patterns = {
            "data_not_found": ["could not find", "not found", "failed to locate", "does not exist", "no such"],
            "tool_error": ["error", "failed", "exception", "timeout"],
            "empty_response": ["empty", "no content", "no data"],
            "wrong_attribution": ["incorrectly", "wrong", "misattributed"],
        }
        
        all_comments = " ".join(j.get("comment", "").lower() for j in judgments)
        
        if any(pattern in all_comments for pattern in failure_patterns["data_not_found"]):
            analysis["failure_type"] = "INCORRECT_FAILURE"
            analysis["reason"] = "Agent reports data not found, but data exists in seed"
        elif any(pattern in all_comments for pattern in failure_patterns["tool_error"]):
            analysis["failure_type"] = "ACTUAL_FAILURE"
            analysis["reason"] = "Tool/API error prevented task completion"
        else:
            analysis["failure_type"] = "NEEDS_REVIEW"
            analysis["reason"] = "Ambiguous failure pattern"
    else:
        analysis["failure_type"] = "ACTUAL_FAILURE"
        analysis["reason"] = "Partial failure - some criteria passed, some failed"
    
    return analysis


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_failures.py <run_id>")
        print("Example: python analyze_failures.py bf7467e8-ffb6-4601-84b7-449ee89c676b")
        sys.exit(1)
    
    run_id = sys.argv[1]
    run_dir = Path("output") / run_id
    
    if not run_dir.exists():
        print(f"Error: Run directory not found: {run_dir}")
        sys.exit(1)
    
    # Load grades
    grades_path = run_dir / "grades.json"
    if not grades_path.exists():
        print(f"Error: grades.json not found: {grades_path}")
        sys.exit(1)
    
    grades = load_json(grades_path)
    
    # Find failed evaluations
    failed_tasks = []
    for grade in grades.get("grades", []):
        task_id = grade["task_id"]
        score = grade.get("score", 0)
        total = grade.get("total", 0)
        passed = grade.get("passed", 0)
        
        if passed < total:
            eval_path = run_dir / f"{task_id}.eval.json"
            if eval_path.exists():
                analysis = analyze_failure(eval_path, task_id)
                analysis["domain"] = grade.get("domain", "unknown")
                analysis["prompt"] = grade.get("prompt", "")[:200] + "..."
                analysis["score"] = score
                analysis["passed_count"] = passed
                analysis["total_count"] = total
                failed_tasks.append(analysis)
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"FAILURE ANALYSIS FOR RUN: {run_id}")
    print(f"{'='*80}\n")
    
    actual_failures = []
    incorrect_failures = []
    needs_review = []
    
    for task in failed_tasks:
        if task["failure_type"] == "ACTUAL_FAILURE":
            actual_failures.append(task)
        elif task["failure_type"] == "INCORRECT_FAILURE":
            incorrect_failures.append(task)
        else:
            needs_review.append(task)
    
    print(f"Summary:")
    print(f"  Total Failed: {len(failed_tasks)}")
    print(f"  Actual Failures: {len(actual_failures)}")
    print(f"  Incorrect Failures: {len(incorrect_failures)}")
    print(f"  Needs Review: {len(needs_review)}\n")
    
    # Print incorrect failures first (most important)
    if incorrect_failures:
        print(f"{'='*80}")
        print("INCORRECT FAILURES (Agent did nothing wrong - task/data/eval issue)")
        print(f"{'='*80}\n")
        
        for task in incorrect_failures:
            print(f"Task ID: {task['task_id']}")
            print(f"Domain: {task['domain']}")
            print(f"Score: {task['score']} ({task['passed_count']}/{task['total_count']})")
            print(f"Reason: {task['reason']}")
            print(f"Prompt: {task['prompt'][:150]}...")
            print(f"\nCriteria:")
            for c in task["criteria_analysis"]:
                status = "✓ PASS" if c["passed"] else "✗ FAIL"
                print(f"  {status}: {c['criterion']}")
                if not c["passed"]:
                    print(f"    Comment: {c['comment'][:200]}...")
            print(f"\n{'-'*40}\n")
    
    # Print actual failures
    if actual_failures:
        print(f"{'='*80}")
        print("ACTUAL FAILURES (Agent failed to complete task correctly)")
        print(f"{'='*80}\n")
        
        for task in actual_failures[:10]:  # Limit output
            print(f"Task ID: {task['task_id']}")
            print(f"Domain: {task['domain']}")
            print(f"Score: {task['score']} ({task['passed_count']}/{task['total_count']})")
            print(f"Prompt: {task['prompt'][:150]}...")
            print(f"\n{'-'*40}\n")
        
        if len(actual_failures) > 10:
            print(f"... and {len(actual_failures) - 10} more actual failures\n")
    
    # Print needs review
    if needs_review:
        print(f"{'='*80}")
        print("NEEDS REVIEW (Ambiguous - requires manual check)")
        print(f"{'='*80}\n")
        
        for task in needs_review:
            print(f"Task ID: {task['task_id']}")
            print(f"Domain: {task['domain']}")
            print(f"Reason: {task['reason']}")
            print(f"\n{'-'*40}\n")
    
    # Output JSON for programmatic use
    output = {
        "run_id": run_id,
        "summary": {
            "total_failed": len(failed_tasks),
            "actual_failures": len(actual_failures),
            "incorrect_failures": len(incorrect_failures),
            "needs_review": len(needs_review),
        },
        "incorrect_failures": incorrect_failures,
        "actual_failures": actual_failures,
        "needs_review": needs_review,
    }
    
    json_path = run_dir / "failure_analysis.json"
    with open(json_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nDetailed analysis saved to: {json_path}")


if __name__ == "__main__":
    main()
