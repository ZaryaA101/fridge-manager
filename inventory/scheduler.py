from apscheduler.schedulers.background import BackgroundScheduler
from inventory.Tasks import check_item_expiration  

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_item_expiration, 'interval', hours=24)
    scheduler.start()

