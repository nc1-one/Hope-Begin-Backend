from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HopeJourneyViewSet, HopefulBeginningCompletionView, EmailTemplateViewSet, StopDailyHopeView

router = DefaultRouter()
router.register(r'journeys', HopeJourneyViewSet, basename='hope-journey')
router.register(r'templates', EmailTemplateViewSet, basename='email-template')

urlpatterns = [
    path('stop/<uuid:pk>/', StopDailyHopeView.as_view(), name='daily-hope-stop'),
    path('hopeful-beginning-complete/', HopefulBeginningCompletionView.as_view(), name='hopeful_beginning_complete'),
    path('', include(router.urls)),
]
