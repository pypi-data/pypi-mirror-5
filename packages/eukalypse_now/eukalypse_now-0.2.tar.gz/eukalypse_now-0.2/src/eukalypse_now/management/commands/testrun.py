from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    def handle(self, arg_project = None, *args, **options):
        from eukalypse_now.tasks import Testrunner 
        Testrunner.delay(arg_project)
