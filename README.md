# Google Ads API Backend (Django)

This is the backend for the AI DataQuark Growth Campaign tool. It provides endpoints for fetching Google Ads audiences, their associated creatives, and pushing test campaigns.

## Setup Instructions

1.  **Create and Activate Virtual Environment**:
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Apply Database Migrations**:
    ```bash
    python manage.py migrate
    ```

4.  **Configure Google Ads API Credentials**:
    Create a file named `google-ads.yaml` in the root of the project and add the following structure. Replace the placeholders with your actual **Production Account** credentials:
    ```yaml
    developer_token: "INSERT_DEVELOPER_TOKEN_HERE"
    client_id: "INSERT_OAUTH2_CLIENT_ID_HERE"
    client_secret: "INSERT_OAUTH2_CLIENT_SECRET_HERE"
    refresh_token: "INSERT_REFRESH_TOKEN_HERE"
    login_customer_id: "INSERT_LOGIN_CUSTOMER_ID_HERE"
    use_proto_plus: true
    ```

5.  **Run the Server**:
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
