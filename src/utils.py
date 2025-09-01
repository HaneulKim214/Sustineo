import numpy as np
import pandas as pd

def df_to_text(grouped_df, value_cols=["CO2e_Tonnes"], decimal_places=2):
    """
    Convert a grouped DataFrame into a readable text format with automatic column names.
    
    Args:
        grouped_df (pd.DataFrame): Grouped DataFrame (can have any grouping columns).
        value_col (str): Column to display as the value.
        decimal_places (int): Decimal places for the value column.
        
    Returns:
        str: Formatted text.
    """
    grouped_df = grouped_df.reset_index()
    grouped_df[value_cols] = np.round(grouped_df[value_cols], decimal_places)
    
    # Determine all columns except the value column
    grp_cols = [col for col in grouped_df.columns if col not in value_cols]
    
    ## Improvements: Avoid loop, print whole dataframe at once or pass markdown table.
      # or vectorize string concatenation.
    text_output = ""
    for row in grouped_df.itertuples():
        row_text = ", ".join([f"{col}: {getattr(row, col)}" for col in grp_cols])
        for value_col in value_cols:
            row_text += f", {value_col}: {getattr(row, value_col)}"
        text_output += row_text + "\n"
        
    return text_output