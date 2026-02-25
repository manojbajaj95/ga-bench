"""Todo application — dummy MCP server exposing todo tools."""

from __future__ import annotations

from datetime import datetime

from fastmcp import FastMCP

from worlds.utils import load_seed_data


class TodoApp:
    """Dummy todo application providing tools to manage tasks."""

    def __init__(self) -> None:
        self.name = "todo"
        self.data = load_seed_data("todo")
        self._tasks: dict[str, dict] = self.data["_TASKS"]

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    def list_tasks(
        self,
        project: str | None = None,
        status: str | None = None,
        priority: str | None = None,
    ) -> list[dict]:
        """List tasks with optional filtering.

        Args:
            project: Filter by project name (e.g., Engineering, Marketing).
            status: Filter by status (pending, in_progress, completed).
            priority: Filter by priority (low, medium, high).

        Returns:
            list[dict]: List of task dicts.

        Tags:
            todo, list, tasks, filter
        """
        results = list(self._tasks.values())
        if project:
            results = [t for t in results if t["project"].lower() == project.lower()]
        if status:
            results = [t for t in results if t["status"].lower() == status.lower()]
        if priority:
            results = [t for t in results if t["priority"].lower() == priority.lower()]

        # Sort by due_date (handling potential template strings if necessary, but usually they are resolved)
        results.sort(key=lambda t: t.get("due_date", ""))
        return results

    def get_task(self, task_id: str) -> dict:
        """Retrieve a single task by its ID.

        Args:
            task_id: The unique ID of the task.

        Returns:
            dict: Full task dict or an error dict if not found.

        Tags:
            todo, get, task, detail
        """
        task = self._tasks.get(task_id)
        if task is None:
            return {"error": f"Task '{task_id}' not found."}
        return dict(task)

    def create_task(
        self,
        title: str,
        project: str,
        priority: str = "medium",
        due_date: str | None = None,
        status: str = "pending",
    ) -> dict:
        """Create a new task.

        Args:
            title: Task title.
            project: Project name.
            priority: Task priority (low, medium, high).
            due_date: Optional due date (ISO format).
            status: Initial status (default 'pending').

        Returns:
            dict: Confirmation with the newly created task id.

        Tags:
            todo, create, task, add
        """
        task_id = f"t{len(self._tasks) + 1:03d}"
        # Ensure unique ID if tXXX already exists
        while task_id in self._tasks:
            task_id = f"t{int(task_id[1:]) + 1:03d}"

        new_task = {
            "id": task_id,
            "title": title,
            "project": project,
            "priority": priority,
            "due_date": due_date or datetime.now().isoformat(),
            "status": status,
        }
        self._tasks[task_id] = new_task
        return {"id": task_id, "status": "created", "task": new_task}

    def update_task(
        self,
        task_id: str,
        title: str | None = None,
        status: str | None = None,
        project: str | None = None,
        priority: str | None = None,
        due_date: str | None = None,
    ) -> dict:
        """Update an existing task.

        Args:
            task_id: The unique ID of the task to update.
            title: New title.
            status: New status (pending, in_progress, completed).
            project: New project name.
            priority: New priority (low, medium, high).
            due_date: New due date (ISO format).

        Returns:
            dict: Updated task or error dict.

        Tags:
            todo, update, task, status
        """
        task = self._tasks.get(task_id)
        if task is None:
            return {"error": f"Task '{task_id}' not found."}

        if title is not None:
            task["title"] = title
        if status is not None:
            task["status"] = status
        if project is not None:
            task["project"] = project
        if priority is not None:
            task["priority"] = priority
        if due_date is not None:
            task["due_date"] = due_date

        return {"id": task_id, "status": "updated", "task": task}

    # ------------------------------------------------------------------

    def list_tools(self) -> list:
        """Return all tool methods exposed by this application.

        Returns:
            list: Callable tool methods.
        """
        return [
            self.list_tasks,
            self.get_task,
            self.create_task,
            self.update_task,
        ]

    def create_mcp_server(self) -> FastMCP:
        """Create and return a FastMCP server with all tools registered."""
        mcp = FastMCP(self.name)
        for tool_fn in self.list_tools():
            mcp.tool()(tool_fn)
        return mcp


if __name__ == "__main__":
    app = TodoApp()
    server = app.create_mcp_server()
    server.run()
