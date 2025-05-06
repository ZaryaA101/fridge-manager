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
                "dimension_length": 3.0,
                "dimension_width": 3.0,
                "dimension_height": 3.0,
            },
            {
                "item_id": uuid.uuid4(),
                "item_name": "Milk Carton",
                "item_type": "Left Shelves",
                "item_image": "MilkGallon.png",
                "dimension_length": 6.0,
                "dimension_width": 6.0,
                "dimension_height": 10.0,
            },
            {
                "item_id": uuid.uuid4(),
                "item_name": "Water Bottle",
                "item_type": "Middle Shelves",
                "item_image": "WaterBottle.jpg",
                "dimension_length": 3.0,
                "dimension_width": 3.0,
                "dimension_height": 8.0,
            },
            {
                "item_id": uuid.uuid4(),
                "item_name": "Egg Carton",
                "item_type": "Produce",
                "item_image": "EggCarton.jpg",
                "dimension_length": 3.0,
                "dimension_width": 10.0,
                "dimension_height": 3.0,
            },
            {
                "item_id": uuid.uuid4(),
                "item_name": "Coca Cola",
                "item_type": "Right Shelves",
                "item_image": "CocaCola.png",
                "dimension_length": 3.0,
                "dimension_width": 3.0,
                "dimension_height": 5.0,
            },
            {
                "item_id": uuid.uuid4(),
                "item_name": "Tomato",
                "item_type": "Produce",
                "item_image": "tomato.jpg",
                "dimension_length": 2.0,
                "dimension_width": 2.0,
                "dimension_height": 2.0,
            },
            {
                "item_id": uuid.uuid4(),
                "item_name": "Yogurt",
                "item_type": "Middle Shelves",
                "item_image": "yogurt.jpg",
                "dimension_length": 4.0,
                "dimension_width": 4.0,
                "dimension_height": 4.0,
            },
            {
                "item_id": uuid.uuid4(),
                "item_name": "Bologna",
                "item_type": "Middle Shelves",
                "item_image": "BolognaPack.jpg",
                "dimension_length": 4.0,
                "dimension_width": 4.0,
                "dimension_height": 2.0,
            },
            {
                "item_id": uuid.uuid4(),
                "item_name": "Ice Cream",
                "item_type": "Freezer",
                "item_image": "icecream.png",
                "dimension_length": 6.0,
                "dimension_width": 4.0,
                "dimension_height": 4.0,
            },
            {
                "item_id": uuid.uuid4(),
                "item_name": "Ketchup Bottle",
                "item_type": "Right Shelves",
                "item_image": "ketchupbottle.jpg",
                "dimension_length": 4.0,
                "dimension_width": 2.0,
                "dimension_height": 8.0,
            },
            
        ]
        for item in items:
            ItemsDetails.objects.update_or_create(
                item_name=item["item_name"],
                defaults=item
            )
        self.stdout.write(self.style.SUCCESS('Successfully populated the database with common food items.'))
