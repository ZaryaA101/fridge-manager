from celery import shared_task
from django.utils import timezone
from .models import FridgeContent
from django.core.mail import send_mail
from django.contrib import messages

@shared_task
def check_item_expiration():
    today = timezone.now().date()
    items_near_expiration = FridgeContent.objects.filter(expiration_date__lte=today + datetime.timedelta(days=4))
    for item in items_near_expiration:
        if item.will_expire_soon():
            send_expiration_notification(item)
def send_expiration_notification(item):
    user = item.family_id.userprofile.user_id  
    send_mail(
        "Item Expiration Warning",
        f"The item '{item.item_id.item_name}' is expiring soon! Please check your fridge.",
        'from@example.com',
        [user.email],
        fail_silently=False,
    )
