import json
from pathlib import Path

import streamlit as st


REPORT_FILE = Path("reports/security_report.json")


st.set_page_config(
    page_title="Security Operations Dashboard",
    page_icon="SOC",
    layout="wide",
)


def load_report() -> dict:
    """Load the latest security monitoring report."""
    if not REPORT_FILE.exists():
        return {
            "generated_at": None,
            "summary": {
                "total_events": 0,
                "total_alerts": 0,
                "alerts_by_severity": {},
            },
            "alerts": [],
        }

    with REPORT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


report = load_report()

summary = report.get("summary", {})
alerts = report.get("alerts", [])
severity_counts = summary.get("alerts_by_severity", {})

total_events = summary.get("total_events", 0)
total_alerts = summary.get("total_alerts", 0)
high_alerts = severity_counts.get("HIGH", 0)
medium_alerts = severity_counts.get("MEDIUM", 0)
low_alerts = severity_counts.get("LOW", 0)


# Dashboard header
st.title("Security Operations Dashboard")
st.caption("Security monitoring, detection and incident analysis")

st.divider()


# Executive metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Security Events", total_events)

with col2:
    st.metric("Total Alerts", total_alerts)

with col3:
    st.metric("High Severity", high_alerts)

with col4:
    st.metric("Medium Severity", medium_alerts)


st.divider()


# Severity overview
st.subheader("Alert Severity Overview")

severity_col1, severity_col2, severity_col3 = st.columns(3)

with severity_col1:
    st.metric("HIGH", high_alerts)

with severity_col2:
    st.metric("MEDIUM", medium_alerts)

with severity_col3:
    st.metric("LOW", low_alerts)


st.divider()


# Security alerts
st.subheader("Security Alerts")

if alerts:
    for alert in alerts:
        alert_type = alert.get("alert_type", "Unknown Alert")
        severity = alert.get("severity", "UNKNOWN")

        with st.container(border=True):
            header_col, severity_col = st.columns([4, 1])

            with header_col:
                st.markdown(f"### {alert_type}")

            with severity_col:
                st.metric("Severity", severity)

            st.write(
                f"**Alert ID:** `{alert.get('alert_id', 'N/A')}`"
            )

            st.write(
                f"**Detection Rule:** `{alert.get('rule', 'N/A')}`"
            )

            st.write(
                f"**Description:** "
                f"{alert.get('description', 'N/A')}"
            )

            details_col1, details_col2, details_col3 = st.columns(3)

            with details_col1:
                st.write(
                    f"**Event Count:** "
                    f"{alert.get('event_count', 0)}"
                )

            with details_col2:
                st.write(
                    f"**Target:** "
                    f"`{alert.get('target', 'N/A')}`"
                )

            with details_col3:
                st.write(
                    f"**Detected:** "
                    f"{alert.get('detected_at', 'N/A')}"
                )

            source_ips = alert.get("source_ips", [])

            if source_ips:
                st.write("**Source IPs**")
                st.write(", ".join(source_ips))

            request_ids = alert.get("request_ids", [])

            if request_ids:
                st.write("**Correlated Request IDs**")

                for request_id in request_ids:
                    st.code(request_id)

else:
    st.success("No security alerts detected.")


st.divider()


# Alert summary table
st.subheader("Alert Summary")

if alerts:
    alert_table = []

    for alert in alerts:
        alert_table.append(
            {
                "Alert ID": alert.get("alert_id", "N/A"),
                "Alert Type": alert.get("alert_type", "N/A"),
                "Rule": alert.get("rule", "N/A"),
                "Severity": alert.get("severity", "N/A"),
                "Target": alert.get("target", "N/A"),
                "Event Count": alert.get("event_count", 0),
            }
        )

    st.dataframe(
        alert_table,
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No security alerts available.")


st.divider()


# Report information
st.subheader("Monitoring Information")

st.write(
    f"**Latest report generated:** "
    f"{report.get('generated_at', 'N/A')}"
)

st.caption(
    "Data source: structured security monitoring report"
)