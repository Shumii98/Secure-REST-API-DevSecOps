import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SecurityReportGenerator:
    """Generates machine-readable SOC security reports."""

    def __init__(self, output_dir: str | Path = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_json_report(
        self,
        events: list[dict[str, Any]],
        alerts: list[dict[str, Any]],
    ) -> Path:
        """Generate a JSON security monitoring report."""

        severity_counts: dict[str, int] = {}

        for alert in alerts:
            severity = alert.get("severity", "UNKNOWN")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_events": len(events),
                "total_alerts": len(alerts),
                "alerts_by_severity": severity_counts,
            },
            "alerts": alerts,
        }

        output_file = self.output_dir / "security_report.json"

        with output_file.open("w", encoding="utf-8") as file:
            json.dump(report, file, indent=2)

        return output_file