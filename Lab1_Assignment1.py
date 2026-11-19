
"""
Lab 1: Agent vs Chatbot
Assignment 1: Two Rounds of Feedback

Extend the Study Planner Agent to accept two independent
rounds of feedback.

Both revisions must modify the same existing plan object.
The plan must not be regenerated from scratch.
"""

import json
import copy


# --------------------------------------------------
# Simulated user inputs
# --------------------------------------------------

SIMULATED_ANSWERS = {
    "subjects": [
        "Data Structures",
        "Operating Systems",
        "AI Agents"
    ],
    "hours_per_day": 2,
    "unavailable_days": ["Sunday"]
}

# Two independent feedback rounds
SIMULATED_FEEDBACK = [
    "Move Tuesday's session to the evening.",
    "Make Friday's session shorter, only one hour."
]


# --------------------------------------------------
# Study Planner Agent
# --------------------------------------------------

class StudyPlannerAgent:

    def __init__(self, existing_schedule):

        # Goal modeled as data
        self.goal = {
            "subjects": None,
            "hours_per_day": None,
            "unavailable_days": None,
            "schedule_generated": False
        }

        self.existing_schedule = existing_schedule
        self.plan = None
        self.log = []

    # --------------------------------------------------
    # Check whether the goal is achieved
    # --------------------------------------------------

    def satisfied(self):
        return self.goal["schedule_generated"] is True

    # --------------------------------------------------
    # Decide the next step
    # --------------------------------------------------

    def next_step(self):

        for field in (
            "subjects",
            "hours_per_day",
            "unavailable_days"
        ):

            if self.goal[field] is None:
                return ("ask", field)

        return ("generate_plan", None)

    # --------------------------------------------------
    # Tool: Read existing schedule
    # --------------------------------------------------

    def read_existing_schedule(self):

        result = self.existing_schedule

        if "error" in result:
            raise RuntimeError(
                f"Tool error: {result['error']}"
            )

        return result

    # --------------------------------------------------
    # Main agent loop
    # --------------------------------------------------

    def run(self):

        while not self.satisfied():

            step, arg = self.next_step()

            # Ask for missing information
            if step == "ask":

                answer = SIMULATED_ANSWERS[arg]

                self.goal[arg] = answer

                self.log.append({
                    "iteration": len(self.log) + 1,
                    "planned": f"ask for {arg}",
                    "action": f"asked user for {arg}",
                    "observed": copy.deepcopy(answer),
                    "stopped": False
                })

            # Generate study plan
            elif step == "generate_plan":

                busy = self.read_existing_schedule()

                self.log.append({
                    "iteration": len(self.log) + 1,
                    "planned": "read existing schedule before generating plan",
                    "action": "tool call: read_existing_schedule()",
                    "observed": copy.deepcopy(busy),
                    "stopped": False
                })

                self.plan = self._build_plan(busy)

                self.goal["schedule_generated"] = True

                self.log.append({
                    "iteration": len(self.log) + 1,
                    "planned": "generate schedule from gathered requirements",
                    "action": "built weekly plan",
                    "observed": copy.deepcopy(self.plan),
                    "stopped": True,
                    "stop_reason": (
                        "goal.schedule_generated is now True"
                    )
                })

        return self.plan

    # --------------------------------------------------
    # Build the weekly study plan
    # --------------------------------------------------

    def _build_plan(self, busy_slots):

        days = [
            day for day in [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday"
            ]
            if day not in self.goal["unavailable_days"]
        ]

        subjects = self.goal["subjects"]

        plan = {}

        for i, day in enumerate(days):

            subject = subjects[i % len(subjects)]

            slot = "17:00-19:00"

            # Avoid existing schedule conflicts
            if day in busy_slots.get("busy_days", []):
                slot = "20:00-22:00"

            plan[day] = {
                "subject": subject,
                "time": slot
            }

        return plan

    # --------------------------------------------------
    # Revise the existing plan using feedback
    # --------------------------------------------------

    def revise(self, feedback):

        self.log.append({
            "iteration": len(self.log) + 1,
            "planned": "apply user feedback to existing plan",
            "action": f"feedback received: '{feedback}'",
            "observed": None,
            "stopped": False
        })

        feedback_lower = feedback.lower()

        # First feedback:
        # Move Tuesday's session to the evening

        if "tuesday" in feedback_lower and "evening" in feedback_lower:

            if "Tuesday" in self.plan:

                self.plan["Tuesday"]["time"] = "20:00-22:00"

                print("Tuesday session moved to evening.")

            else:
                print("Tuesday is not available in the plan.")

        # Second feedback:
        # Make Friday's session one hour long

        elif "friday" in feedback_lower and "one hour" in feedback_lower:

            if "Friday" in self.plan:

                start_time = self.plan["Friday"]["time"].split("-")[0]

                start_hour = int(start_time.split(":")[0])

                end_hour = start_hour + 1

                self.plan["Friday"]["time"] = (
                    f"{start_hour:02d}:00-{end_hour:02d}:00"
                )

                print("Friday session shortened to one hour.")

            else:
                print("Friday is not available in the plan.")

        else:
            print("Feedback not recognized:", feedback)
            return self.plan

        # Record the revised plan
        self.log.append({
            "iteration": len(self.log) + 1,
            "planned": "confirm revised plan",
            "action": "mutated existing plan (not regenerated from scratch)",
            "observed": copy.deepcopy(self.plan),
            "stopped": True,
            "stop_reason": "revision applied without restarting the loop"
        })

        return self.plan


# --------------------------------------------------
# Main program
# --------------------------------------------------

if __name__ == "__main__":

    # Mock existing schedule
    existing_schedule = {
        "busy_days": ["Wednesday"]
    }

    agent = StudyPlannerAgent(existing_schedule)

    # Generate initial plan
    print("\n========== INITIAL STUDY PLAN ==========")

    plan = agent.run()

    print(json.dumps(plan, indent=4))

    # Store original plan object identity
    original_plan_id = id(agent.plan)

    # --------------------------------------------------
    # First feedback round
    # --------------------------------------------------

    print("\n========== FIRST FEEDBACK ROUND ==========")

    first_feedback = SIMULATED_FEEDBACK[0]

    print("Feedback:", first_feedback)

    revised_plan_1 = agent.revise(first_feedback)

    print("\nPlan after first revision:")

    print(json.dumps(revised_plan_1, indent=4))

    # --------------------------------------------------
    # Second feedback round
    # --------------------------------------------------

    print("\n========== SECOND FEEDBACK ROUND ==========")

    second_feedback = SIMULATED_FEEDBACK[1]

    print("Feedback:", second_feedback)

    revised_plan_2 = agent.revise(second_feedback)

    print("\nPlan after second revision:")

    print(json.dumps(revised_plan_2, indent=4))

    # --------------------------------------------------
    # Verify same plan object was modified
    # --------------------------------------------------

    print("\n========== OBJECT IDENTITY VERIFICATION ==========")

    current_plan_id = id(agent.plan)

    print("Original Plan ID:", original_plan_id)

    print("Current Plan ID:", current_plan_id)

    print(
        "Same plan object:",
        original_plan_id == current_plan_id
    )

    # --------------------------------------------------
    # Full iteration log
    # --------------------------------------------------

    print("\n========== FULL ITERATION LOG ==========")

    for entry in agent.log:

        print(json.dumps(entry, indent=4))

