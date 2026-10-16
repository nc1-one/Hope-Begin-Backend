from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import HopeStory
from .serializers import HopeStorySerializer, PublicHopeStorySerializer, HopeStoryCreateSerializer
from common.throttles import StrictPublicFormThrottle

class HopeStoryViewSet(viewsets.ModelViewSet):
    queryset = HopeStory.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['full_name', 'testimonial', 'occupation']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return HopeStoryCreateSerializer
        if self.action == 'approved':
            return PublicHopeStorySerializer
        return HopeStorySerializer

    def get_permissions(self):
        # Anyone can submit a story or read the approved ones
        if self.action in ['create', 'approved']:
            return [permissions.AllowAny()]
        # Reviewing, editing and deleting stories is for the admin team only
        return [permissions.IsAdminUser()]

    def get_throttles(self):
        if self.action == 'create':
            return [StrictPublicFormThrottle()]
        return super().get_throttles()

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def approved(self, request):
        approved_stories = HopeStory.objects.filter(status='APPROVED').order_by('-created_at')
        page = self.paginate_queryset(approved_stories)
        if page is not None:
            serializer = PublicHopeStorySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PublicHopeStorySerializer(approved_stories, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # Return the created story data (or a subset)
        data = PublicHopeStorySerializer(serializer.instance).data
        response = Response(data, status=status.HTTP_201_CREATED, headers=headers)
        response.message = "Your hope story has been submitted for review. Thank you for sharing!"
        return response
