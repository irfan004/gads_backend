from django.db import models

class CampaignSetting(models.Model):
    BIDDING_STRATEGIES = [
        ('MAX_CONVERSIONS', 'Max Conversions'),
        ('TARGET_CPA', 'Target CPA'),
        ('TARGET_ROAS', 'Target ROAS'),
    ]

    campaign_name = models.CharField(max_length=255)
    daily_budget = models.DecimalField(max_digits=15, decimal_places=2)
    bidding_strategy = models.CharField(max_length=50, choices=BIDDING_STRATEGIES)
    location = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.campaign_name
