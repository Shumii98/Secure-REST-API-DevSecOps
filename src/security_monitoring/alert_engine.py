from collections import Counter
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class SecurityAlertEngine:
    """Detects suspicious patterns in structured security events."""

    def __init__(self, events: list[dict[str, Any]]):
        self.events = events

    @staticmethod
    def _alert_id() -> str:
        """Generate a unique identifier for a security alert."""
        return f"ALT-{uuid4().hex[:12].upper()}"

    @staticmethod
    def _detected_at() -> str:
        """Return the alert detection timestamp in UTC."""
        return datetime.now(timezone.utc).isoformat()

    def detect_failed_login_burst(
        self,
        threshold: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Detect repeated failed logins from the same IP address.

        Returns one alert for each IP that reaches the threshold.
        """
        failed_logins = [
            event
            for event in self.events
            if event.get("message") == "login_failed"
        ]

        ip_counts = Counter(
            event.get("ip_address", "unknown")
            for event in failed_logins
        )

        alerts: list[dict[str, Any]] = []

        for ip_address, count in ip_counts.items():
            if count >= threshold:
                matching_events = [
                    event
                    for event in failed_logins
                    if event.get("ip_address", "unknown") == ip_address
                ]

                request_ids = sorted(
                    {
                        event["request_id"]
                        for event in matching_events
                        if event.get("request_id")
                    }
                )

                alerts.append(
                    {
                        "alert_id": self._alert_id(),
                        "alert_type": "AUTHENTICATION_FAILURE_BURST",
                        "rule": "failed_login_burst",
                        "severity": "HIGH",
                        "detected_at": self._detected_at(),
                        "source_ip": ip_address,
                        "event_count": count,
                        "request_ids": request_ids,
                        "description": (
                            f"{count} failed login attempts detected "
                            f"from {ip_address}"
                        ),
                    }
                )

        return alerts

    def detect_user_failures(
        self,
        threshold: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Detect repeated failed logins targeting the same username.
        """
        failed_logins = [
            event
            for event in self.events
            if event.get("message") == "login_failed"
        ]

        users: list[str] = []

        for event in failed_logins:
            detail = event.get("user") or event.get("detail", "")

            if detail:
                users.append(detail)

        user_counts = Counter(users)

        alerts: list[dict[str, Any]] = []

        for user, count in user_counts.items():
            if count >= threshold:
                matching_events = [
                    event
                    for event in failed_logins
                    if (event.get("user") or event.get("detail", "")) == user
                ]

                request_ids = sorted(
                    {
                        event["request_id"]
                        for event in matching_events
                        if event.get("request_id")
                    }
                )

                source_ips = sorted(
                    {
                        event["ip_address"]
                        for event in matching_events
                        if event.get("ip_address")
                    }
                )

                alerts.append(
                    {
                        "alert_id": self._alert_id(),
                        "alert_type": "TARGETED_ACCOUNT_FAILURE",
                        "rule": "targeted_account_failure",
                        "severity": "MEDIUM",
                        "detected_at": self._detected_at(),
                        "target": user,
                        "source_ips": source_ips,
                        "event_count": count,
                        "request_ids": request_ids,
                        "description": (
                            f"{count} failed authentication events "
                            f"associated with {user}"
                        ),
                    }
                )

        return alerts

    def generate_alerts(self) -> list[dict[str, Any]]:
        """Run all detection rules and return generated alerts."""
        alerts: list[dict[str, Any]] = []

        alerts.extend(self.detect_failed_login_burst())
        alerts.extend(self.detect_user_failures())

        return alerts