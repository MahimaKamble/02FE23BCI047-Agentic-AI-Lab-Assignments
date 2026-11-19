
"""
Lab 10: Cloud Operations Agent -- Safe Auto-Remediation
Low-risk actions may execute automatically.
High-risk rollback actions always require human approval.
"""

# Original payments-service incident
LOGS = [
    {"ts": "14:00:00", "level": "INFO",
     "msg": "deploy started: payments-service v2.4.1"},
    {"ts": "14:00:45", "level": "INFO",
     "msg": "deploy completed: payments-service v2.4.1"},
    {"ts": "14:03:10", "level": "WARN",
     "msg": "refund endpoint latency elevated"},
    {"ts": "14:03:40", "level": "ERROR",
     "msg": "refund endpoint: NullPointerException in RefundHandler"},
    {"ts": "14:04:05", "level": "ERROR",
     "msg": "refund endpoint: NullPointerException in RefundHandler"},
    {"ts": "14:04:30", "level": "ERROR",
     "msg": "refund endpoint: NullPointerException in RefundHandler"},
]

DEPLOY_HISTORY = [
    {
        "ts": "14:00:00",
        "service": "payments-service",
        "version": "v2.4.1",
        "prev_version": "v2.4.0"
    },
]

METRICS = {
    "baseline_error_rate": 0.5,
    "current_error_rate": 1.6
}

# Database connection-pool incident from Assignment 1
DATABASE_LOGS = [
    {"ts": "13:50:00", "level": "INFO",
     "msg": "deploy started: database-service v3.2.0"},
    {"ts": "13:50:30", "level": "INFO",
     "msg": "deploy completed: database-service v3.2.0"},
    {"ts": "14:08:00", "level": "WARN",
     "msg": "database connection pool nearing maximum capacity"},
    {"ts": "14:10:00", "level": "ERROR",
     "msg": "database connection pool exhausted"},
    {"ts": "14:10:30", "level": "ERROR",
     "msg": "database connection timeout"},
    {"ts": "14:11:00", "level": "ERROR",
     "msg": "database connection pool exhausted"},
]

DATABASE_DEPLOY_HISTORY = [
    {
        "ts": "13:50:00",
        "service": "database-service",
        "version": "v3.2.0",
        "prev_version": "v3.1.9"
    },
]

DATABASE_METRICS = {
    "baseline_error_rate": 0.5,
    "current_error_rate": 0.7
}

# New WARNING-level incident for safe auto-remediation
WARNING_LOGS = [
    {"ts": "15:00:00", "level": "INFO",
     "msg": "deploy started: notification-service v1.8.0"},
    {"ts": "15:00:30", "level": "INFO",
     "msg": "deploy completed: notification-service v1.8.0"},
    {"ts": "15:03:00", "level": "WARN",
     "msg": "single pod memory usage elevated"},
    {"ts": "15:04:00", "level": "WARN",
     "msg": "notification-service pod approaching memory limit"},
]

WARNING_DEPLOY_HISTORY = [
    {
        "ts": "15:00:00",
        "service": "notification-service",
        "version": "v1.8.0",
        "prev_version": "v1.7.9"
    },
]

WARNING_METRICS = {
    "baseline_error_rate": 0.5,
    "current_error_rate": 0.7
}

def classify_severity(metrics):
    ratio = (
        metrics["current_error_rate"] /
        metrics["baseline_error_rate"]
    )

    if metrics["current_error_rate"] > 50:
        return "down"

    if ratio >= 2:
        return "degraded"

    return "early_warning"

def find_incident_start(logs):
    # A warning can also mark the start of an incident.
    for entry in logs:
        if entry["level"] in ("WARN", "ERROR"):
            return entry["ts"]

    return None

def correlate_with_recent_changes(logs, deploys, incident_start):
    error_msgs = [
        entry["msg"] for entry in logs
        if entry["level"] in ("WARN", "ERROR")
    ]

    all_messages = " ".join(error_msgs).lower()

    if "connection" in all_messages or "pool" in all_messages:
        affected_path = "database connection pool"
        target_service = "database"

    elif "refund" in all_messages:
        affected_path = "refund"
        target_service = "payments"

    elif "memory" in all_messages or "pod" in all_messages:
        affected_path = "single pod memory usage"
        target_service = "notification"

    else:
        affected_path = "unknown"
        target_service = None

    for deploy in deploys:
        if (
            incident_start is not None
            and deploy["ts"] < incident_start
            and target_service is not None
            and deploy["service"].lower().startswith(target_service)
        ):
            return {
                "hypothesis": (
                    f"Incident began at {incident_start}, shortly after "
                    f"the {deploy['ts']} deployment of "
                    f"{deploy['service']} {deploy['version']}. "
                    f"The affected area is {affected_path}."
                ),
                "suspect_deploy": deploy,
                "affected_path": affected_path,
            }

    return {
        "hypothesis": "No recent deployment correlates with the incident.",
        "suspect_deploy": None,
        "affected_path": affected_path,
    }

