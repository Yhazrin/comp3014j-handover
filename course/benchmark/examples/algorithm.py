# ======================= TEAM DETAILS (fill in before submitting) =======================
# Brightspace group:
# Members (name, student number):
#   1.
#   2.
#   3.
# ==========================================================================================
"""Always-stay starter: a runnable interface example, not a developed solution.

This policy never requests handover. The simulator still performs initial
attachment and recovery after radio link failure. On the supplied practice
suite it scores 84.93 against A3's 100: a 15.07% lower composite index.

Keep StudentPolicy, reset and decide, but develop your own decision rule
using the documented observation fields. See README.md and Document 2,
Section 9 for guidance. Explain and evaluate your changes in report.pdf.

Submitting this supplied sample as your solution fails the assignment,
regardless of its score or report mark. Changes only to names, comments
or formatting do not count as developing your own algorithm.
"""


class StudentPolicy:
    def reset(self, config: dict) -> None:
        # Initialise any per-device state your own policy needs here.
        pass

    def decide(self, observation: dict) -> dict:
        # Replace this with your own handover decision rule.
        return {"action": "stay"}
