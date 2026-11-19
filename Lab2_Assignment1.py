
"""
Lab 2: Tool-Using Agent
Assignment 1: Add a Notification Tool with Justified Use

Tools:
1. calculator
2. read_csv
3. mock_events_api
4. send_notification

The notification tool only drafts messages.
It does not send actual notifications.
"""

import csv
import io
import json


# --------------------------------------------------
# CSV DATA
# --------------------------------------------------

SIGNUPS_CSV = """event,signups
AI Club Talk,12
Hackathon Kickoff,9
Robotics Demo,15
GenAI Workshop,7
Capstone Expo,20
Career Panel,11
"""


# --------------------------------------------------
# MOCK EVENTS API DATABASE
# --------------------------------------------------

MOCK_EVENTS_API_DB = {
    "AI Club Talk": {
        "date": "2026-07-02",
        "location": "CS Block Auditorium"
    },

    "Hackathon Kickoff": {
        "date": "2026-07-05",
        "location": "Innovation Lab"
    }
}


# --------------------------------------------------
# TOOL 1: CALCULATOR
# --------------------------------------------------

def calculator(operation, values):

    if operation == "average":

        if not values:
            return {"error": "no values supplied"}

        return {
            "result": sum(values) / len(values)
        }

    if operation == "sum":

        return {
            "result": sum(values)
        }

    return {
        "error": f"unsupported operation: {operation}"
    }


# --------------------------------------------------
# TOOL 2: READ CSV
# --------------------------------------------------

def read_csv(source_text=SIGNUPS_CSV):

    reader = csv.DictReader(
        io.StringIO(source_text)
    )

    rows = list(reader)

    if not rows:

        return {
            "error": "empty file",
            "rows": [],
            "row_count": 0
        }

    return {
        "rows": rows,
        "row_count": len(rows)
    }


# --------------------------------------------------
# TOOL 3: MOCK EVENTS API
# --------------------------------------------------

def mock_events_api(event_name):

    record = MOCK_EVENTS_API_DB.get(event_name)

    if record is None:

        return {
            "error": (
                f"no event metadata found for '{event_name}'"
            )
        }

    return record


# --------------------------------------------------
# TOOL 4: SEND NOTIFICATION
# --------------------------------------------------

def send_notification(message):

    # Only drafts the notification.
    # It does not send any actual message.

    return {
        "status": "drafted",
        "message": message,
        "sent": False
    }


# --------------------------------------------------
# TOOL REGISTRY
# --------------------------------------------------

TOOLS = {
    "calculator": calculator,
    "read_csv": read_csv,
    "events_api": mock_events_api,
    "send_notification": send_notification
}


# --------------------------------------------------
# CAMPUS DATA ASSISTANT
# --------------------------------------------------

