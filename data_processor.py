import pandas as pd

def normalize_monday_data(raw_data):
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
                # Strip extra spaces to save tokens
                val = str(col.get("text") or "N/A").strip()
                row[col_key] = val
            flat_items.append(row)
        processed_boards[board_name] = flat_items
    return processed_boards

def get_data_quality_report(processed_data):
    # Shorten the report to save space
    caveats = []
    for board_name, items in processed_data.items():
        if not items: caveats.append(f"{board_name} empty")
    return caveats