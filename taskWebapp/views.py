"""
This file contains the views for the taskWebapp app.
"""
import mimetypes
import os
import re

import requests
from django.http import (FileResponse, Http404, HttpResponse,
                         HttpResponseRedirect)
from django.shortcuts import render
from django.template import loader
from django.urls import reverse

from taskPrj import settings

from .forms import DsSearchForm


def home(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render())


# def seach_dataset(request, accession):
#     accession = request.GET.get("accession")
#     if accession is None:
#         return HttpResponseRedirect(reverse("home"))
#     return HttpResponseRedirect(reverse("results", args=(accession,)))


def ds_details_view(request, accession):
    data = {}
    # call the API endpoint to get dataset details
    url = request.build_absolute_uri(
        reverse('api:dataset_details', args=(accession, )))
    with requests.get(url, stream=True) as req:
        if req.status_code == 200:
            json_data = req.json()
            data = json_data
        else:
            raise Http404()

    return render(request, "results.html", data)


def get_dataset(request):
    if request.method == "POST":
        form = DsSearchForm(request.POST)
        if form.is_valid():
            ds_accession = request.POST.get('ds_accession', '')
            return HttpResponseRedirect(f'/details/' + ds_accession)
    else:
        form = DsSearchForm()

    return render(request, "search.html", {"form": form})


def download_file(request, accession, filetype="metadata"):
    """
    Download the metadata files
    """
    # check accession code
    if re.match(r"^(MTBLS\w+)", accession):
        prefix = settings.MTBLS_ACC_PREFIX
        if filetype == "metadata":
            filename = "i_Investigation.txt"
        elif filetype == "metabolites":
            filename = f"m_{accession}_*_maf.tsv"
        elif filetype == "rawdata":
            filename = "i_Investigation.txt"

    elif re.match(r"^(ST\w+)", accession):
        prefix = settings.MTWB_ACC_PREFIX
        filename = f"{accession}.mwtab.txt"
    elif re.match(r"^(MTBK\w+)", accession):
        prefix = settings.MTBK_ACC_PREFIX
        filename = f"{accession}.idf.txt"

    filepath = os.path.join(settings.DATASETS_DIR, prefix, accession, filename)

    try:
        path = open(filepath, "r")
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        response["Content-Disposition"] = f"attachment; filename={accession}_{filename}"
        return response
    except FileNotFoundError:
        raise Http404()
