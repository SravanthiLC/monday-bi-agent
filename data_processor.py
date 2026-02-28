import pandas as pd

def normalize_monday_data(raw_data):
    """
    Transforms and cleans Monday.com data.
    Requirement: Automatically ignores/removes columns that are mostly empty (N/A).
    """
    processed_boards = {}
    boards = raw_data.get("data", {}).get("boards", [])
    
    for board in boards:
        board_name = board["name"]
        items = board.get("items_page", {}).get("items", [])
        
        flat_items = []
        for item in items:
            row = {"Item": item["name"]}
            for col in item.get("column_values", []):
                col_key = col.get("column", {}).get("title") or col.get("id")
                val = str(col.get("text") or "N/A").strip()
                row[col_key] = val
            flat_items.append(row)
        
        if not flat_items:
            continue

        # Convert to DataFrame to perform high-level cleaning
        df = pd.DataFrame(flat_items)

        # 1. REMOVE USELESS COLUMNS: 
        # If a column is 90% or more "N/A", it's noise. Drop it.
        na_threshold = 0.9
        cols_to_keep = []
        for col in df.columns:
            na_count = (df[col] == "N/A").sum()
            if (na_count / len(df)) < na_threshold:
                cols_to_keep.append(col)
        
        df_cleaned = df[cols_to_keep]

        # 2. REMOVE COLUMNS WITH NO VARIANCE:
        # If every single row has the exact same value, it's usually not useful for BI.
        # (Optional: uncomment below if you want to be even more aggressive)
        # df_cleaned = df_cleaned.loc[:, df_cleaned.nunique() > 1]

        processed_boards[board_name] = df_cleaned.to_dict('records')
        
    return processed_boards

def get_data_quality_report(processed_data):
    """Returns a short list of warnings about missing data."""
    caveats = []
    for board_name, items in processed_data.items():
        if not items:
            caveats.append(f"Board '{board_name}' filtered out (no valid data).")
    return caveats