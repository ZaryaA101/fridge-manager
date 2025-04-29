from django.core.management.base import BaseCommand
from inventory.models import ItemsDetails
import uuid

class Command(BaseCommand):
    help = 'Fills the database with 10 common food items'

    def handle(self, *args, **kwargs):
        items = [
            {
                "item_id": uuid.uuid4(),
                "item_name": "Apple",
                "item_type": "Produce",
                "item_image": "apple.webp",
                "dimension_length": 8.0,
                "dimension_width": 8.0,
                "dimension_height": 8.0,
            },
            {
                "item_id": uuid.uuid4(),
                "item_name": "Milk Carton",
                "item_type": "Left Shelves",
                "item_image": "MilkGallon.png",
                "dimension_length": 10.0,
                "dimension_width": 10.0,
                "dimension_height": 25.0,
            },
            
        ]
        for item in items:
            ItemsDetails.objects.update_or_create(
                item_name=item["item_name"],
                defaults=item
            )
        self.stdout.write(self.style.SUCCESS('Successfully populated the database with common food items.'))
