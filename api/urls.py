from django.urls import path
from .views import AudienceListView, AudienceCreativesView, CampaignPushView

urlpatterns = [
    path('audiences/', AudienceListView.as_view(), name='audience-list'),
    path('audiences/<str:audience_id>/creatives/', AudienceCreativesView.as_view(), name='audience-creatives'),
    path('campaigns/', CampaignPushView.as_view(), name='campaign-push'),
]
