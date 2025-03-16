"""
Command used to get the dataset data from the repository API
"""
from django.core.management.base import BaseCommand
from taskApi.utils import get_dataset_data


class Command(BaseCommand):
    help = 'Get dataset data from the repository API'

    def add_arguments(self, parser):
        ca = parser.add_argument(
            '-a', '--accession',
            nargs=1, type=str,
            help="<Required> Dataset accession number, i.e.: MTBLSxxx, STxxx, MTBKxxx")

    def handle(self, *args, **options):
        # Get the datasets list from the dataset API

        if options['accession'] is None:
            print("Please provide a valid dataset accession number.")
            return

        accession = options['accession'][0]
        print(f"Getting Dataset data from {accession}")
        get_dataset_data(accession)
        print("Done.")
