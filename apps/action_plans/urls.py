from django.urls import path
from .views import EmailActionPlanView

urlpatterns = [
    path('email/', EmailActionPlanView.as_view(), name='action-plan-email'),
]
