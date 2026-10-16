from rest_framework.throttling import AnonRateThrottle

class StrictPublicFormThrottle(AnonRateThrottle):
    """
    Stricter throttle for public form submissions.
    """
    scope = 'public_form'


class ActionPlanEmailThrottle(AnonRateThrottle):
    """
    Tight limit for the endpoint that emails a visitor their action plan,
    since it sends mail to an address the visitor types in.
    """
    scope = 'action_plan_email'


class AnalyticsClickThrottle(AnonRateThrottle):
    """
    Caps anonymous event counting per visitor so the counts can't be flooded.
    Normal use, even ticking every day and every tool, stays far below it.
    """
    scope = 'analytics_click'
