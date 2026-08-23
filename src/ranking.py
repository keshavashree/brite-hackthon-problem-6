import pandas as pd
import numpy as np

def calculate_rankings(signals: pd.DataFrame) -> pd.DataFrame:
    """
    Apply weighted ranking to prioritize benefit cases for human review.
    
    Weights reflect signal severity while avoiding administrative bias.
    """
    ranked = signals.copy()
    
    # ---------------------------------------------------------
    # 1. Define signal weights
    # ---------------------------------------------------------
    weights = {
        "extreme_deviation_signal": 2.5,
        "award_deviation_signal": 2.0,
        "severe_persistence_signal": 2.0,
        "duplicate_payment_signal": 2.0,
        "persistence_signal": 1.5,
        "multiple_payment_signal": 1.0,
        "monthly_change_signal": 1.0
    }
    
    # Calculate weighted sum
    weighted_sum = 0.0
    total_weight = 0.0
    for col, weight in weights.items():
        if col in ranked.columns:
            weighted_sum += ranked[col] * weight
            total_weight += weight
            
    # Normalize score to 0.0 - 1.0
    if total_weight > 0:
        ranked["prioritisation_score"] = weighted_sum / total_weight
    else:
        ranked["prioritisation_score"] = 0.0
        
    # ---------------------------------------------------------
    # 2. Sort and assign ranks
    # Sort by prioritisation_score (descending) and case_id (ascending for tie-breaking)
    # ---------------------------------------------------------
    ranked = ranked.sort_values(
        by=["prioritisation_score", "case_id"],
        ascending=[False, True]
    ).reset_index(drop=True)
    
    ranked["rank"] = ranked.index + 1
    
    return ranked
