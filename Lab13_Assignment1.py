
"""
Lab 13: Discipline-Specific Engineering Agents
Assignment 1: Add a Second Domain - Electrical Load Forecasting

The original Mechanical predictive-maintenance agent is retained.
A parallel Electrical Engineering agent is added for load forecasting.

Both agents use threshold-based classification and safety checks.
ALARM-level actions require human review and are never auto-executed.
"""

# ============================================================
# ORIGINAL MECHANICAL ENGINEERING AGENT
# ============================================================

# Simulated sensor log for one motor over 6 readings.
SENSOR_LOG = [
    {"t": 0, "vibration_mm_s": 1.8, "temp_c": 61},
    {"t": 1, "vibration_mm_s": 1.9, "temp_c": 62},
    {"t": 2, "vibration_mm_s": 2.4, "temp_c": 65},
    {"t": 3, "vibration_mm_s": 3.1, "temp_c": 70},
    {"t": 4, "vibration_mm_s": 4.6, "temp_c": 76},
    {"t": 5, "vibration_mm_s": 6.2, "temp_c": 84},
]

# ISO 10816-based-style thresholds for illustration.
THRESHOLDS = {
    "vibration_warn": 2.8,
    "vibration_alarm": 4.5,
    "temp_warn": 70,
    "temp_alarm": 80
}


def tool_read_sensor_log():
    return SENSOR_LOG


def classify_condition(reading):
    if (
        reading["vibration_mm_s"] >= THRESHOLDS["vibration_alarm"]
        or reading["temp_c"] >= THRESHOLDS["temp_alarm"]
    ):
        return "ALARM"

    if (
        reading["vibration_mm_s"] >= THRESHOLDS["vibration_warn"]
        or reading["temp_c"] >= THRESHOLDS["temp_warn"]
    ):
        return "WARNING"

    return "NORMAL"


def trend_direction(log):
    deltas = [
        log[i + 1]["vibration_mm_s"] - log[i]["vibration_mm_s"]
        for i in range(len(log) - 1)
    ]

    return "worsening" if all(d >= 0 for d in deltas) else "mixed"


def safety_check(condition):
    # ALARM-level shutdown recommendations require human approval.
    if condition == "ALARM":
        return {
            "action_allowed": "recommend_shutdown_for_human_review",
            "auto_execute": False
        }

    if condition == "WARNING":
        return {
            "action_allowed": "schedule_inspection",
            "auto_execute": False
        }

    return {
        "action_allowed": "continue_monitoring",
        "auto_execute": True
    }


def predictive_maintenance_agent():
    log = tool_read_sensor_log()
    latest = log[-1]

    condition = classify_condition(latest)
    trend = trend_direction(log)
    safety = safety_check(condition)

    output = {
        "domain": "Mechanical Engineering -- Predictive Maintenance",
        "latest_reading": latest,
        "condition": condition,
        "trend": trend,
        "recommended_action": safety["action_allowed"],
        "auto_executed": safety["auto_execute"],
        "evaluation_method": (
            "Threshold classification against ISO-10816-style "
            "vibration bands, cross-checked with temperature trend "
            "over the log window."
        )
    }

    return output


# ============================================================
# NEW ELECTRICAL ENGINEERING AGENT
# ============================================================

# Simulated electrical load forecasting data.
# Forecast values represent expected power consumption in kW.
ELECTRICAL_LOAD_LOG = [
    {"t": 0, "forecast_load_kw": 62},
    {"t": 1, "forecast_load_kw": 68},
    {"t": 2, "forecast_load_kw": 74},
    {"t": 3, "forecast_load_kw": 82},
    {"t": 4, "forecast_load_kw": 91},
    {"t": 5, "forecast_load_kw": 98},
]

# Illustrative thresholds for a system with 100 kW capacity.
LOAD_THRESHOLDS = {
    "capacity_kw": 100,
    "load_warn": 80,
    "load_alarm": 95
}


def tool_read_electrical_load_log():
    return ELECTRICAL_LOAD_LOG


def classify_load_condition(reading):
    forecast_load = reading["forecast_load_kw"]

    if forecast_load >= LOAD_THRESHOLDS["load_alarm"]:
        return "ALARM"

    if forecast_load >= LOAD_THRESHOLDS["load_warn"]:
        return "WARNING"

    return "NORMAL"


def electrical_load_trend(log):
    deltas = [
        log[i + 1]["forecast_load_kw"] - log[i]["forecast_load_kw"]
        for i in range(len(log) - 1)
    ]

    return "increasing" if all(d >= 0 for d in deltas) else "fluctuating"


def electrical_safety_check(condition):
    # An ALARM-level load must be reviewed by a qualified engineer.
    # The agent must never automatically disconnect the electrical supply.
    if condition == "ALARM":
        return {
            "action_allowed": "recommend_load_reduction_for_human_review",
            "auto_execute": False
        }

    if condition == "WARNING":
        return {
            "action_allowed": "recommend_load_monitoring",
            "auto_execute": False
        }

    return {
        "action_allowed": "continue_normal_operation",
        "auto_execute": True
    }


def electrical_load_forecasting_agent():
    log = tool_read_electrical_load_log()
    latest = log[-1]

    condition = classify_load_condition(latest)
    trend = electrical_load_trend(log)
    safety = electrical_safety_check(condition)

    output = {
        "domain": "Electrical Engineering -- Load Forecasting",
        "latest_reading": latest,
        "system_capacity_kw": LOAD_THRESHOLDS["capacity_kw"],
        "condition": condition,
        "trend": trend,
        "recommended_action": safety["action_allowed"],
        "auto_executed": safety["auto_execute"],
        "evaluation_method": (
            "Threshold-based classification of forecast electrical "
            "load against the system capacity, with load trend analysis."
        )
    }

    return output


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    # Run Mechanical Engineering agent.
    mechanical_result = predictive_maintenance_agent()

    print("=== Mechanical Engineering Agent Output ===")
    for key, value in mechanical_result.items():
        print(f"{key}: {value}")

    # Run Electrical Engineering agent.
    electrical_result = electrical_load_forecasting_agent()

    print("\n=== Electrical Engineering Agent Output ===")
    for key, value in electrical_result.items():
        print(f"{key}: {value}")

    # Safety verification for both domains.
    assert (
        mechanical_result["condition"] != "ALARM"
        or mechanical_result["auto_executed"] is False
    ), "Mechanical ALARM must require human review!"

    assert (
        electrical_result["condition"] != "ALARM"
        or electrical_result["auto_executed"] is False
    ), "Electrical ALARM must require human review!"

    print("\n=== Safety Verification ===")
    print("Mechanical ALARM auto-execution blocked: PASS")
    print("Electrical ALARM auto-execution blocked: PASS")
    print("Both agents require human review for ALARM actions.")
