from html import escape

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions, status, pagination, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from .models import HopeJourney, HopefulBeginningCompletion, EmailTemplate
from .serializers import HopeJourneySerializer, EmailTemplateSerializer
from rest_framework.views import APIView

from common.email_copy import copy_for, site_path
from common.email_parts import BROWN, page_html
from common.utils import get_site_url

class HopeJourneyPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

from common.throttles import StrictPublicFormThrottle

class HopeJourneyViewSet(viewsets.ModelViewSet):
    queryset = HopeJourney.objects.all()
    serializer_class = HopeJourneySerializer
    pagination_class = HopeJourneyPagination
    throttle_classes = [StrictPublicFormThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        'is_active': ['exact'],
        'created_at': ['gte', 'lte'],
    }
    search_fields = ['first_name', 'last_name', 'email']

    def get_permissions(self):
        # Anyone can join the journey (create)
        if self.action == 'create':
            return [permissions.AllowAny()]
        # Only admin can list, retrieve, update or delete subscriptions
        return [permissions.IsAdminUser()]

    def create(self, request, *args, **kwargs):
        # Someone who signed up before (and finished or stopped) starts again
        # from day 1 instead of hitting "this email is taken". The answer is
        # the same either way, so it doesn't tell whether an address signed up.
        email = str(request.data.get('email', '')).strip()
        existing = HopeJourney.objects.filter(email__iexact=email).first() if email else None
        serializer = self.get_serializer(existing, data=request.data) if existing else self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        from .tasks import send_welcome_and_day_one

        if existing and existing.is_active:
            subscriber = serializer.save()
        else:
            subscriber = serializer.save(current_day=1, is_active=True, finished_at=None)
            send_welcome_and_day_one.delay(subscriber.id)

        response = Response(serializer.data, status=status.HTTP_201_CREATED)
        response.data['message'] = copy_for(subscriber.lang).DAILY['welcome']
        return response

class HopefulBeginningCompletionView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        HopefulBeginningCompletion.objects.create()
        return Response({"message": "Hopeful Beginning completion recorded."}, status=status.HTTP_201_CREATED)


class EmailTemplateViewSet(viewsets.ModelViewSet):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = None  # Small number of templates, no need for pagination
    
    def get_queryset(self):
        return EmailTemplate.objects.all().order_by('day_number')

    def perform_update(self, serializer):
        # Saving new words makes them that day's English email, unless the
        # dashboard says otherwise (switching back to the built-in day).
        if 'is_active' not in self.request.data and (
            'subject' in self.request.data or 'html_content' in self.request.data
        ):
            serializer.save(is_active=True)
        else:
            serializer.save()


@method_decorator(csrf_exempt, name='dispatch')
class StopDailyHopeView(View):
    """
    The link at the bottom of every Daily Hope email. Opening it asks first,
    so a mail scanner that follows links can't stop anyone's emails; the
    button (or a mail app's one-tap unsubscribe) posts back here to stop.
    """

    def get(self, request, pk):
        subscriber = get_object_or_404(HopeJourney, pk=pk)
        c = copy_for(subscriber.lang).DAILY
        if not subscriber.is_active:
            return self._done(subscriber)
        return self._page(subscriber, c['stop_confirm'], f"""
            <form method="post" style="margin: 24px 0 0;">
                <button type="submit" style="background-color: {BROWN}; color: #ffffff; border: 0; padding: 14px 24px; border-radius: 12px; font-weight: 700; font-size: 16px; cursor: pointer;">{escape(c['stop'])}</button>
            </form>
        """)

    def post(self, request, pk):
        subscriber = get_object_or_404(HopeJourney, pk=pk)
        if subscriber.is_active:
            subscriber.is_active = False
            subscriber.save(update_fields=['is_active', 'updated_at'])
        return self._done(subscriber)

    def _done(self, subscriber):
        c = copy_for(subscriber.lang).DAILY
        home = get_site_url(site_path(subscriber.lang, '/'))
        return self._page(subscriber, c['stopped_title'], f"""
            <p style="margin: 12px 0 0;">{escape(c['stopped_text'])}</p>
            <p style="margin: 24px 0 0;"><a href="{home}" style="color: {BROWN}; font-weight: 700;">{escape(c['stopped_back'])}</a></p>
        """)

    def _page(self, subscriber, title, body):
        html = page_html(f"""
            <p style="margin: 0; font-weight: 700;">HopeBegins</p>
            <h1 style="font-family: Georgia, 'Times New Roman', serif; font-weight: 400; font-size: 30px; line-height: 1.15; margin: 20px 0 0;">{escape(title)}</h1>
            {body}
        """, subscriber.lang)
        head = '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex"><title>HopeBegins</title>'
        return HttpResponse(html.replace('<body', f'<head>{head}</head><body', 1))
