from rest_framework import serializers
from .models import Donation

class DonationSerializer(serializers.ModelSerializer):
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = Donation
        fields = '__all__'
        read_only_fields = ('stripe_session_id', 'stripe_payment_intent_id', 'created_at', 'updated_at')

    # What Stripe recorded can't be changed by hand.
    STRIPE_LOCKED = ('amount', 'covered_fee', 'donation_type', 'status', 'date')

    def validate(self, data):
        if data.get('website'):
            raise serializers.ValidationError("Anti-spam: Bot detected.")
        # Remove website so it doesn't get passed to the model
        data.pop('website', None)
        if self.instance is not None and self.instance.stripe_session_id:
            changed = [
                field for field in self.STRIPE_LOCKED
                if field in data and data[field] != getattr(self.instance, field)
            ]
            if changed:
                raise serializers.ValidationError(
                    "This gift came through Stripe, so its amount, type, status and date can't be changed."
                )
        return data
