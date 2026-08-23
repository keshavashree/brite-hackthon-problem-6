import pandas as pd
import os

def analyze_fairness(ranked_cases: pd.DataFrame, output_dir: str = "output") -> pd.DataFrame:
    """
    Examine the distribution of prioritised cases across demographic groups.
    
    Returns a DataFrame summarizing representation and selection rates.
    """
    df = ranked_cases.copy()
    
    # ---------------------------------------------------------
    # Merge demographic columns if not present
    # ---------------------------------------------------------
    demographic_cols = ["language_preference", "age_band", "district"]
    if not all(col in df.columns for col in demographic_cols):
        from src.data_loader import load_cases
        cases = load_cases()
        df = df.merge(
            cases[["case_id"] + [c for c in demographic_cols if c not in df.columns]],
            on="case_id",
            how="left"
        )
        
    total_cases = len(df)
    top_20_ids = set(df.head(20)["case_id"])
    top_100_ids = set(df.head(100)["case_id"])
    
    rows = []
    
    for col in demographic_cols:
        if col not in df.columns:
            continue
            
        # Get overall counts
        counts = df[col].value_counts()
        
        for val, pop_count in counts.items():
            # Get cases in this group
            group_df = df[df[col] == val]
            group_case_ids = set(group_df["case_id"])
            
            top_20_count = len(group_case_ids.intersection(top_20_ids))
            top_100_count = len(group_case_ids.intersection(top_100_ids))
            
            rows.append({
                "demographic_dimension": col,
                "group_value": str(val),
                "population_count": pop_count,
                "population_share": pop_count / total_cases,
                "top_20_count": top_20_count,
                "top_20_selection_rate": top_20_count / pop_count if pop_count > 0 else 0.0,
                "top_100_count": top_100_count,
                "top_100_selection_rate": top_100_count / pop_count if pop_count > 0 else 0.0,
            })
            
    report = pd.DataFrame(rows)
    
    # Ensure output directory exists and save CSV
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    report.to_csv(os.path.join(output_dir, "fairness_report.csv"), index=False)
    
    return report
