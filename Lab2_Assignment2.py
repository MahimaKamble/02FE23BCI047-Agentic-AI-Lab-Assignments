
"""
Lab 2 - Assignment 2: A Three-Tool Chain

Tools:
1. read_csv
2. filter_by_category
3. calculator

The assistant reads event data, filters technical events,
validates the filtered output, and calculates the average sign-ups.
"""

import csv
import io

# Added category column to the original CSV data
SIGNUPS_CSV = """event,signups,category
AI Club Talk,12,technical
Hackathon Kickoff,9,technical
Robotics Demo,15,technical
GenAI Workshop,7,technical
Capstone Expo,20,social
Career Panel,11,social
"""


# TOOL 1: Read CSV
def read_csv(source_text=SIGNUPS_CSV):
    reader = csv.DictReader(io.StringIO(source_text))
    rows = list(reader)

    if not rows:
        return {
            "error": "CSV file is empty",
            "rows": [],
            "row_count": 0
        }

    return {
        "rows": rows,
        "row_count": len(rows)
    }


# TOOL 2: Filter rows by category
def filter_by_category(rows, category):
    filtered_rows = [
        row for row in rows
        if row["category"].strip().lower() == category.strip().lower()
    ]

    return {
        "filtered_rows": filtered_rows,
        "filtered_count": len(filtered_rows)
    }


# TOOL 3: Calculator
def calculator(operation, values):
    if operation == "average":
        if not values:
            return {"error": "No values supplied"}

        return {"result": sum(values) / len(values)}

    if operation == "sum":
        return {"result": sum(values)}

    return {"error": f"Unsupported operation: {operation}"}


# Tool registry
TOOLS = {
    "read_csv": read_csv,
    "filter_by_category": filter_by_category,
    "calculator": calculator
}


class CampusDataAssistant:

    def __init__(self):
        self.trace = []

    # Common method for calling tools and recording their execution
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

    def answer(self, question):

        q = question.lower()

        # Three-tool chain for category-specific average
        if "average" in q and "technical" in q:

            # STEP 1: Read CSV
            csv_result = self._call(
                "read_csv",
                "Event sign-up records and categories are stored in the CSV"
            )

            # STEP 2: Filter technical events
            filter_result = self._call(
                "filter_by_category",
                "Only technical events are required for this question",
                rows=csv_result["rows"],
                category="technical"
            )

            # Validate filter output before calculating average
            filtered_rows = filter_result["filtered_rows"]

            if not filtered_rows:
                return (
                    "No technical events were found. "
                    "Average cannot be calculated."
                )

            print(
                "\nValidation passed: "
                f"{filter_result['filtered_count']} technical events found."
            )

            # Extract sign-up counts from filtered rows
            values = [
                int(row["signups"])
                for row in filtered_rows
            ]

            # STEP 3: Calculate average
            average_result = self._call(
                "calculator",
                "Calculate average sign-ups using only the filtered technical events",
                operation="average",
                values=values
            )

            return (
                f"Average sign-ups for technical events: "
                f"{average_result['result']:.2f} "
                f"(across {filter_result['filtered_count']} events)."
            )

        return "I don't have a tool path configured for that question."


if __name__ == "__main__":

    assistant = CampusDataAssistant()

    question = "What's the average sign-up for technical events only?"

    print("Q:", question)
    print("A:", assistant.answer(question))

    print("\n=== Full Tool Execution Trace ===")

    for i, entry in enumerate(assistant.trace, 1):

        print(
            f"\n{i}. tool={entry['tool']} "
            f'reason="{entry["reason"]}"'
        )

        print("   input =", entry["input"])
        print("   output =", entry["output"])