def risk_level(action):
    HIGH_RISK = {"rollback", "scale", "config_change", "delete"}
    LOW_RISK = {"open_ticket", "notify", "restart_single_pod"}

    if action in HIGH_RISK:
        return "high"

    if action in LOW_RISK:
        return "low"

    return "unknown"

def draft_approval_request(hypothesis, action, rollback_plan):
    return {
        "diagnosis": hypothesis["hypothesis"],
        "proposed_action": action,
        "risk_if_wrong": (
            "Brief service interruption may occur if the rollback "
            "hypothesis is incorrect."
        ),
        "rollback_plan": rollback_plan,
        "status": "AWAITING HUMAN APPROVAL -- NOT EXECUTED",
    }

def diagnose_and_propose(
    logs, deploys, metrics, proposed_action="rollback",
    urgency_prompt=False
):
    severity = classify_severity(metrics)
    incident_start = find_incident_start(logs)

    hypothesis = correlate_with_recent_changes(
        logs, deploys, incident_start
    )

    risk = risk_level(proposed_action)

    # High-risk actions must always go through human approval.
    if risk == "high":
        suspect = hypothesis["suspect_deploy"]

        if suspect is None:
            return {
                "severity": severity,
                "incident_start": incident_start,
                "diagnosis": hypothesis["hypothesis"],
                "proposed_action": proposed_action,
                "status": "MANUAL INVESTIGATION REQUIRED",
            }

        request = draft_approval_request(
            hypothesis,
            proposed_action,
            rollback_plan=(
                f"Revert to {suspect['prev_version']}; "
                f"if that also errors, re-deploy {suspect['version']}."
            )
        )

        if urgency_prompt:
            request["note"] = (
                "Urgency noted, but high-risk action still requires "
                "human approval -- not bypassing the gate."
            )

        return {
            "severity": severity,
            "incident_start": incident_start,
            **request
        }

    # Low-risk actions are simulated as automatically executed.
    if risk == "low":
        return {
            "severity": severity,
            "incident_start": incident_start,
            "diagnosis": hypothesis["hypothesis"],
            "proposed_action": proposed_action,
            "action_executed": proposed_action,
            "status": "EXECUTED AUTOMATICALLY -- LOW RISK",
        }

    # Unknown actions are never executed.
    return {
        "severity": severity,
        "incident_start": incident_start,
        "diagnosis": hypothesis["hypothesis"],
        "proposed_action": proposed_action,
        "status": "BLOCKED -- UNKNOWN ACTION RISK",
    }

if __name__ == "__main__":

    print("=== SCENARIO 1: PAYMENTS SERVICE (HIGH RISK) ===")

    payments_result = diagnose_and_propose(
        LOGS,
        DEPLOY_HISTORY,
        METRICS,
        proposed_action="rollback",
        urgency_prompt=True
    )

    for key, value in payments_result.items():
        print(f"{key}: {value}")

    print("\n=== SCENARIO 2: DATABASE SERVICE (HIGH RISK) ===")

    database_result = diagnose_and_propose(
        DATABASE_LOGS,
        DATABASE_DEPLOY_HISTORY,
        DATABASE_METRICS,
        proposed_action="rollback"
    )

    for key, value in database_result.items():
        print(f"{key}: {value}")

    print("\n=== SCENARIO 3: NOTIFICATION SERVICE (WARNING) ===")

    warning_result = diagnose_and_propose(
        WARNING_LOGS,
        WARNING_DEPLOY_HISTORY,
        WARNING_METRICS,
        proposed_action="restart_single_pod"
    )

    for key, value in warning_result.items():
        print(f"{key}: {value}")

    print("\n=== SAFETY VERIFICATION ===")

    print(
        "Warning incident has early-warning severity:",
        warning_result["severity"] == "early_warning"
    )

    print(
        "Low-risk restart executed automatically:",
        warning_result.get("action_executed") == "restart_single_pod"
    )

    print(
        "Payments rollback requires approval:",
        payments_result.get("status") ==
        "AWAITING HUMAN APPROVAL -- NOT EXECUTED"
    )

    print(
        "Database rollback requires approval:",
        database_result.get("status") ==
        "AWAITING HUMAN APPROVAL -- NOT EXECUTED"
    )

    print(
        "No rollback executed automatically:",
        "action_executed" not in payments_result
        and "action_executed" not in database_result
    )

    assert warning_result["severity"] == "early_warning"
    assert warning_result["action_executed"] == "restart_single_pod"
    assert "action_executed" not in payments_result
    assert "action_executed" not in database_result

    print("\nAll assignment checks passed.")