import os
import requests
from dotenv import load_dotenv

load_dotenv()

MONDAY_API_KEY = os.getenv("MONDAY_API_KEY")
API_URL = "https://api.monday.com/v2"

DEALS_BOARD_ID = 5026893490
WORK_ORDERS_BOARD_ID = 5026893371


def fetch_boards_data():
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
              value
            }}
          }}
        }}
      }}
    }}
    """

    headers = {
        "Authorization": MONDAY_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(API_URL, json={"query": query}, headers=headers)

    if response.status_code != 200:
        raise Exception("Failed to fetch data from Monday")

    return response.json()