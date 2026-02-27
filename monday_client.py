import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Configuration from .env
MONDAY_API_KEY = os.getenv("MONDAY_API_KEY")
API_URL = "https://api.monday.com/v2"

# Board IDs provided in your assessment
DEALS_BOARD_ID = 5026893490
WORK_ORDERS_BOARD_ID = 5026893371

def fetch_boards_data():
    """
    Fetches live data from Monday.com boards.
    Includes 'column title' expansion so the AI sees human-readable names.
    """
    query = f"""
    {{
      boards (ids: [{DEALS_BOARD_ID}, {WORK_ORDERS_BOARD_ID}]) {{
        id
        name
        items_page(limit: 100) {{
          items {{
            id
            name
            column_values {{
              id
              text
              column {{
                title
              }}
            }}
          }}
        }}
      }}
    }}
    """

    headers = {
        "Authorization": MONDAY_API_KEY,
        "Content-Type": "application/json",
        "API-Version": "2024-01"  # Ensures compatibility with items_page
    }

    try:
        response = requests.post(API_URL, json={"query": query}, headers=headers)
        response.raise_for_status() # Raises an error for 4XX or 5XX status codes
        
        data = response.json()
        
        # Basic error handling for Monday-specific API errors
        if "errors" in data:
            raise Exception(f"Monday API Error: {data['errors'][0]['message']}")
            
        return data

    except requests.exceptions.RequestException as e:
        raise Exception(f"Connection Error: Could not connect to Monday.com. {e}")