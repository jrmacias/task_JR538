"""
This file contains the views for the taskApi app.
"""
import logging
import os
import re

from django.contrib.auth.models import Group, User
from django.http import Http404, JsonResponse
from django_filters import rest_framework as filters
from rest_framework import mixins, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from taskApi.models import DatasetRepository
from taskApi.serializers import (DatasetRepositorySerializer, GroupSerializer,
                                 UserSerializer)
from taskPrj import settings

from .utils import get_dataset_data, parse_dataset_data

logger = logging.getLogger(__name__)


@permission_classes([IsAuthenticated])
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


@permission_classes([IsAuthenticated])
class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]


class DatasetRepositoryInfoView(viewsets.GenericViewSet,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin
                                ):
    """
    API endpoint for dataset repositories
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = DatasetRepository.objects.all()
    serializer_class = DatasetRepositorySerializer
    filter_backends = (filters.DjangoFilterBackend,
                       SearchFilter, OrderingFilter)
    search_fields = ['name', 'accession_template']
    ordering_fields = ['name', 'accession_template']
    ordering = ['name']


@api_view(['GET'])
def view_DatasetDetails(request, accession=None):

    # check accession code
    if re.match(r"^(MTBLS\w+)", accession):
        prefix = settings.MTBLS_ACC_PREFIX
    elif re.match(r"^(ST\w+)", accession):
        prefix = settings.MTWB_ACC_PREFIX
    elif re.match(r"^(MTBK\w+)", accession):
        prefix = settings.MTBK_ACC_PREFIX
    else:
        raise Http404(f"Invalid accession code: {str(accession)}")

    local_path = os.path.join(settings.DATASETS_DIR, prefix, accession)
    try:
        # check if already downloaded
        if not os.path.exists(local_path):
            logger.debug(f"Get Dataset for the first time: {accession}")
            get_dataset_data(prefix, accession)
        # parse local cache data
        logger.debug(f"Parse Dataset {accession}")
        dataset = parse_dataset_data(prefix, accession)
    except Exception as ex:
        raise Http404(f"Dataset not found: {accession}")

    return JsonResponse(dataset)
