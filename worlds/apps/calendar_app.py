"""Calendar application — dummy MCP server exposing calendar tools."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from fastmcp import FastMCP

from worlds.utils import load_seed_data


class CalendarApp:
    """Dummy calendar application providing tools to manage calendar events."""

    def __init__(self) -> None:
        self.name = "calendar"
        self.data = load_seed_data("calendar")
        self._events: dict[str, dict] = dict(self.data["_EVENTS"])

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    def list_events(
        self,
        calendar: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict]:
        """List calendar events, optionally filtered by calendar or date range.

        Args:
            calendar: Calendar name to filter by (work, personal). None returns all.
            start_date: ISO datetime string; only return events starting at or after this time.
            end_date: ISO datetime string; only return events starting before this time.

        Returns:
            list[dict]: Events sorted by start time (without description).

        Tags:
            calendar, list, events, schedule, view
        """
        results = []
        for ev in self._events.values():
            if calendar and ev["calendar"] != calendar:
                continue
            if start_date and ev["start"] < start_date:
                continue
            if end_date and ev["start"] >= end_date:
                continue
            results.append({k: v for k, v in ev.items() if k != "description"})
        results.sort(key=lambda e: e["start"])
        return results

    def get_event(self, event_id: str) -> dict:
        """Get full details of a calendar event including description.

        Args:
            event_id: The unique ID of the event.

        Returns:
            dict: Full event dict or error dict if not found.

        Tags:
            calendar, get, event, detail, view
        """
        ev = self._events.get(event_id)
        if ev is None:
            return {"error": f"Event '{event_id}' not found."}
        return dict(ev)

    def create_event(
        self,
        title: str,
        start: str,
        end: str,
        attendees: list[str] | None = None,
        description: str = "",
        calendar: Literal["work", "personal"] = "work",
    ) -> dict:
        """Create a new calendar event.

        Args:
            title: Event title.
            start: Start time as ISO datetime string (e.g. '2026-02-23T10:00:00').
            end: End time as ISO datetime string.
            attendees: List of attendee email addresses.
            description: Optional event description.
            calendar: Calendar to add the event to ('work' or 'personal').

        Returns:
            dict: The newly created event.

        Tags:
            calendar, create, event, schedule, add
        """
        event_id = str(uuid.uuid4())[:8]
        event = {
            "id": event_id,
            "title": title,
            "start": start,
            "end": end,
            "attendees": attendees or [],
            "description": description,
            "calendar": calendar,
            "status": "confirmed",
        }
        self._events[event_id] = event
        return dict(event)

    def update_event(
        self,
        event_id: str,
        title: str | None = None,
        start: str | None = None,
        end: str | None = None,
        description: str | None = None,
        status: Literal["confirmed", "tentative", "cancelled"] | None = None,
    ) -> dict:
        """Update fields on an existing calendar event.

        Args:
            event_id: The unique ID of the event to update.
            title: New title, or None to leave unchanged.
            start: New start time (ISO string), or None to leave unchanged.
            end: New end time (ISO string), or None to leave unchanged.
            description: New description, or None to leave unchanged.
            status: New status (confirmed, tentative, cancelled), or None to leave unchanged.

        Returns:
            dict: Updated event or error dict.

        Tags:
            calendar, update, edit, event, modify
        """
        ev = self._events.get(event_id)
        if ev is None:
            return {"error": f"Event '{event_id}' not found."}
        if title is not None:
            ev["title"] = title
        if start is not None:
            ev["start"] = start
        if end is not None:
            ev["end"] = end
        if description is not None:
            ev["description"] = description
        if status is not None:
            ev["status"] = status
        return dict(ev)

    def delete_event(self, event_id: str) -> dict:
        """Permanently delete a calendar event.

        Args:
            event_id: The unique ID of the event to delete.

        Returns:
            dict: Confirmation with deleted event title, or error dict.

        Tags:
            calendar, delete, remove, event, cancel
        """
        ev = self._events.pop(event_id, None)
        if ev is None:
            return {"error": f"Event '{event_id}' not found."}
        return {"id": event_id, "title": ev["title"], "status": "deleted"}

    def search_events(self, query: str) -> list[dict]:
        """Search events by keyword in title or description (case-insensitive).

        Args:
            query: Search string matched against title and description.

        Returns:
            list[dict]: Matching events sorted by start time (without description).

        Tags:
            calendar, search, find, query, filter
        """
        q = query.lower()
        results = [
            {k: v for k, v in ev.items() if k != "description"}
            for ev in self._events.values()
            if q in ev["title"].lower() or q in ev["description"].lower()
        ]
        results.sort(key=lambda e: e["start"])
        return results

    def get_free_slots(self, date: str, duration_minutes: int = 60) -> list[dict]:
        """Find free time slots on a given day within working hours (9am–6pm).

        Args:
            date: Date to check in YYYY-MM-DD format.
            duration_minutes: Minimum slot length required in minutes (default 60).

        Returns:
            list[dict]: Free slots as dicts with 'start' and 'end' ISO strings.

        Tags:
            calendar, free, slots, availability, schedule
        """
        day_start = datetime.fromisoformat(f"{date}T09:00:00")
        day_end = datetime.fromisoformat(f"{date}T18:00:00")

        busy = sorted(
            [
                (datetime.fromisoformat(ev["start"]), datetime.fromisoformat(ev["end"]))
                for ev in self._events.values()
                if ev["start"].startswith(date)
            ],
            key=lambda x: x[0],
        )

        slots = []
        cursor = day_start
        for b_start, b_end in busy:
            if b_start > cursor:
                gap_minutes = (b_start - cursor).seconds // 60
                if gap_minutes >= duration_minutes:
                    slots.append({"start": cursor.isoformat(), "end": b_start.isoformat()})
            cursor = max(cursor, b_end)
        if cursor < day_end:
            gap_minutes = (day_end - cursor).seconds // 60
            if gap_minutes >= duration_minutes:
                slots.append({"start": cursor.isoformat(), "end": day_end.isoformat()})
        return slots

    def list_calendars(self) -> list[dict]:
        """List all calendars with event counts.

        Returns:
            list[dict]: Each entry has calendar name and total event count.

        Tags:
            calendar, list, calendars, summary
        """
        counts: dict[str, int] = {}
        for ev in self._events.values():
            counts[ev["calendar"]] = counts.get(ev["calendar"], 0) + 1
        return [{"calendar": name, "total": count} for name, count in sorted(counts.items())]

    # ------------------------------------------------------------------

    def list_tools(self) -> list:
        """Return all tool methods exposed by this application.

        Returns:
            list: Callable tool methods.
        """
        return [
            self.list_events,
            self.get_event,
            self.create_event,
            self.update_event,
            self.delete_event,
            self.search_events,
            self.get_free_slots,
            self.list_calendars,
        ]

    def create_mcp_server(self) -> FastMCP:
        """Create and return a FastMCP server with all tools registered."""
        mcp = FastMCP(self.name)
        for tool_fn in self.list_tools():
            mcp.tool()(tool_fn)
        return mcp


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = CalendarApp()
    server = app.create_mcp_server()
    server.run()
