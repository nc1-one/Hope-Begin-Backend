from django.urls import path
from .views import EmailActionPlanView, PlanCheckInView

urlpatterns = [
    path('email/', EmailActionPlanView.as_view(), name='action-plan-email'),
    path('check-in/', PlanCheckInView.as_view(), name='action-plan-check-in'),
]
