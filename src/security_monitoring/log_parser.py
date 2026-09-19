import json
from pathlib import Path
from typing import Any


class SecurityLogParser:
    """Parses structured JSON security logs."""

    def __init__(self, log_file: str | Path):
        self.log_file = Path(log_file)

    def read_events(self) -> list[dict[str, Any]]:
        """Read valid JSON log entries from the security log."""
        if not self.log_file.exists():
            return []

        events: list[dict[str, Any]] = []

        with self.log_file.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if not line:
                    continue

                try:
                    event = json.loads(line)

                    if isinstance(event, dict):
                        events.append(event)

                except json.JSONDecodeError:
                    continue

        return events

    def get_event_counts(self) -> dict[str, int]:
        """Return the number of occurrences for each security event."""
        counts: dict[str, int] = {}

        for event in self.read_events():
            message = event.get("message", "unknown")
            counts[message] = counts.get(message, 0) + 1

        return counts

    def get_failed_logins(self) -> list[dict[str, Any]]:
        """Return failed login events."""
        return [
            event
            for event in self.read_events()
            if event.get("message") == "login_failed"
        ]

    def get_events_by_request_id(
        self, request_id: str
    ) -> list[dict[str, Any]]:
        """Return all events associated with a request ID."""
        return [
            event
            for event in self.read_events()
            if event.get("request_id") == request_id
        ]