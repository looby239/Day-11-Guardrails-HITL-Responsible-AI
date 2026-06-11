"""
Lab 11 — Part 4: Human-in-the-Loop Design
  TODO 12: Confidence Router
  TODO 13: Design 3 HITL decision points
"""
from dataclasses import dataclass


# ============================================================
# TODO 12: Implement ConfidenceRouter
#
# Route agent responses based on confidence scores:
#   - HIGH (>= 0.9): Auto-send to user
#   - MEDIUM (0.7 - 0.9): Queue for human review
#   - LOW (< 0.7): Escalate to human immediately
#
# Special case: if the action is HIGH_RISK (e.g., money transfer,
# account deletion), ALWAYS escalate regardless of confidence.
#
# Implement the route() method.
# ============================================================

HIGH_RISK_ACTIONS = [
    "transfer_money",
    "close_account",
    "change_password",
    "delete_data",
    "update_personal_info",
]


@dataclass
class RoutingDecision:
    """Result of the confidence router."""
    action: str          # "auto_send", "queue_review", "escalate"
    confidence: float
    reason: str
    priority: str        # "low", "normal", "high"
    requires_human: bool


class ConfidenceRouter:
    """Route agent responses based on confidence and risk level.

    Thresholds:
        HIGH:   confidence >= 0.9 -> auto-send
        MEDIUM: 0.7 <= confidence < 0.9 -> queue for review
        LOW:    confidence < 0.7 -> escalate to human

    High-risk actions always escalate regardless of confidence.
    """

    HIGH_THRESHOLD = 0.9
    MEDIUM_THRESHOLD = 0.7

    def route(self, response: str, confidence: float,
              action_type: str = "general") -> RoutingDecision:
        """Route a response based on confidence score and action type.

        Args:
            response: The agent's response text
            confidence: Confidence score between 0.0 and 1.0
            action_type: Type of action (e.g., "general", "transfer_money")

        Returns:
            RoutingDecision with routing action and metadata
        """
        if action_type in HIGH_RISK_ACTIONS:
            action = "escalate"
            priority = "high"
            requires_human = True
            reason = f"High-risk action '{action_type}' requires human approval"
        elif confidence >= self.HIGH_THRESHOLD:
            action = "auto_send"
            priority = "low"
            requires_human = False
            reason = f"High confidence ({confidence:.2f}) >= threshold ({self.HIGH_THRESHOLD})"
        elif confidence >= self.MEDIUM_THRESHOLD:
            action = "queue_review"
            priority = "normal"
            requires_human = True
            reason = f"Medium confidence ({confidence:.2f}) between {self.MEDIUM_THRESHOLD} and {self.HIGH_THRESHOLD}"
        else:
            action = "escalate"
            priority = "high"
            requires_human = True
            reason = f"Low confidence ({confidence:.2f}) < threshold ({self.MEDIUM_THRESHOLD})"

        return RoutingDecision(
            action=action,
            confidence=confidence,
            reason=reason,
            priority=priority,
            requires_human=requires_human
        )


# ============================================================
# TODO 13: Design 3 HITL decision points
#
# For each decision point, define:
# - trigger: What condition activates this HITL check?
# - hitl_model: Which model? (human-in-the-loop, human-on-the-loop,
#   human-as-tiebreaker)
# - context_needed: What info does the human reviewer need?
# - example: A concrete scenario
#
# Think about real banking scenarios where human judgment is critical.
# ============================================================

hitl_decision_points = [
    {
        "id": 1,
        "name": "High-Value Money Transfer Approval",
        "trigger": "Transfer amount > 50,000,000 VND OR cumulative daily transfers > 100,000,000 VND",
        "hitl_model": "human-as-tiebreaker",
        "context_needed": "Customer account balance, transaction history (last 7 days), recipient account details, transfer purpose, fraud risk score, customer KYC verification level.",
        "example": "Customer requests to transfer 120,000,000 VND to a newly registered recipient account.",
    },
    {
        "id": 2,
        "name": "Sensitive Personal Information Update",
        "trigger": "Change of primary contact details (phone, email) OR updates to KYC fields.",
        "hitl_model": "human-in-the-loop",
        "context_needed": "Current customer information, photo of ID documents, selfie verification match, previous change timestamps, recent login IP/device history.",
        "example": "Customer requests to change their registered phone number via chat after logging in from a new device.",
    },
    {
        "id": 3,
        "name": "Account Closure & Balance Withdrawal",
        "trigger": "Account closure requests OR account deactivation with outstanding balances.",
        "hitl_model": "human-as-tiebreaker",
        "context_needed": "Current account balance, outstanding loans or unpaid credit cards, active recurring payments, customer tier (VIP/Regular), closure reasoning.",
        "example": "Customer wants to close their bank account which has a remaining balance of 5,000,000 VND and a linked credit card.",
    },
]


# ============================================================
# Quick tests
# ============================================================

def test_confidence_router():
    """Test ConfidenceRouter with sample scenarios."""
    router = ConfidenceRouter()

    test_cases = [
        ("Balance inquiry", 0.95, "general"),
        ("Interest rate question", 0.82, "general"),
        ("Ambiguous request", 0.55, "general"),
        ("Transfer $50,000", 0.98, "transfer_money"),
        ("Close my account", 0.91, "close_account"),
    ]

    print("Testing ConfidenceRouter:")
    print("=" * 80)
    print(f"{'Scenario':<25} {'Conf':<6} {'Action Type':<18} {'Decision':<15} {'Priority':<10} {'Human?'}")
    print("-" * 80)

    for scenario, conf, action_type in test_cases:
        decision = router.route(scenario, conf, action_type)
        print(
            f"{scenario:<25} {conf:<6.2f} {action_type:<18} "
            f"{decision.action:<15} {decision.priority:<10} "
            f"{'Yes' if decision.requires_human else 'No'}"
        )

    print("=" * 80)


def test_hitl_points():
    """Display HITL decision points."""
    print("\nHITL Decision Points:")
    print("=" * 60)
    for point in hitl_decision_points:
        print(f"\n  Decision Point #{point['id']}: {point['name']}")
        print(f"    Trigger:  {point['trigger']}")
        print(f"    Model:    {point['hitl_model']}")
        print(f"    Context:  {point['context_needed']}")
        print(f"    Example:  {point['example']}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_confidence_router()
    test_hitl_points()
