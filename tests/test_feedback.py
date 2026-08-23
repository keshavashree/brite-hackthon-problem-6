import pandas as pd

from src.feedback import (
    build_signal_adjustments,
    apply_feedback,
)


def test_feedback_category_is_converted_to_adjustment():

    feedback = pd.DataFrame(
        {
            "case_id": ["C-33248"],
            "feedback_type": ["false_positive"],
            "reason": [
                "Administrative activity"
            ],
            "signal_category": [
                "administrative_activity"
            ],
            "action": [
                "exclude_from_risk"
            ],
        }
    )

    adjustments = build_signal_adjustments(
        feedback
    )

    assert adjustments[
        "administrative_activity"
    ] == 0.0


def test_feedback_does_not_change_base_score():

    ranked = pd.DataFrame(
        {
            "case_id": ["C-33248"],
            "investigation_score": [0.8],
            "award_deviation_signal": [0.0],
            "persistence_signal": [0.0],
            "duplicate_payment_signal": [0.0],
            "multiple_payment_signal": [0.0],
            "monthly_change_signal": [0.0],
        }
    )

    feedback = pd.DataFrame(
        {
            "case_id": ["C-33248"],
            "feedback_type": ["false_positive"],
            "reason": [
                "Administrative activity"
            ],
            "signal_category": [
                "administrative_activity"
            ],
            "action": [
                "exclude_from_risk"
            ],
        }
    )

    result = apply_feedback(
        ranked,
        feedback,
    )

    assert result.iloc[0][
        "investigation_score"
    ] == 0.8
