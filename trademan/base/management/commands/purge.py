from django.core.management.base import BaseCommand
from base.models import Figi


class Command(BaseCommand):
    help = 'Обнуление базы'

    def handle(self, *args, **options):
        Figi.objects.all().delete()
