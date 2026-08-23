import pandas as pd

from src.feedback import apply_feedback


def test_empty_feedback_does_not_change_scores():

    ranked = pd.DataFrame(
        {
            "case_id": ["C-1", "C-2"],
            "investigation_score": [0.8, 0.6],
        }
    )

    feedback = pd.DataFrame(
        columns=[
            "case_id",
            "feedback_type",
            "reason",
            "signal_category",
            "action",
        ]
    )

    result = apply_feedback(
        ranked,
        feedback,
    )

    assert list(
        result["investigation_score"]
    ) == [0.8, 0.6]


def test_false_positive_feedback_changes_score():

    ranked = pd.DataFrame(
        {
            "case_id": ["C-33248", "C-2"],
            "investigation_score": [0.8, 0.6],
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
            "action": ["downweight"],
        }
    )

    result = apply_feedback(
        ranked,
        feedback,
    )

    affected = result[
        result["case_id"] == "C-33248"
    ].iloc[0]

    assert affected["adjusted_score"] < 0.8


def test_feedback_does_not_retrain_or_modify_base_score():

    ranked = pd.DataFrame(
        {
            "case_id": ["C-33248"],
            "investigation_score": [0.8],
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
            "action": ["downweight"],
        }
    )

    result = apply_feedback(
        ranked,
        feedback,
    )

    assert result.iloc[0][
        "investigation_score"
    ] == 0.8
