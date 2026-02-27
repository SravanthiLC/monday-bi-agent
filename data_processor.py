
import pandas as pd
import json

def normalize_monday_data(raw_data):
    """
    Parses Monday.com's nested JSON into a clean list of dictionaries.
    Handles missing values and standardizes column names.
    """
    processed_boards = {}
    
    boards = raw_data.get("data", {}).get("boards", [])
    
    for board in boards:
        board_name = board["name"]
        items = board.get("items_page", {}).get("items", [])
        
        rows = []
        for item in items:
            # Start with basic info
            row = {"item_name": item["name"]}
            
            # Flatten column values
            for col in item.get("column_values", []):
                # We use 'text' for a human-readable version of the data
                col_id = col["id"]
                col_value = col.get("text")
                
                # Handle nulls/missing data immediately
                if col_value is None or col_value == "":
                    col_value = "N/A"
                
                row[col_id] = col_value
            
            rows.append(row)
        
        processed_boards[board_name] = rows
        
    return processed_boards

def get_data_quality_report(processed_data):
    """
    Quickly scans data for missing fields to provide 'Caveats' to the LLM.
    """
    caveats = []
    for board, rows in processed_data.items():
        if not rows:
            caveats.append(f"Board '{board}' is empty.")
            continue
            
        # Check for N/As in critical columns like 'Status' or 'Value'
        df = pd.DataFrame(rows)
        null_counts = (df == "N/A").sum()
        for col, count in null_counts.items():
            if count > 0:
                caveats.append(f"Board '{board}', Column '{col}' has {count} missing values.")
                
    return caveats

def clean_for_llm(raw_data):
    """
    Minimizes the data size by removing IDs and only keeping 
    essential text fields.
    """
    simplified_data = []
    boards = raw_data.get("data", {}).get("boards", [])
    
    for board in boards:
        board_info = {"board_name": board["name"], "items": []}
        for item in board.get("items_page", {}).get("items", []):
            # Create a compact dictionary for each row
            compact_item = {"name": item["name"]}
            for col in item.get("column_values", []):
                # Only add if there is actual text content
                if col.get("text"):
                    compact_item[col["id"]] = col["text"]
            board_info["items"].append(compact_item)
        simplified_data.append(board_info)
        
    return simplified_data