from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User

import jsonfield

from .signals import event_logged


PUSHER_CONFIG = getattr(settings, "PUSHER_CONFIG", None)


class Log(models.Model):
    
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    action = models.CharField(max_length=50, db_index=True)
    extra = jsonfield.JSONField()
    
    class Meta:
        ordering = ["-timestamp"]


def log(user, action, extra=None):
    if (user is not None and not user.is_authenticated()):
        user = None
    if extra is None:
        extra = {}
    
    if PUSHER_CONFIG:
        try:
            import pusher
            p = pusher.Pusher(
                app_id=PUSHER_CONFIG["app_id"],
                key=PUSHER_CONFIG["key"],
                secret=PUSHER_CONFIG["secret"]
            )
            # send utc date (http://stackoverflow.com/questions/948532/how-do-you-convert-a-javascript-date-to-utc/951417#951417)
            p["event_log"].trigger(action, {
                "user": user.username if user else None,
                "extra": extra,
                "date": datetime.utcnow().isoformat()
            })
        except Exception, e:
            event_logged.send(
                sender=Log,
                event=Log.objects.create(user=user, action="PUSHER_FAILED", extra={"exception": str(e)})
            )
    
    event = Log.objects.create(user=user, action=action, extra=extra)
    event_logged.send(sender=Log, event=event)
    return event
