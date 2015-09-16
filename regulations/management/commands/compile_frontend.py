from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--long', '-l', dest='long',
            help='Help for the long options'),
    )
    help = 'Help text goes here'

    def handle(self, **options):
         print "This is a command"
