# Google Ads API Backend (Django)

This is the backend for the AI DataQuark Growth Campaign tool. It provides endpoints for fetching Google Ads audiences, their associated creatives, and pushing test campaigns.

## Setup Instructions

1.  **Activate Virtual Environment**:
    Ensure your virtual environment is active.
    ```bash
    .\venv\Scripts\activate
    ```

2.  **Configure Google Ads API Credentials**:
    Open the `google-ads.yaml` file located in the root of the project.
    Replace the placeholder values with your **Production Account** credentials:
    - `developer_token`
    - `client_id`
    - `client_secret`
    - `refresh_token`
    - `login_customer_id`

3.  **Run the Server**:
    ```bash
    python manage.py runserver
    ```
    The server will start at `http://127.0.0.1:8000/`.

## API Endpoints

### 1. Fetch Audiences
- **URL:** `GET /api/audiences/`
- **Optional Query Params:** `?prefix=ML` (filters audiences starting with 'ML')
- **Response Example:**
  ```json
  [
    {
      "id": 123456789,
      "name": "ML - High Intent Travel",
      "description": "Users interested in travel",
      "size": 50000
    }
  ]
  ```

### 2. Fetch Audience Creatives
- **URL:** `GET /api/audiences/<audience_id>/creatives/`
- **Description:** Fetches ads linked to ad groups that target the specified audience.
- **Response Example:**
  ```json
  {
    "creatives": [
      {
        "id": 987654321,
        "name": "Creative_12_V1",
        "type": "RESPONSIVE_SEARCH_AD",
        "final_urls": ["https://example.com/travel"]
      }
    ]
  }
  ```

### 3. Push Campaign
- **URL:** `POST /api/campaigns/`
- **Body (JSON):**
  ```json
  {
      "campaign_name": "AI DataQuark Growth Campaign",
      "daily_budget": "75000.00",
      "bidding_strategy": "TARGET_CPA",
      "location": "India",
      "start_date": "2026-05-06",
      "end_date": "2026-05-30"
  }
  ```
- **Description:** Saves the campaign locally (SQLite) and pushes a paused test campaign to Google Ads.
- **Response Example:**
  ```json
  {
    "message": "Campaign settings saved and test campaign pushed successfully.",
    "local_id": 1,
    "google_ads_campaign_resource_name": "customers/1234567890/campaigns/987654321"
  }
  ```