class CampusDataAssistant:

    def __init__(self):

        self.trace = []

        # Defined low-turnout threshold
        self.threshold = 13

    # --------------------------------------------------
    # Common tool calling method
    # --------------------------------------------------

    def _call(self, tool_name, reason, **kwargs):

        result = TOOLS[tool_name](**kwargs)

        entry = {
            "tool": tool_name,
            "reason": reason,
            "input": kwargs,
            "output": result
        }

        self.trace.append(entry)

        if "error" in result:

            raise RuntimeError(
                f"{tool_name} failed: {result['error']}"
            )

        return result

    # --------------------------------------------------
    # Answer user questions
    # --------------------------------------------------

    def answer(self, question):

        q = question.lower()

        # ----------------------------------------------
        # Calculate total and average sign-ups
        # ----------------------------------------------

        if "average" in q and "sign" in q:

            csv_result = self._call(
                "read_csv",
                "Sign-up counts are stored in the CSV file"
            )

            values = [
                int(row["signups"])
                for row in csv_result["rows"]
            ]

            # Calculate total
            total = self._call(
                "calculator",
                "Calculate total event sign-ups",
                operation="sum",
                values=values
            )

            # Calculate average
            avg = self._call(
                "calculator",
                "Calculate average sign-ups per event",
                operation="average",
                values=values
            )

            average_value = avg["result"]

            # ------------------------------------------
            # Check low-turnout threshold
            # ------------------------------------------

            notification_result = None

            if average_value < self.threshold:

                message = (
                    "Low turnout alert! The average event "
                    f"sign-ups are {average_value:.2f}, "
                    f"which is below the threshold of "
                    f"{self.threshold}. Please review "
                    "event publicity and student engagement."
                )

                # Call notification tool only when needed
                notification_result = self._call(
                    "send_notification",
                    (
                        f"Average sign-ups ({average_value:.2f}) "
                        f"is below the threshold ({self.threshold}); "
                        "a low-turnout notice must be drafted."
                    ),
                    message=message
                )

            return (
                f"Total sign-ups: {total['result']}. "
                f"Average per event: {average_value:.2f} "
                f"(across {csv_result['row_count']} events). "
                + (
                    "Low-turnout notification drafted."
                    if notification_result
                    else "No notification required."
                )
            )

        # ----------------------------------------------
        # Get Hackathon event details
        # ----------------------------------------------

        if "where" in q and "hackathon" in q:

            meta = self._call(
                "events_api",
                "Event location and date are stored in the events API",
                event_name="Hackathon Kickoff"
            )

            return (
                f"Hackathon Kickoff is at "
                f"{meta['location']} on {meta['date']}."
            )

        # ----------------------------------------------
        # Get Capstone Expo details
        # ----------------------------------------------

        if "where" in q and "capstone" in q:

            try:

                meta = self._call(
                    "events_api",
                    "Checking the events API for Capstone Expo metadata",
                    event_name="Capstone Expo"
                )

                return (
                    f"Capstone Expo is at "
                    f"{meta['location']} on {meta['date']}."
                )

            except RuntimeError:

                return (
                    "I don't have location/date metadata "
                    "for Capstone Expo in the events API."
                )

        return "I don't have a tool path configured for that question."


# --------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    assistant = CampusDataAssistant()

    questions = [

        "How many students signed up for events this month, "
        "and what's the average per event?",

        "Where and when is the Hackathon Kickoff?",

        "Where and when is the Capstone Expo?"
    ]

    # ----------------------------------------------
    # Execute questions
    # ----------------------------------------------

    print("========== CAMPUS DATA ASSISTANT ==========")

    for question in questions:

        print("\nQ:", question)

        answer = assistant.answer(question)

        print("A:", answer)

    # ----------------------------------------------
    # Display notification draft
    # ----------------------------------------------

    print("\n========== NOTIFICATION DRAFT ==========")

    notification_entries = [
        entry for entry in assistant.trace
        if entry["tool"] == "send_notification"
    ]

    if notification_entries:

        for entry in notification_entries:

            print("Status:", entry["output"]["status"])

            print("Message:", entry["output"]["message"])

            print("Actually sent:", entry["output"]["sent"])

    else:

        print("No notification was required.")

    # ----------------------------------------------
    # Display complete tool trace
    # ----------------------------------------------

    print("\n========== FULL TOOL TRACE ==========")

    for index, entry in enumerate(
        assistant.trace, 1
    ):

        print(f"\n{index}. Tool: {entry['tool']}")

        print("Reason:", entry["reason"])

        print("Input:", entry["input"])

        print("Output:", entry["output"])

    # ----------------------------------------------
    # Final verification
    # ----------------------------------------------

    print("\n========== VERIFICATION ==========")

    print("Threshold:", assistant.threshold)

    print(
        "Notification tool added:",
        "send_notification" in TOOLS
    )

    print(
        "Notification drafted:",
        len(notification_entries) > 0
    )

    print(
        "Notification actually sent:",
        any(
            entry["output"].get("sent", False)
            for entry in notification_entries
        )
    )
