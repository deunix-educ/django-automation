#
# encoding: utf-8
from django.core.management import BaseCommand
from contrib import utils

class Command(BaseCommand):
    help = "Return a number in hexa format"

    def add_arguments(self, parser):
        parser.add_argument('-l', '--length', type=int, help='Length of the decimal number', default=19)

    def handle(self, *args, **options):
        n = options.get('length', 19)
        uuid = utils.gen_device_uuid(n)
        print(f'Hexa size {len(uuid)+2}: ', f'0x{uuid}')