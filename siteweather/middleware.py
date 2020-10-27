import pytz

from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.session.get('django_timezone')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        # else:
        #     timezone.deactivate()
        # If 14, 15 lines are commented, timezone will not deactivate when user logs out or logs in.
        return self.get_response(request)
