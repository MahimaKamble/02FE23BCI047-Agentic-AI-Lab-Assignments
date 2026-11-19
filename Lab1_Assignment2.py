
"""
Lab 1: Agent vs Chatbot
Assignment 2: Detect a Scheduling Conflict

The agent checks existing busy days against the
student's unavailable days before generating a plan.

If conflicts exist, it reports them explicitly
and does not finalize the study plan.
"""

import json


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


# --------------------------------------------------
# Study Planner Agent
# --------------------------------------------------

class StudyPlannerAgent:

    def __init__(self, existing_schedule):

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
    # Check whether goal is achieved
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
    # Check scheduling conflicts
    # --------------------------------------------------

    def detect_conflicts(self, busy_slots):

        busy_days = set(busy_slots.get("busy_days", []))

        unavailable_days = set(
            self.goal["unavailable_days"]
        )

        # Busy days not included in unavailable days
        conflicts = sorted(
            busy_days - unavailable_days
        )

        return conflicts

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
                    "observed": answer,
                    "stopped": False
                })

            # Generate plan
            elif step == "generate_plan":

                busy = self.read_existing_schedule()

                self.log.append({
                    "iteration": len(self.log) + 1,
                    "planned": "read existing schedule",
                    "action": "tool call: read_existing_schedule()",
                    "observed": busy,
                    "stopped": False
                })

                # Check conflicts before building the plan
                conflicts = self.detect_conflicts(busy)

                if conflicts:

                    conflict_message = (
                        "Scheduling conflict detected! "
                        "The following days are already busy: "
                        + ", ".join(conflicts)
                    )

                    print("\nWARNING:", conflict_message)

                    print(
                        "Please update your unavailable days "
                        "before generating the study plan."
                    )

                    self.log.append({
                        "iteration": len(self.log) + 1,
                        "planned": "check busy days against unavailable days",
                        "action": "detected scheduling conflicts",
                        "observed": {
                            "conflicting_days": conflicts,
                            "unavailable_days": (
                                self.goal["unavailable_days"]
                            )
                        },
                        "stopped": True,
                        "stop_reason": (
                            "plan generation blocked due to scheduling conflicts"
                        )
                    })

                    # Do not generate a conflicting plan
                    return None

                # Generate plan only if no conflicts exist
                self.plan = self._build_plan(busy)

                self.goal["schedule_generated"] = True

                self.log.append({
                    "iteration": len(self.log) + 1,
                    "planned": "generate schedule from gathered requirements",
                    "action": "built weekly plan",
                    "observed": self.plan,
                    "stopped": True,
                    "stop_reason": (
                        "no scheduling conflicts detected"
                    )
                })

        return self.plan

    # --------------------------------------------------
    # Build the actual study plan
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

            plan[day] = {
                "subject": subject,
                "time": slot
            }

        return plan


# --------------------------------------------------
# Main program
# --------------------------------------------------

if __name__ == "__main__":

    # Existing schedule with TWO busy days
    existing_schedule = {
        "busy_days": [
            "Wednesday",
            "Friday"
        ]
    }

    agent = StudyPlannerAgent(existing_schedule)

    print("========== STUDENT REQUIREMENTS ==========")

    print(
        json.dumps(
            SIMULATED_ANSWERS,
            indent=4
        )
    )

    print("\n========== EXISTING SCHEDULE ==========")

    print(
        json.dumps(
            existing_schedule,
            indent=4
        )
    )

    # Run the agent
    print("\n========== RUNNING STUDY PLANNER AGENT ==========")

    plan = agent.run()

    # Display final result
    print("\n========== FINAL RESULT ==========")

    if plan is None:

        print("Study plan was NOT generated.")

        print("Reason: Scheduling conflicts must be resolved.")

    else:

        print("Study plan generated successfully.")

        print(json.dumps(plan, indent=4))

    # --------------------------------------------------
    # Display full iteration log
    # --------------------------------------------------

    print("\n========== FULL ITERATION LOG ==========")

    for entry in agent.log:

        print(
            json.dumps(
                entry,
                indent=4
            )
        )

    # --------------------------------------------------
    # Final verification
    # --------------------------------------------------

    print("\n========== VERIFICATION ==========")

    print(
        "Conflicts detected:",
        plan is None
    )

    print(
        "Schedule generated:",
        agent.goal["schedule_generated"]
    )

    print(
        "Final plan:",
        agent.plan
    )
