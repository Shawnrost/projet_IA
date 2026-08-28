from django.urls import path
from .views import ChurnPredictionView

urlpatterns = [
    path("predict/", ChurnPredictionView.as_view(), name="churn-predict"),
]