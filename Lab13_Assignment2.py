
"""
Lab 13: Discipline-Specific Engineering Agents
Assignment 2: Escalate on a Trend, Not Just a Threshold

Extends the original Mechanical predictive-maintenance agent.
Three consecutive WARNING-level readings trigger an explicit
schedule_inspection recommendation.

ALARM-level actions always require human review.
"""

# ============================================================
# SENSOR DATA
# ============================================================

# Original sensor log from the lab guide.
SENSOR_LOG = [
    {"t": 0, "vibration_mm_s": 1.8, "temp_c": 61},
    {"t": 1, "vibration_mm_s": 1.9, "temp_c": 62},
    {"t": 2, "vibration_mm_s": 2.4, "temp_c": 65},
    {"t": 3, "vibration_mm_s": 3.1, "temp_c": 70},
    {"t": 4, "vibration_mm_s": 4.6, "temp_c": 76},
    {"t": 5, "vibration_mm_s": 6.2, "temp_c": 84},
]

# Modified log for Assignment 2.
# The last three readings are WARNING-level.
# None reaches the ALARM threshold.
WARNING_TREND_LOG = [
    {"t": 0, "vibration_mm_s": 1.8, "temp_c": 61},
    {"t": 1, "vibration_mm_s": 2.0, "temp_c": 63},
    {"t": 2, "vibration_mm_s": 2.9, "temp_c": 71},
    {"t": 3, "vibration_mm_s": 3.3, "temp_c": 74},
    {"t": 4, "vibration_mm_s": 3.9, "temp_c": 78},
]


# ============================================================
# THRESHOLDS
# ============================================================

THRESHOLDS = {
    "vibration_warn": 2.8,
    "vibration_alarm": 4.5,
    "temp_warn": 70,
    "temp_alarm": 80
}


# ============================================================
# TOOLS AND CLASSIFICATION
# ============================================================

def tool_read_sensor_log(sensor_log):
    return sensor_log


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


# ============================================================
# NEW: CONSECUTIVE WARNING DETECTION
# ============================================================

def count_consecutive_warnings(log):

    warning_count = 0

    # Examine readings backwards from the latest reading.
    for reading in reversed(log):

        condition = classify_condition(reading)

        if condition == "WARNING":
            warning_count += 1
        else:
            break

    return warning_count


# ============================================================
# SAFETY CHECK
# ============================================================

def safety_check(condition):

    # ALARM requires human maintenance engineer approval.
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


# ============================================================
# PREDICTIVE MAINTENANCE AGENT
# ============================================================

def predictive_maintenance_agent(sensor_log):

    log = tool_read_sensor_log(sensor_log)

    latest = log[-1]

    condition = classify_condition(latest)
    trend = trend_direction(log)

    warning_streak = count_consecutive_warnings(log)

    safety = safety_check(condition)

    recommended_action = safety["action_allowed"]
    auto_executed = safety["auto_execute"]

    escalation_reason = "No three-reading WARNING streak detected."

    # New assignment requirement:
    # Three consecutive WARNING readings trigger inspection.
    if warning_streak >= 3 and condition != "ALARM":

        recommended_action = "schedule_inspection"
        auto_executed = False

        escalation_reason = (
            "Three consecutive WARNING-level readings detected. "
            "Inspection recommended."
        )

    output = {
        "domain": "Mechanical Engineering -- Predictive Maintenance",
        "latest_reading": latest,
        "condition": condition,
        "trend": trend,
        "consecutive_warning_readings": warning_streak,
        "recommended_action": recommended_action,
        "auto_executed": auto_executed,
        "escalation_reason": escalation_reason,
        "evaluation_method": (
            "Threshold classification against ISO-10816-style "
            "vibration bands, cross-checked with temperature trend "
            "and consecutive WARNING readings."
        )
    }

    return output


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("=== Trend-Based Escalation ===")

    result = predictive_maintenance_agent(WARNING_TREND_LOG)

    for key, value in result.items():
        print(f"{key}: {value}")

    # Verify that the three-warning streak was detected.
    assert result["consecutive_warning_readings"] == 3

    # Verify that the agent recommends inspection.
    assert result["recommended_action"] == "schedule_inspection"

    # Verify that no reading reached ALARM.
    assert result["condition"] == "WARNING"

    # Verify that inspection is not automatically executed.
    assert result["auto_executed"] is False

    print("\n=== Assignment Verification ===")
    print("Three consecutive WARNING readings detected: PASS")
    print("No ALARM threshold reached: PASS")
    print("Inspection recommendation generated: PASS")
    print("Inspection requires human review: PASS")

    # Also verify original ALARM safety behavior.
    alarm_result = predictive_maintenance_agent(SENSOR_LOG)

    assert alarm_result["condition"] == "ALARM"
    assert alarm_result["auto_executed"] is False

    print("Original ALARM safety gate preserved: PASS")
