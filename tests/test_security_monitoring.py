from src.security_monitoring.alert_engine import SecurityAlertEngine
from src.security_monitoring.log_parser import SecurityLogParser


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