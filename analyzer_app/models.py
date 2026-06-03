from django.db import models
from django.contrib.auth.models import User

class FoodHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_name = models.CharField(max_length=100)
    confidence = models.FloatField()
    calories = models.IntegerField(null=True, blank=True)
    protein = models.FloatField(null=True, blank=True)
    fat = models.FloatField(null=True, blank=True)
    carbs = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.food_name}"
    
class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    height = models.FloatField(null=True, blank=True)

    weight = models.FloatField(null=True, blank=True)

    age = models.IntegerField(null=True, blank=True)

    gender = models.CharField(max_length=10, blank=True)

    bmi = models.FloatField(null=True, blank=True)

    bmi_category = models.CharField(max_length=30, blank=True)
    
    
class UserBadge(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    badge_name = models.CharField(
        max_length=100
    )

    earned_at = models.DateTimeField(
        auto_now_add=True
    )
    
    def __str__(self):
        return f"{self.user.username} - {self.badge_name}"