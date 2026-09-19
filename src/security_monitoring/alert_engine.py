from collections import Counter
from typing import Any


class SecurityAlertEngine:
    """Detects suspicious patterns in structured security events."""

    def __init__(self, events: list[dict[str, Any]]):
        self.events = events

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
                alerts.append(
                    {
                        "alert_type": "AUTHENTICATION_FAILURE_BURST",
                        "severity": "HIGH",
                        "source_ip": ip_address,
                        "event_count": count,
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

        users = []

        for event in failed_logins:
            detail = event.get("user") or event.get("detail", "")

            if detail:
                users.append(detail)

        user_counts = Counter(users)

        alerts: list[dict[str, Any]] = []

        for user, count in user_counts.items():
            if count >= threshold:
                alerts.append(
                    {
                        "alert_type": "TARGETED_ACCOUNT_FAILURE",
                        "severity": "MEDIUM",
                        "target": user,
                        "event_count": count,
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