import json
from pathlib import Path
from .types import Task, Rubric


def create_task(
    domain: str,
    prompt: str,
    gold_response: str,
    rubric: list[str | Rubric],
    task_id: str | None = None,
) -> Task:
    rubric_items = [
        Rubric(criteria=r) if isinstance(r, str) else r for r in rubric
    ]
    kwargs = dict(domain=domain, prompt=prompt, gold_response=gold_response, rubric=rubric_items)
    if task_id is not None:
        kwargs["id"] = task_id
    return Task(**kwargs)


def save_task(task: Task, path: str | Path) -> None:
    Path(path).write_text(task.model_dump_json(indent=2))


def load_task(path: str | Path) -> Task:
    return Task.model_validate_json(Path(path).read_text())


def load_tasks(directory: str | Path) -> list[Task]:
    directory = Path(directory)
    tasks = []
    for file in sorted(directory.glob("*.json")):
        tasks.append(load_task(file))
    return tasks
