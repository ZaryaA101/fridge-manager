
from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import now
from django.contrib.auth import get_user_model
import atexit
import logging

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

def check_fridge_capacity():
    from .models import FridgeDetail, FridgeContent
    threshold = settings.FRIDGE_WARNING_THRESHOLD
    fridges = FridgeDetail.objects.all()

    for fridge in fridges:
        total_space = fridge.capacity
        used_space = sum(item.space for item in FridgeContent.objects.filter(fridge=fridge))
        usage_ratio = used_space / total_space if total_space > 0 else 0

        if usage_ratio >= threshold:
            for user in fridge.family.members.all():
                send_mail(
                    subject=' Fridge Almost Full',
                    message=f"Hi {user.username},\n\nYour fridge '{fridge.name}' is {int(usage_ratio * 100)}% full.",
                    from_email='admin@fridgeapp.com',
                    recipient_list=[user.email],
                )
            logger.info(f"Warning sent for fridge {fridge.name} ({usage_ratio:.2f})")

class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'

    def ready(self):
        scheduler.add_job(
            check_fridge_capacity,
            trigger=IntervalTrigger(hours=1),
            name="Check fridge space usage",
            replace_existing=True,
        )
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())

