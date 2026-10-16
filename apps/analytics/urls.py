from django.urls import path
from .views import AnalyticsView, ClickAnalyticsView, ImpactAnalyticsView, RecordClickView

urlpatterns = [
    path('', AnalyticsView.as_view(), name='analytics-overview'),
    path('impact/', ImpactAnalyticsView.as_view(), name='impact-analytics'),
    path('click/', RecordClickView.as_view(), name='record-click'),
    path('clicks/', ClickAnalyticsView.as_view(), name='click-analytics'),
]
