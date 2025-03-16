"""
Command used to get the datasets list from the dataset repository API
"""

from django.core.management.base import BaseCommand
from taskApi.utils import get_dataset_list


class Command(BaseCommand):
    help = 'Get dataset list from the dataset repository API'
    # missing_args_message = "Too few arguments. Please, provide a repository name."

    def add_arguments(self, parser):
        ca = parser.add_argument(
            '-s', '--dataset_repository',
            choices=['MetaboLights', 'Metabolomics-Workbench', 'MetaboBank'],
            nargs=1, type=str,
            help="<Required> Repository name, i.e.: MetaboLights | ")

    def handle(self, *args, **options):
        # Get the datasets list from the dataset API
        
        if options['dataset_repository'] is None:
            print("Please provide a valid repository name.")
            print("""- Valid options are:
                    MetaboLights
                    Metabolomics-Workbench
                    MetaboBank
                    """)
            return
        
        repository_name = options['dataset_repository'][0]
        print(f"Getting datasets list from {repository_name}")
        get_dataset_list(repository_name)
        print("Done.")
