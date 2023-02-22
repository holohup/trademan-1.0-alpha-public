from base.models import Figi
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Обнуление базы'

    def handle(self, *args, **options):
        Figi.objects.all().delete()
