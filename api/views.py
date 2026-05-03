import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from google.ads.googleads.errors import GoogleAdsException
from .serializers import CampaignSettingSerializer
from .gads_client import get_google_ads_client

class AudienceListView(APIView):
    """
    Fetches up to 5 audiences from Google Ads.
    By default fetches any audience, but can filter by prefix (e.g., ?prefix=ML)
    """
    def get(self, request):
        prefix = request.query_params.get('prefix', '')
        
        try:
            client = get_google_ads_client()
            ga_service = client.get_service("GoogleAdsService")
            
            # The customer_id must be provided or derived. 
            # Usually, you get this from the client config or request.
            # Assuming login_customer_id or a fixed test customer id for now.
            # We'll need the user to provide the target customer_id, or we read it from config if available.
            # For this example, let's read the login_customer_id from the client config.
            customer_id = str(client.login_customer_id).replace("-", "") if client.login_customer_id else None
            
            if not customer_id:
                return Response({"error": "No login_customer_id found in config. Please specify customer_id."}, status=status.HTTP_400_BAD_REQUEST)

            query = """
                SELECT
                    user_list.id,
                    user_list.name,
                    user_list.description,
                    user_list.size_for_search
                FROM user_list
            """
            
            if prefix:
                query += f" WHERE user_list.name LIKE '{prefix}%'"
                
            query += " LIMIT 5"

            response = ga_service.search(customer_id=customer_id, query=query)
            
            audiences = []
            for row in response:
                audiences.append({
                    "id": row.user_list.id,
                    "name": row.user_list.name,
                    "description": row.user_list.description,
                    "size": row.user_list.size_for_search
                })
                
            return Response(audiences, status=status.HTTP_200_OK)

        except FileNotFoundError as e:
            return Response({"error": str(e), "message": "google-ads.yaml missing or incomplete."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except GoogleAdsException as e:
            error_message = ""
            for error in e.failure.errors:
                error_message += f"Error with message: {error.message}. "
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AudienceCreativesView(APIView):
    """
    Fetches creatives (ads/assets) associated with ad groups targeting the given audience_id.
    """
    def get(self, request, audience_id):
        try:
            client = get_google_ads_client()
            ga_service = client.get_service("GoogleAdsService")
            customer_id = str(client.login_customer_id).replace("-", "")
            
            if not customer_id:
                return Response({"error": "No login_customer_id found in config."}, status=status.HTTP_400_BAD_REQUEST)

            # Step 1: Find AdGroups that target this user_list (audience_id)
            ad_group_query = f"""
                SELECT ad_group.id
                FROM ad_group_criterion
                WHERE ad_group_criterion.user_list.user_list = 'customers/{customer_id}/userLists/{audience_id}'
            """
            ad_group_response = ga_service.search(customer_id=customer_id, query=ad_group_query)
            
            ad_group_ids = [str(row.ad_group.id) for row in ad_group_response]
            
            if not ad_group_ids:
                return Response({"message": "No ad groups found targeting this audience.", "creatives": []}, status=status.HTTP_200_OK)

            # Step 2: Fetch Ads (Creatives) for those AdGroups
            ad_group_ids_str = ", ".join(ad_group_ids)
            ads_query = f"""
                SELECT
                    ad_group_ad.ad.id,
                    ad_group_ad.ad.name,
                    ad_group_ad.ad.type,
                    ad_group_ad.ad.final_urls
                FROM ad_group_ad
                WHERE ad_group.id IN ({ad_group_ids_str})
                LIMIT 10
            """
            
            ads_response = ga_service.search(customer_id=customer_id, query=ads_query)
            
            creatives = []
            for row in ads_response:
                creatives.append({
                    "id": row.ad_group_ad.ad.id,
                    "name": row.ad_group_ad.ad.name,
                    "type": row.ad_group_ad.ad.type_.name,
                    "final_urls": list(row.ad_group_ad.ad.final_urls)
                })

            return Response({"creatives": creatives}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CampaignPushView(APIView):
    """
    Saves campaign settings to SQLite and pushes a test campaign to Google Ads.
    """
    def post(self, request):
        serializer = CampaignSettingSerializer(data=request.data)
        if serializer.is_valid():
            # Save locally to SQLite
            campaign_setting = serializer.save()
            
            # Push to Google Ads
            try:
                client = get_google_ads_client()
                customer_id = str(client.login_customer_id).replace("-", "")
                
                # 1. Create a Campaign Budget
                campaign_budget_service = client.get_service("CampaignBudgetService")
                campaign_budget_operation = client.get_type("CampaignBudgetOperation")
                campaign_budget = campaign_budget_operation.create
                campaign_budget.name = f"Test Budget {uuid.uuid4()}"
                campaign_budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
                campaign_budget.amount_micros = int(float(campaign_setting.daily_budget) * 1000000) # Convert to micros
                
                budget_response = campaign_budget_service.mutate_campaign_budgets(
                    customer_id=customer_id, operations=[campaign_budget_operation]
                )
                budget_resource_name = budget_response.results[0].resource_name

                # 2. Create the Campaign
                campaign_service = client.get_service("CampaignService")
                campaign_operation = client.get_type("CampaignOperation")
                campaign = campaign_operation.create
                campaign.name = campaign_setting.campaign_name + f" (Test Push {uuid.uuid4()})"
                # Status PAUSED to ensure it's just a test
                campaign.status = client.enums.CampaignStatusEnum.PAUSED
                campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
                
                # Bidding Strategy setup
                # Mapping user selection to simple strategies
                if campaign_setting.bidding_strategy == 'TARGET_CPA':
                    campaign.target_cpa.target_cpa_micros = 1000000  # Default 1 unit target CPA
                elif campaign_setting.bidding_strategy == 'TARGET_ROAS':
                    campaign.target_roas.target_roas = 1.0 # Default 1.0 ROAS
                else: # MAX_CONVERSIONS
                    campaign.maximize_conversions.target_cpa_micros = 0 # No specific target
                
                # Assign budget
                campaign.campaign_budget = budget_resource_name
                
                # Location (Targeting) and Schedule are omitted here for brevity as they require
                # creating specific CampaignCriterion objects for GeoTargeting.

                campaign_response = campaign_service.mutate_campaigns(
                    customer_id=customer_id, operations=[campaign_operation]
                )
                
                return Response({
                    "message": "Campaign settings saved and test campaign pushed successfully.",
                    "local_id": campaign_setting.id,
                    "google_ads_campaign_resource_name": campaign_response.results[0].resource_name
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                # If Google Ads push fails, we might want to log it or delete the local record.
                # For now, we just return the error.
                return Response({"error": str(e), "message": "Failed to push to Google Ads, but saved locally."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
