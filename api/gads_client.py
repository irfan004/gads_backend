import os
from google.ads.googleads.client import GoogleAdsClient
from django.conf import settings

def get_google_ads_client():
    """
    Initializes and returns the Google Ads client using the local yaml config.
    """
    yaml_path = os.path.join(settings.BASE_DIR, 'google-ads.yaml')
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"Google Ads configuration file not found at {yaml_path}")
    
    return GoogleAdsClient.load_from_storage(yaml_path, version="v17")
