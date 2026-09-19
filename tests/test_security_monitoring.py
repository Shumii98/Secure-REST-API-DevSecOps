import json

from src.security_monitoring.alert_engine import SecurityAlertEngine
from src.security_monitoring.log_parser import SecurityLogParser
from src.security_monitoring.report_generator import SecurityReportGenerator


def test_failed_login_burst_detection():
    events = [
        {
            "message": "login_failed",
            "ip_address": "192.168.1.10",
            "request_id": "REQ-001",
        },
        {
            "message": "login_failed",
            "ip_address": "192.168.1.10",
            "request_id": "REQ-002",
        },
        {
            "message": "login_failed",
            "ip_address": "192.168.1.10",
            "request_id": "REQ-003",
        },
        {
            "message": "login_failed",
            "ip_address": "192.168.1.10",
            "request_id": "REQ-004",
        },
        {
            "message": "login_failed",
            "ip_address": "192.168.1.10",
            "request_id": "REQ-005",
        },
    ]

    engine = SecurityAlertEngine(events)
    alerts = engine.detect_failed_login_burst(threshold=5)

    assert len(alerts) == 1
    assert alerts[0]["alert_type"] == "AUTHENTICATION_FAILURE_BURST"
    assert alerts[0]["severity"] == "HIGH"
    assert alerts[0]["source_ip"] == "192.168.1.10"
    assert alerts[0]["event_count"] == 5
    assert len(alerts[0]["request_ids"]) == 5


def test_targeted_account_failure_detection():
    events = [
        {
            "message": "login_failed",
            "user": "admin",
            "ip_address": "10.0.0.5",
            "request_id": "REQ-101",
        },
        {
            "message": "login_failed",
            "user": "admin",
            "ip_address": "10.0.0.6",
            "request_id": "REQ-102",
        },
        {
            "message": "login_failed",
            "user": "admin",
            "ip_address": "10.0.0.7",
            "request_id": "REQ-103",
        },
    ]

    engine = SecurityAlertEngine(events)
    alerts = engine.detect_user_failures(threshold=3)

    assert len(alerts) == 1
    assert alerts[0]["alert_type"] == "TARGETED_ACCOUNT_FAILURE"
    assert alerts[0]["severity"] == "MEDIUM"
    assert alerts[0]["target"] == "admin"
    assert alerts[0]["event_count"] == 3
    assert len(alerts[0]["source_ips"]) == 3
    assert len(alerts[0]["request_ids"]) == 3


def test_no_alert_below_threshold():
    events = [
        {
            "message": "login_failed",
            "ip_address": "192.168.1.20",
            "request_id": "REQ-201",
        },
        {
            "message": "login_failed",
            "ip_address": "192.168.1.20",
            "request_id": "REQ-202",
        },
    ]

    engine = SecurityAlertEngine(events)

    alerts = engine.detect_failed_login_burst(threshold=5)

    assert alerts == []


def test_log_parser_request_id_filter(tmp_path):
    log_file = tmp_path / "security.log"

    log_file.write_text(
        '{"message":"login_failed","request_id":"REQ-301"}\n'
        '{"message":"login_success","request_id":"REQ-302"}\n'
        '{"message":"logout","request_id":"REQ-301"}\n',
        encoding="utf-8",
    )

    parser = SecurityLogParser(log_file)

    events = parser.read_events()
    matching_events = parser.get_events_by_request_id("REQ-301")

    assert len(events) == 3
    assert len(matching_events) == 2
    assert all(
        event["request_id"] == "REQ-301"
        for event in matching_events
    )


def test_log_parser_missing_file():
    parser = SecurityLogParser("does-not-exist/security.log")

    assert parser.read_events() == []
    assert parser.get_failed_logins() == []
    assert parser.get_event_counts() == {}


def test_log_parser_invalid_json():
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as directory:
        log_file = Path(directory) / "security.log"

        log_file.write_text(
            '{"message":"login_failed","request_id":"REQ-401"}\n'
            'this is not valid json\n'
            '{"message":"logout","request_id":"REQ-402"}\n',
            encoding="utf-8",
        )

        parser = SecurityLogParser(log_file)

        events = parser.read_events()

        assert len(events) == 2
        assert events[0]["message"] == "login_failed"
        assert events[1]["message"] == "logout"


def test_log_parser_event_counts():
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as directory:
        log_file = Path(directory) / "security.log"

        log_file.write_text(
            '{"message":"login_failed"}\n'
            '{"message":"login_failed"}\n'
            '{"message":"login_success"}\n',
            encoding="utf-8",
        )

        parser = SecurityLogParser(log_file)

        counts = parser.get_event_counts()

        assert counts["login_failed"] == 2
        assert counts["login_success"] == 1


def test_log_parser_failed_logins():
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as directory:
        log_file = Path(directory) / "security.log"

        log_file.write_text(
            '{"message":"login_failed","user":"admin"}\n'
            '{"message":"login_success","user":"admin"}\n'
            '{"message":"login_failed","user":"analyst"}\n',
            encoding="utf-8",
        )

        parser = SecurityLogParser(log_file)

        failed = parser.get_failed_logins()

        assert len(failed) == 2
        assert all(
            event["message"] == "login_failed"
            for event in failed
        )


def test_report_generator(tmp_path):
    events = [
        {
            "message": "login_failed",
            "request_id": "REQ-501",
        }
    ]

    alerts = [
        {
            "alert_id": "ALT-TEST001",
            "alert_type": "TARGETED_ACCOUNT_FAILURE",
            "rule": "targeted_account_failure",
            "severity": "MEDIUM",
            "event_count": 3,
            "target": "admin",
        },
        {
            "alert_id": "ALT-TEST002",
            "alert_type": "AUTHENTICATION_FAILURE_BURST",
            "rule": "failed_login_burst",
            "severity": "HIGH",
            "event_count": 5,
            "source_ip": "10.0.0.1",
        },
    ]

    generator = SecurityReportGenerator(tmp_path)

    report_path = generator.generate_json_report(
        events=events,
        alerts=alerts,
    )

    assert report_path.exists()

    report = json.loads(
        report_path.read_text(encoding="utf-8")
    )

    assert report["summary"]["total_events"] == 1
    assert report["summary"]["total_alerts"] == 2
    assert report["summary"]["alerts_by_severity"]["HIGH"] == 1
    assert report["summary"]["alerts_by_severity"]["MEDIUM"] == 1
    assert len(report["alerts"]) == 2