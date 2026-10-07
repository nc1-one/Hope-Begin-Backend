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
