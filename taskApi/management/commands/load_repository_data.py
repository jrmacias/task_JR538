"""
Command to setup some base tables that need/may contain fixed data.
"""

from django.core.management.base import BaseCommand
from taskApi.utils import load_repository_data


class Command(BaseCommand):
    """
    Command to update the dataset repositories data from local CSV file.
    """

    help = "Update dataset repositories data from local CSV file."
    missing_args_message = "Too few arguments. Please, provide a filename."
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path', nargs=1, type=str,
            help="<Required> CSV file path, i.e.: ./data/dataset_repositories.csv")

    def handle(self, *args, **options):
        file_path = options['file_path'][0]
        print(f"Reading data from {file_path}")
        load_repository_data(file_path)
        print("Done.")
