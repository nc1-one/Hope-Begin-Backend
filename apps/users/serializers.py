from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils.crypto import get_random_string
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['role'] = user.role
        token['email'] = user.email
        token['is_approved'] = user.is_approved
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        if not self.user.is_approved and self.user.role != 'admin':
            raise serializers.ValidationError({
                "detail": "Your account is pending admin approval."
            })

        # Add extra responses
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'username': self.user.username,
            'role': self.user.role,
            'is_approved': self.user.is_approved,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }
        return data

class UserSerializer(serializers.ModelSerializer):
    prayer_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'role', 'is_approved', 
            'first_name', 'last_name', 'phone', 'church_community', 
            'carrier_reason', 'agreed_to_guidelines', 'date_joined',
            'prayer_count'
        )
        read_only_fields = ('id', 'role', 'is_approved', 'date_joined', 'prayer_count')

    def get_prayer_count(self, obj):
        return obj.assigned_prayers.count()

class AdminUserSerializer(serializers.ModelSerializer):
    prayer_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'role', 'is_approved', 
            'first_name', 'last_name', 'phone', 'church_community', 
            'carrier_reason', 'agreed_to_guidelines', 'date_joined',
            'prayer_count'
        )
        read_only_fields = ('id', 'date_joined', 'prayer_count')

    def get_prayer_count(self, obj):
        return obj.assigned_prayers.count()

class StaffUserSerializer(AdminUserSerializer):
    """What a staff admin can change on a user. Roles stay with the super admin."""

    class Meta(AdminUserSerializer.Meta):
        read_only_fields = ('id', 'role', 'date_joined', 'prayer_count')

class AdminTeamSerializer(serializers.ModelSerializer):
    """One person on the admin team, as the super admin sees them."""
    has_password = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'role', 'is_active',
            'has_password', 'date_joined', 'last_login',
        )
        read_only_fields = fields

    def get_has_password(self, obj):
        # False until they open the invite link and set one.
        return obj.has_usable_password()

class AddStaffAdminSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField()

    def validate_email(self, value):
        value = value.strip().lower()
        existing = User.objects.filter(email__iexact=value).first()
        # Someone whose access was taken away can be added back.
        if existing and not (existing.role == 'staff' and not existing.is_active):
            raise serializers.ValidationError(
                "This email already has a HopeBegins account. Use a different email."
            )
        return value

    def create(self, validated_data):
        email = validated_data['email']
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            username = email
            while User.objects.filter(username=username).exists():
                username = f"{email}-{get_random_string(4).lower()}"
            user = User(username=username, email=email)
        user.first_name = validated_data['first_name'].strip()
        user.last_name = validated_data.get('last_name', '').strip()
        user.role = 'staff'
        user.is_staff = True
        user.is_superuser = False
        user.is_active = True
        user.is_approved = True
        # They choose their own password from the invite email.
        user.set_unusable_password()
        user.save()
        return user

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role='user',
            is_approved=False  # Registration must be approved by admin
        )
        return user

class AdminRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role='admin',
            is_staff=True,
            is_approved=True  # Admin users are pre-approved for now
        )
        return user

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

class ResetPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid token or user ID.")

        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError("Invalid or expired token.")

        attrs['user'] = user
        return attrs

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
class CarrierApplicationSerializer(serializers.ModelSerializer):
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)
    lastNameHoney = serializers.CharField(required=False, allow_blank=True, write_only=True)
    startTime = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 
            'phone', 'church_community', 'carrier_reason', 'agreed_to_guidelines',
            'website', 'lastNameHoney', 'startTime'
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'carrier_reason': {'required': True},
            'agreed_to_guidelines': {'required': True}
        }

    def validate_agreed_to_guidelines(self, value):
        if not value:
            raise serializers.ValidationError("You must agree to the guidelines to apply.")
        return value

    def validate(self, data):
        from common.utils import validate_form_time, check_spam_keywords

        # Honeypot checks
        if data.get('website') or data.get('lastNameHoney'):
            raise serializers.ValidationError("Anti-spam: Bot detected.")
            
        # Keyword filtering
        if check_spam_keywords(data.get('carrier_reason', '')):
            raise serializers.ValidationError({"carrier_reason": "Your application contains restricted keywords. Please revise and try again."})
            
        # Time-based validation
        start_time = data.get('startTime')
        if not validate_form_time(start_time):
            raise serializers.ValidationError("Anti-spam: Form submitted too quickly.")

        # Remove fields so they don't get passed to the model
        data.pop('website', None)
        data.pop('lastNameHoney', None)
        data.pop('startTime', None)
        return data

    def create(self, validated_data):
        # Create a user without a password (it will be set after approval)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=get_random_string(32),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
            church_community=validated_data.get('church_community', ''),
            carrier_reason=validated_data.get('carrier_reason', ''),
            agreed_to_guidelines=validated_data.get('agreed_to_guidelines', False),
            role='carrier',
            is_approved=False
        )
        return user
