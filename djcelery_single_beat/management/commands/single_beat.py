from optparse import make_option

from django.core.management.base import BaseCommand
from djcelery_single_beat.process import Process


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--app'),
        make_option('--pidfile'),
        make_option('--schedule'),
    )

    def handle(self, *args, **options):
        process = Process({
            'app': options.get('app'),
            'pidfile': options.get('pidfile'),
            'schedule': options.get('schedule'),
        })
        process.run()
