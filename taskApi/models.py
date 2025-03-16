""" 
This module contains the models for the taskApi app. 
"""

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

# https://ftp.ebi.ac.uk/pub/databases/metabolights/studies/public/
# https://ftp.ebi.ac.uk/pub/databases/metabolights/studies/public/MTBLS93/

# https://www.metabolomicsworkbench.org/rest/study/study_id/ST/available

# https://ddbj.nig.ac.jp/public/metabobank/study/
# https://ddbj.nig.ac.jp/public/metabobank/study/MTBKS93/


def dataset_files_folder(instance, filename):
    accession_prefix = str(instance.dataset.repository.accession_prefix())
    accession = str(instance.dataset.pk)
    return '/'.join(['datasets', accession_prefix, accession, filename])


class DatasetRepository(models.Model):
    """
    DatasetRepository
    Store dataset repository information
    """
    name = models.CharField(max_length=100, blank=True, null=True)
    accession_template = models.CharField(max_length=10, blank=True, null=True)
    repository_website = models.CharField(
        max_length=250, blank=True, null=True)

    def accession_prefix(self):
        return f'{self.accession_template.replace("x", "")}'

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Dataset-Repository"
        verbose_name_plural = "Dataset-Repositories"


class DatasetRepositoryFile(models.Model):
    """
    DatasetRepositoryFile
    Store files available from a particular dataset repository
    """
    repository = models.ForeignKey(DatasetRepository, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.repository} - {self.filename}'


class Dataset(models.Model):
    """
    Dataset
    Store dataset information
    """
    repository = models.ForeignKey(DatasetRepository, on_delete=models.CASCADE)
    accession = models.CharField(max_length=50, blank=False,
                                 default='', primary_key=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.title}'


class DatasetFile(models.Model):
    """
    DatasetFile
    Store files for a particular dataset
    """
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to=dataset_files_folder, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def dataset_accession(self):
        return f'{self.dataset.accession}'

    def __str__(self):
        return f'{self.dataset} - {self.file}'


class Metabolite(models.Model):
    """
    Metabolite
    Store metabolite names
    """
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.name}'


class DatasetMetabolite(models.Model):
    """
    DatasetMetabolite
    Relacional table between Dataset and Metabolite
    """
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    metabolite = models.ForeignKey(Metabolite, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.dataset} - {self.metabolite}'
