
"""
Lab 10: Cloud Operations Agent -- Second Incident Type
Observe -> Reason -> Act, with human approval for rollback.
"""

# Original incident: payments-service deployment failure
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

# New incident: database connection-pool exhaustion
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
    for entry in logs:
        if entry["level"] == "ERROR":
            return entry["ts"]

    return None

def correlate_with_recent_changes(logs, deploys, incident_start):
    error_msgs = [
        entry["msg"] for entry in logs
        if entry["level"] == "ERROR"
    ]

    all_messages = " ".join(error_msgs).lower()

    # Identify the affected code path and corresponding service.
    if "connection" in all_messages or "pool" in all_messages:
        affected_path = "database connection pool"
        target_service = "database"
    elif "refund" in all_messages:
        affected_path = "refund"
        target_service = "payments"
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
                    f"Error rate rose starting {incident_start}, shortly "
                    f"after the {deploy['ts']} deploy of "
                    f"{deploy['service']} {deploy['version']}. "
                    f"Errors are concentrated in the {affected_path} "
                    f"code path, consistent with a regression introduced "
                    f"in that release."
                ),
                "suspect_deploy": deploy,
                "affected_path": affected_path,
            }

    return {
        "hypothesis": "No recent deploy correlates with the incident window.",
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
            "Brief service interruption (~30s) during rollback "
            "if hypothesis is incorrect."
        ),
        "rollback_plan": rollback_plan,
        "status": "AWAITING HUMAN APPROVAL -- NOT EXECUTED",
    }

def diagnose_and_propose(logs, deploys, metrics, urgency_prompt=False):
    severity = classify_severity(metrics)
    incident_start = find_incident_start(logs)

    hypothesis = correlate_with_recent_changes(
        logs, deploys, incident_start
    )

    proposed_action = "rollback"
    risk = risk_level(proposed_action)

    if risk == "high":
        suspect = hypothesis["suspect_deploy"]

        if suspect is None:
            return {
                "severity": severity,
                "incident_start": incident_start,
                "diagnosis": hypothesis["hypothesis"],
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

    return {
        "severity": severity,
        "incident_start": incident_start,
        "action_executed": proposed_action,
    }

if __name__ == "__main__":

    print("=== ORIGINAL INCIDENT: PAYMENTS SERVICE ===")

    original_result = diagnose_and_propose(
        LOGS,
        DEPLOY_HISTORY,
        METRICS,
        urgency_prompt=True
    )

    for key, value in original_result.items():
        print(f"{key}: {value}")

    print("\n=== SECOND INCIDENT: DATABASE CONNECTION POOL ===")

    database_result = diagnose_and_propose(
        DATABASE_LOGS,
        DATABASE_DEPLOY_HISTORY,
        DATABASE_METRICS,
        urgency_prompt=True
    )

    for key, value in database_result.items():
        print(f"{key}: {value}")

    print("\n=== ASSIGNMENT VERIFICATION ===")

    print(
        "Different severity:",
        original_result["severity"] != database_result["severity"]
    )

    print(
        "Original diagnosis identifies refund path:",
        "refund" in original_result["diagnosis"].lower()
    )

    print(
        "Database diagnosis identifies connection pool:",
        "database connection pool"
        in database_result["diagnosis"].lower()
    )

    print(
        "Database diagnosis identifies database deployment:",
        "database-service"
        in database_result["diagnosis"]
    )

    print(
        "Both incidents require human approval:",
        original_result.get("status") == "AWAITING HUMAN APPROVAL -- NOT EXECUTED"
        and database_result.get("status") == "AWAITING HUMAN APPROVAL -- NOT EXECUTED"
    )

    assert original_result["severity"] == "degraded"
    assert database_result["severity"] == "early_warning"
    assert "refund" in original_result["diagnosis"].lower()
    assert "database connection pool" in database_result["diagnosis"].lower()
    assert "action_executed" not in original_result
    assert "action_executed" not in database_result

    print("\nAll assignment checks passed.")