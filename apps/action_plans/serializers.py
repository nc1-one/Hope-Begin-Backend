import re
from urllib.parse import urlparse

from rest_framework import serializers

from common.utils import check_spam_keywords, validate_form_time

# Links in a plan can only be a path on the HopeBegins site ("/hope-ai"),
# HopeBegins, its prayer app, the Himala Everyday e-coach page, or a phone
# number. This stops the endpoint
# from being used to email arbitrary links from our domain.
ALLOWED_LINK_HOSTS = {
    'hopebegins.today',
    'www.hopebegins.today',
    'warroom.hopebegins.today',
}
ALLOWED_LINK_PREFIXES = ('https://m.me/Mayhimalaeveryday',)


SITE_PATH = re.compile(r'^/[a-z0-9\-/]*$')


def is_allowed_link(link):
    if SITE_PATH.match(link):
        return True
    if link.startswith('tel:'):
        return link[4:].replace('+', '').isdigit()
    if link.startswith(ALLOWED_LINK_PREFIXES):
        return True
    parsed = urlparse(link)
    return parsed.scheme == 'https' and parsed.hostname in ALLOWED_LINK_HOSTS


class PlanItemSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    detail = serializers.CharField(max_length=1000, allow_blank=True)
    steps = serializers.ListField(
        child=serializers.CharField(max_length=400),
        required=False,
        max_length=6,
    )
    link = serializers.CharField(max_length=300, required=False, allow_blank=True)
    link_label = serializers.CharField(max_length=80, required=False, allow_blank=True)

    def validate_link(self, value):
        if value and not is_allowed_link(value):
            raise serializers.ValidationError('Link is not allowed.')
        return value


class PlanSectionSerializer(serializers.Serializer):
    heading = serializers.CharField(max_length=120)
    intro = serializers.CharField(max_length=300, required=False, allow_blank=True)
    items = PlanItemSerializer(many=True, max_length=10)


class EmailActionPlanSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=60, required=False, allow_blank=True)
    summary = serializers.ListField(
        child=serializers.CharField(max_length=200), max_length=6
    )
    sections = PlanSectionSerializer(many=True, max_length=10)
    website = serializers.CharField(required=False, allow_blank=True)
    startTime = serializers.IntegerField(required=False)

    def validate(self, data):
        if data.get('website'):
            raise serializers.ValidationError('Anti-spam: Bot detected.')
        if not validate_form_time(data.get('startTime')):
            raise serializers.ValidationError('Anti-spam: Form submitted too quickly.')

        # Names are left out: the keyword check matches inside words
        # ("Seo-yeon" contains "seo").
        text = ' '.join(
            data['summary']
            + [
                ' '.join([item['title'], item['detail'], item.get('link_label', ''), *item.get('steps', [])])
                for section in data['sections']
                for item in section['items']
            ]
        )
        if check_spam_keywords(text):
            raise serializers.ValidationError('Your plan contains restricted keywords.')

        data.pop('website', None)
        data.pop('startTime', None)
        return data
