from pathlib import Path

from src.security_monitoring.alert_engine import SecurityAlertEngine
from src.security_monitoring.log_parser import SecurityLogParser
from src.security_monitoring.report_generator import SecurityReportGenerator


def run_monitoring() -> Path:
    """Run the complete security monitoring pipeline."""

    log_file = Path("logs/security.log")

    parser = SecurityLogParser(log_file)
    events = parser.read_events()

    alert_engine = SecurityAlertEngine(events)
    alerts = alert_engine.generate_alerts()

    report_generator = SecurityReportGenerator()
    report_path = report_generator.generate_json_report(
        events=events,
        alerts=alerts,
    )

    print("Security monitoring completed.")
    print(f"Events analyzed: {len(events)}")
    print(f"Alerts generated: {len(alerts)}")
    print(f"Report generated: {report_path}")

    return report_path


if __name__ == "__main__":
    run_monitoring()