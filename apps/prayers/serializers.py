from rest_framework import serializers

from apps.action_plans.serializers import country_field
from common.email_copy import LANGUAGES
from .models import Prayer, PrayerResponse, Organization
from django.contrib.auth import get_user_model

User = get_user_model()

class PrayerResponseSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = PrayerResponse
        fields = ('id', 'prayer', 'content', 'user', 'user_email', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'name', 'description', 'is_active', 'created_at', 'updated_at')

class PrayerSerializer(serializers.ModelSerializer):
    responses = PrayerResponseSerializer(many=True, read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    assigned_to_email = serializers.EmailField(source='assigned_to.email', read_only=True)
    
    # CamelCase fields for frontend compatibility
    isAnonymous = serializers.BooleanField(source='is_anonymous', required=False)
    shareFirstName = serializers.BooleanField(source='share_first_name', required=False)
    wantsFollowUp = serializers.BooleanField(source='wants_follow_up', required=False)
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)
    lastNameHoney = serializers.CharField(required=False, allow_blank=True, write_only=True)
    startTime = serializers.IntegerField(required=False, write_only=True)
    
    # Organization fields
    organizationId = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.filter(is_active=True),
        source='organization',
        required=False,
        allow_null=True,
        write_only=True
    )
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    lang = serializers.ChoiceField(choices=LANGUAGES, default='en', write_only=True)
    country = country_field()

    class Meta:
        model = Prayer
        fields = (
            'id', 'title', 'email', 'content', 'category', 'category_display', 'lang', 'country',
            'isAnonymous', 'shareFirstName', 'wantsFollowUp', 
            'status', 'assigned_to', 'assigned_to_email', 
            'user', 'created_at', 'updated_at', 'responses',
            'website', 'lastNameHoney', 'startTime',
            'organizationId', 'organization_name'
        )
        read_only_fields = (
            'id', 'status', 'assigned_to', 'user', 
            'created_at', 'updated_at', 'responses'
        )

    def validate(self, data):
        from common.utils import validate_form_time, check_spam_keywords
        
        # Honeypot checks
        if data.get('website') or data.get('lastNameHoney'):
            raise serializers.ValidationError("Anti-spam: Bot detected.")
        
        # Keyword filtering
        if check_spam_keywords(data.get('content', '')):
            raise serializers.ValidationError({"content": "Your submission contains restricted keywords. Please revise and try again."})
        
        # Time-based validation
        start_time = data.get('startTime')
        if not validate_form_time(start_time):
            raise serializers.ValidationError("Anti-spam: Form submitted too quickly.")
            
        # Remove fields so they don't get passed to the model
        data.pop('website', None)
        data.pop('lastNameHoney', None)
        data.pop('startTime', None)
        data['country'] = data.get('country', '').upper()
        return data

class AdminPrayerSerializer(serializers.ModelSerializer):
    responses = PrayerResponseSerializer(many=True, read_only=True)
    assigned_to_email = serializers.EmailField(source='assigned_to.email', read_only=True)
    
    # CamelCase fields for frontend compatibility
    isAnonymous = serializers.BooleanField(source='is_anonymous', required=False)
    shareFirstName = serializers.BooleanField(source='share_first_name', required=False)
    wantsFollowUp = serializers.BooleanField(source='wants_follow_up', required=False)

    # Organization fields
    organizationId = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        source='organization',
        required=False,
        allow_null=True,
        write_only=True
    )
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = Prayer
        fields = (
            'id', 'title', 'email', 'content', 'category', 
            'isAnonymous', 'shareFirstName', 'wantsFollowUp', 
            'status', 'assigned_to', 'assigned_to_email', 
            'user', 'created_at', 'updated_at', 'responses',
            'organizationId', 'organization_name'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'responses')
