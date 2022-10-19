from django.utils import timezone


class TimezoneMiddleware(object):
    def process_request(self, request):
        if tzname := request.session.get('django_timezone'):
            timezone.activate(tzname)
        else:
            timezone.deactivate()
