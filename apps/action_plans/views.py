import hashlib
import logging

from django.core.cache import cache
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.throttles import ActionPlanEmailThrottle
from .emails import send_action_plan_email
from .serializers import EmailActionPlanSerializer

logger = logging.getLogger(__name__)

# Per-recipient cap on top of the per-IP throttle.
MAX_EMAILS_PER_ADDRESS_PER_DAY = 3


class EmailActionPlanView(APIView):
    """
    Emails a visitor the Hopeful Beginning Plan they built on /action-plan.
    Nothing is stored: the plan is rendered into the email and discarded.
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_classes = [ActionPlanEmailThrottle]

    def post(self, request):
        serializer = EmailActionPlanSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data

        address_key = 'action-plan-email:' + hashlib.sha256(
            data['email'].lower().encode()
        ).hexdigest()
        sent_today = cache.get(address_key, 0)
        if sent_today >= MAX_EMAILS_PER_ADDRESS_PER_DAY:
            return Response(
                {'message': 'This plan was already sent to this address today.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        try:
            send_action_plan_email(
                data['email'],
                data.get('first_name', '').strip(),
                data['summary'],
                data['sections'],
            )
        except Exception:
            logger.exception('Failed to send action plan email')
            return Response(
                {'message': 'We could not send the email right now.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        cache.set(address_key, sent_today + 1, timeout=60 * 60 * 24)
        return Response({'message': 'Plan sent.'}, status=status.HTTP_200_OK)
