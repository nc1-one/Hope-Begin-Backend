from django.db import models


def default_journey_steps():
    return [
        {"key": "welcome", "label": "Welcome"},
        {"key": "word", "label": "A Word for You"},
        {"key": "prayer", "label": "Guided Prayer"},
        {"key": "devotional", "label": "Devotional"},
        {"key": "next-steps", "label": "Next Steps"},
    ]


def default_journey_welcome_section():
    return {
        "title": "Your Hopeful Beginning",
        "body": (
            "Feeling hopeless is hard. Thank you for coming here.\nThere are five short steps. Move to the next one whenever you're ready."
        ),
        "expectations_title": "What to expect:",
        "expectations": [
            "A short video message of encouragement",
            "A guided prayer",
            "A short reading on what the Bible says about hope",
            "Ways to get more support",
        ],
        "button_text": "Continue",
    }


def default_journey_word_section():
    return {
        "title": "A Word for You",
        "description": "Before anything else, we want you to hear this.",
        "video_embed_url": "https://www.youtube.com/embed/zHPaFDRZMUo?rel=0",
        "verse_text": "He heals the broken in heart, and binds up their wounds.",
        "verse_reference": "Psalm 147:3",
        "previous_button_text": "Previous",
        "next_button_text": "Continue",
    }


def default_journey_prayer_section():
    return {
        "title": "Guided Prayer",
        "description": "Read each step slowly. Pray the words, or just read them.",
        "steps": [
            {
                "title": "Be Still",
                "text": (
                    "Sit still for a moment. Let your shoulders drop and breathe slowly."
                ),
            },
            {
                "title": "Acknowledge",
                "text": (
                    "Name what you're feeling, like sadness, fear or tiredness, without judging yourself for it. Breathe in slowly."
                ),
            },
            {
                "title": "Release",
                "text": (
                    "Lord, I give You my fear, my pain and my worry. You said to cast my burdens on You, so here they are."
                ),
            },
            {
                "title": "Receive",
                "text": (
                    "I receive Your peace that passes understanding. I receive Your love "
                    "that never fails. I receive the hope that You are working all things "
                    "together for my good."
                ),
            },
            {
                "title": "Rest",
                "text": (
                    "I rest in You, Lord. Things are not okay right now, but You are with me. Amen."
                ),
            },
        ],
        "back_button_text": "Back",
        "next_button_text": "Next",
        "final_button_text": "Continue to Devotional",
    }


def default_journey_devotional_section():
    return {
        "title": "What is Hope?",
        "subtitle": "A short reading on hope.",
        "content_cards": [
            (
                "In the Bible, hope is trust that God will keep His promises, even when you can't yet see how."
            ),
            (
                "Hebrews calls hope an anchor for the soul. An anchor doesn't stop the storm. It keeps the boat from drifting until the storm passes."
            ),
        ],
        "verse_text": "This hope we have as an anchor of the soul, a hope both sure and steadfast and entering into that which is within the veil;",
        "verse_reference": "Hebrews 6:19",
        "good_news_title": "The Good News",
        "good_news_body": (
            "God loves you, and that love doesn't depend on what you've done. He sent His Son, Jesus, so you would never walk through darkness alone. You can come to Him as you are today."
        ),
        "reflection_title": "Reflect on this:",
        "reflection_prompt": (
            "What would change if you believed, even a little, that tomorrow could be different?"
        ),
        "previous_button_text": "Previous",
        "next_button_text": "Continue",
    }


def default_journey_next_steps_section():
    return {
        "title": "Your Next Step",
        "description": (
            "You've finished all five steps. Here are ways to keep going."
        ),
        "actions": [
            {"title": "I Need Someone to Pray for Me", "href": "/prayers", "icon": "heart"},
            {"title": "Start Daily Hope Drops", "href": "/daily-hope", "icon": "mail"},
            {"title": "Talk to Hope AI", "href": "/hope-ai", "icon": "message-square"},
            {"title": "Listen to a HopeCast", "href": "/hopecasts", "icon": "headphones"},
        ],
        "home_link_text": "Back to Home",
    }


def default_journey_crisis_section():
    return {
        "heading": "In crisis? Call one of these lines:",
        "contacts": [
            {
                "title": "National Center for Mental Health 24/7 Crisis Hotline",
                "icon": "heart",
                "lines": [
                    {"label": "Landline (nationwide):", "value": "1553"},
                    {"label": "Mobile:", "value": "0917-899-8727 / 0966-351-4518"},
                ],
            },
            {
                "title": "Hopeline Philippines Emotional Crisis Support",
                "icon": "message-square",
                "lines": [
                    {"label": "Call:", "value": "(02) 8804-4673"},
                    {"label": "Mobile:", "value": "0917-558-4673 / 0918-873-4673"},
                ],
            },
            {
                "title": "In Touch Community Services Crisis Line (24/7)",
                "icon": "heart",
                "lines": [
                    {"label": "Call:", "value": "(02) 8893-7603"},
                    {"label": "Mobile:", "value": "0917-800-1123"},
                ],
            },
        ],
    }


class PopoutSettings(models.Model):
    is_enabled = models.BooleanField(default=True)
    interval_seconds = models.IntegerField(default=15)

    class Meta:
        verbose_name = "Popout Settings"
        verbose_name_plural = "Popout Settings"

    def __str__(self):
        return "Popout Settings"

    def save(self, *args, **kwargs):
        if not self.pk and PopoutSettings.objects.exists():
            return
        return super().save(*args, **kwargs)

class PopoutItem(models.Model):
    message = models.CharField(max_length=255)
    button_text = models.CharField(max_length=50)
    link = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.message

class JourneyContent(models.Model):
    title = models.CharField(max_length=255, default="A Word for You")
    description = models.TextField(default="Before anything else, we want you to hear this.")
    video_embed_url = models.URLField(default="https://www.youtube.com/embed/zHPaFDRZMUo?rel=0")
    page_title = models.CharField(max_length=255, default="Hopeful Beginning")
    page_subtitle = models.TextField(default="Five short steps for when you feel hopeless.")
    steps = models.JSONField(default=default_journey_steps)
    welcome_section = models.JSONField(default=default_journey_welcome_section)
    word_section = models.JSONField(default=default_journey_word_section)
    prayer_section = models.JSONField(default=default_journey_prayer_section)
    devotional_section = models.JSONField(default=default_journey_devotional_section)
    next_steps_section = models.JSONField(default=default_journey_next_steps_section)
    crisis_section = models.JSONField(default=default_journey_crisis_section)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Journey Content"
        verbose_name_plural = "Journey Content"

    def __str__(self):
        return "Journey Content Settings"

    def save(self, *args, **kwargs):
        if not self.pk and JourneyContent.objects.exists():
            # Ensure only one instance exists
            return
        return super().save(*args, **kwargs)
