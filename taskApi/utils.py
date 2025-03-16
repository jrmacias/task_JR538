"""
This file contains utility functions for the taskApi app
"""
import ftplib
import json
import logging
import os
import re
from html.parser import HTMLParser

import pandas as pd
import requests

from taskPrj import settings

logger = logging.getLogger(__name__)


def save_json_data(data, path, filename, createIfNotExist=True):
    """
    Save JSON data as *.json file
    """
    logger.debug(f"Save JSON data to {path}/{filename}")
    try:
        if path and createIfNotExist:
            os.makedirs(path, exist_ok=True)
        full_path = os.path.join(path, filename)
        with open(full_path, 'w') as f:
            json.dump(data, f)
        return f.name
    except Exception as exc:
        logger.exception(exc)
        raise (exc)


def get_json_data(url):
    """
    Request JSON data from a URL
    """
    logger.debug(f"Get JSON data from {url}")
    try:
        with requests.get(url, stream=True) as req:
            if req.status_code == 200:
                logger.debug(f"Got request status: {req.status_code}")
                return req.json()
    except Exception as exc:
        logger.exception(exc)
        raise (exc)


def get_text_data(url):
    """
    Request text data from a URL
    """
    logger.debug(f"Get text data from {url}")
    try:
        with requests.get(url, stream=True) as req:
            if req.status_code == 200:
                logger.debug(f"Got request status: {req.status_code}")
                return req.text
    except Exception as exc:
        logger.exception(exc)
        raise (exc)


def save_text_data(data, path, filename, createIfNotExist=True):
    """
    Save text data as *.txt file
    """
    logger.debug(f"Save text data to {path}/{filename}")
    try:
        if path and createIfNotExist:
            os.makedirs(path, exist_ok=True)
        full_path = os.path.join(path, filename)
        with open(full_path, 'w') as f:
            for line in data:
                f.write(f"{line}")
        return f.name
    except Exception as exc:
        logger.exception(exc)
        raise (exc)


class HTMLFilter(HTMLParser):
    """"
    Auxiliary class to parse html into plain text
    """
    text = ""

    def handle_data(self, data):
        self.text += data


def get_dataset_data(prefix, accession):
    """
    Guess the repository from the accession code
    and process calling the corresponding function
    """
    if prefix == settings.MTBLS_ACC_PREFIX:
        # reposiroty is MetaboLights
        get_dataset_files_mtbls(prefix, accession)
    elif prefix == settings.MTWB_ACC_PREFIX:
        # reposiroty is Metabolomics-Workbench
        return get_dataset_files_mtwb(prefix, accession)
    elif prefix == settings.MTBK_ACC_PREFIX:
        # reposiroty is Metabobank
        return get_dataset_files_mtbk(prefix, accession)
    else:
        logger.debug(f"Dataset repository not found: {accession}")


def get_dataset_files_mtbls(prefix, accession):
    """
    Get a list of datasets from MetaboLights
    https://ftp.ebi.ac.uk/pub/databases/metabolights/studies/public/
    """
    mtbls_ftp_dataset_path = os.path.join(
        settings.MTBLS_FTP_BASE_DIR, accession)
    local_base_dir = os.path.join(settings.DATASETS_DIR, prefix, accession)

    logger.debug(
        f"Getting dataset from: {settings.MTBLS_FTP_URL}{settings.MTBLS_FTP_BASE_DIR}")
    try:
        ftp = ftplib.FTP(settings.MTBLS_FTP_URL,
                         settings.MTBLS_FTP_USER, settings.MTBLS_FTP_USER_PASS)
        logger.debug(f"Connected: {settings.MTBLS_FTP_URL}")
        ftp.cwd(mtbls_ftp_dataset_path)
        logger.debug(f"Current directory: {mtbls_ftp_dataset_path}")
        metadata_files = ftp.nlst()
        for filename in metadata_files:
            # get metadata files
            match_files = re.match(r"([siam]).+\.((txt)|(tsv))", filename)
            if match_files:
                local_file_path = os.path.join(local_base_dir, filename)
                url = os.path.join(settings.MTBLS_REMOTE_URL,
                                   accession, filename)
                with requests.get(url, stream=True) as req:
                    if req.status_code == 404:
                        logger.exception(f"Could not download file {url}")
                        return None
                    else:
                        # create local dir if needed
                        local_path = os.makedirs(os.path.dirname(
                            local_file_path), exist_ok=True)
                        with open(local_file_path, "w") as fd:
                            fd.write(req.text)
            # get result files, within FILES dir
            if filename == "FILES":
                logger.debug(
                    f"Getting result files (within FILES dir) {settings.MTBLS_FTP_URL} : {settings.MTBLS_FTP_BASE_DIR}")
                ftp.cwd(filename)
                result_files = ftp.nlst()
                local_file_path = os.path.join(
                    local_base_dir, settings.MTBLS_FNAME_RESULT_FILES)
                # create local dir if needed
                local_path = os.makedirs(os.path.dirname(
                    local_file_path), exist_ok=True)
                with open(local_file_path, 'w') as f:
                    for file in result_files:
                        f.write(f"{file}\n")
        ftp.quit()
    except ftplib.all_errors as exc:
        logger.exception(exc)
        raise (exc)


def get_dataset_files_mtwb(prefix, accession):
    """
    Get a list of datasets from Metabolomics-Workbench
    base url :                  https://www.metabolomicsworkbench.org
    {accession}.mwtab.json:     https://www.metabolomicsworkbench.org/data/study_textformat_view.php?JSON=YES&STUDY_ID={study_id}&ANALYSIS_ID={analysis_id}&MODE=d
    {accession}.mwtab.txt:      https://www.metabolomicsworkbench.org/data/study_textformat_view.php?STUDY_ID={study_id}&ANALYSIS_ID={analysis_id}&MODE=d
    """
    local_base_dir = os.path.join(settings.DATASETS_DIR, prefix, accession)
    logger.debug(f"Getting dataset from: {settings.MTWB_REST_BASE_URL}")
    try:
        # get ANALYSIS_ID
        url = f"https://www.metabolomicsworkbench.org/rest/study/study_id/{accession}/analysis"
        logger.debug(f"Get ANALYSIS_ID from: {url}")
        json_data = get_json_data(url)
        if json_data:
            study_id = json_data["study_id"]
            logger.debug(f"Got study_id: {study_id}")
            analysis_id = json_data["analysis_id"]
            logger.debug(f"Got analysis_id: {analysis_id}")
        # get STxxx.json file
        url = f"https://www.metabolomicsworkbench.org/data/study_textformat_view.php?JSON=YES&STUDY_ID={study_id}&ANALYSIS_ID={analysis_id}&MODE=d"
        logger.debug(f"Get STxxx.json file from : {url}")
        json_data = get_json_data(url)
        logger.debug(f"Got json_data: {json_data}")
        if json_data:
            local_filename = study_id + settings.MTWB_FNAME_JSON_SUFIX
            logger.debug(
                f"Save STxxx.json file to : {local_base_dir}/{local_filename}")
            save_json_data(json_data, local_base_dir, local_filename)
        # get STxxx.mwtab.txt file
        url = f"https://www.metabolomicsworkbench.org/data/study_textformat_view.php?STUDY_ID={study_id}&ANALYSIS_ID={analysis_id}&MODE=d"
        logger.debug(f"Get STxxx.mwtab.txt file from : {url}")
        text_data = get_text_data(url)
        logger.debug(f"Got text_data: {text_data}")
        if text_data:
            local_filename = study_id + settings.MTWB_FNAME_MWTAB_SUFIX
            logger.debug(
                f"Save STxxx.mwtab.txt file to : {local_base_dir}/{local_filename}")
            save_text_data(text_data, local_base_dir, local_filename)
    except Exception as exc:
        logger.exception(exc)
        raise (exc)


def get_dataset_files_mtbk(prefix, accession):
    """
    Get a list of datasets from Metabobank
    base url :                  https://ddbj.nig.ac.jp/public/metabobank
    {accession}.idf.txt:        https://ddbj.nig.ac.jp/public/metabobank/study/{accession}/{accession}.idf.txt
    {accession}.srdf.txt:       https://ddbj.nig.ac.jp/public/metabobank/study/{accession}/{accession}.sdrf.txt
    {accession}.filelist.txt:   https://ddbj.nig.ac.jp/public/metabobank/study/{accession}/{accession}.filelist.txt
    {accession}.maf.yyy.txt:    https://ddbj.nig.ac.jp/public/metabobank/study/{accession}/{accession}.maf.{*}.txt
    """
    local_base_dir = os.path.join(settings.DATASETS_DIR, prefix, accession)
    logger.debug(f"Getting dataset from: {settings.MTWB_REST_BASE_URL}")
    try:
        # get xxx.idf.txt file
        url = f"https://ddbj.nig.ac.jp/public/metabobank/study/{accession}/{accession}.idf.txt"
        logger.debug(f"Get xxx.idf.txt file from : {url}")
        text_data = get_text_data(url)
        logger.debug(f"Got text_data: {text_data}")
        if text_data:
            local_filename = accession + settings.MTBK_IDF_FILE_PREFIX + settings.MTBK_FILES_SUFIX
            logger.debug(
                f"Save xxx.idf.txt file to : {local_base_dir}/{local_filename}")
            save_text_data(text_data, local_base_dir, local_filename)

        # get xxx.srdf.txt file
        url = f"https://ddbj.nig.ac.jp/public/metabobank/study/{accession}/{accession}.sdrf.txt"
        logger.debug(f"Get xxx.srdf.txt file from : {url}")
        text_data = get_text_data(url)
        logger.debug(f"Got text_data: {text_data}")
        if text_data:
            local_filename = accession + settings.MTBK_SDRF_FILE_PREFIX + settings.MTBK_FILES_SUFIX
            logger.debug(
                f"Save xxx.srdf.txt file to : {local_base_dir}/{local_filename}")
            save_text_data(text_data, local_base_dir, local_filename)

        # get xxx.filelist.txt file
        url = f"https://ddbj.nig.ac.jp/public/metabobank/study/{accession}/{accession}.filelist.txt"
        logger.debug(f"Get xxx.filelist.txt file from : {url}")
        text_data = get_text_data(url)
        logger.debug(f"Got text_data: {text_data}")
        if text_data:
            local_filename = accession + \
                settings.MTBK_FILELIST_FILE_PREFIX + settings.MTBK_FILES_SUFIX
            logger.debug(
                f"Save xxx.filelist.txt file to : {local_base_dir}/{local_filename}")
            save_text_data(text_data, local_base_dir, local_filename)

        # get xxx.maf.yyy.txt files
        url = f"https://ddbj.nig.ac.jp/public/metabobank/study/{accession}/"
        logger.debug(f"Get xxx.maf.yyy.txt files from : {url}")
        html_data = get_text_data(url)
        logger.debug(f"Got html/text_data: {html_data}")
        if text_data:
            # use class HTMLParser o parse html to plain text
            hf = HTMLFilter()
            hf.feed(html_data)
            text_data = hf.text
            text_data = text_data.split()
            # get all xxx.maf.yyy.txt files
            filenames = []
            for item in text_data:
                if ".maf." in item:
                    filenames.append(item.rsplit(".txt", 1)[
                                     0]+settings.MTBK_FILES_SUFIX)
            for filename in filenames:
                # https://ddbj.nig.ac.jp/public/metabobank/study/{accession}/{filename}
                url = f"https://ddbj.nig.ac.jp/public/metabobank/study/{accession}/{filename}"
                logger.debug(f"Get xxx.maf.yyy.txt file from : {url}")
                text_data = get_text_data(url)
                logger.debug(f"Got text_data: {text_data}")
                if text_data:
                    logger.debug(
                        f"Save xxx.maf.yyy.txt file to : {local_base_dir}/{filename}")
                    save_text_data(text_data, local_base_dir, filename)

    except Exception as exc:
        logger.exception(exc)
        raise (exc)


def parse_dataset_data(prefix, accession):
    if prefix == settings.MTBLS_ACC_PREFIX:
        # reposiroty is MetaboLights
        return parse_dataset_data_mtbls(prefix, accession)
    elif prefix == settings.MTWB_ACC_PREFIX:
        # reposiroty is Metabolomics-Workbench
        return parse_dataset_data_mtwb(prefix, accession)
    elif prefix == settings.MTBK_ACC_PREFIX:
        # eposiroty is Metabobank
        return parse_dataset_data_mtbk(prefix, accession)
    else:
        logger.debug(f"Dataset repository not found: {accession}")


def parse_dataset_data_mtbls(prefix, accession):
    dataset = {}
    dataset["accession"] = accession
    local_base_dir = os.path.join(settings.DATASETS_DIR, prefix, accession)
    # get metadata parsing the investigation file
    logger.debug(
        f"Get metadata parsing the analysis file {accession} : {settings.MTBLS_FNAME_INVESTIGATION}")
    dataset = get_metadata_mtbls(
        os.path.join(local_base_dir, settings.MTBLS_FNAME_INVESTIGATION), dataset)
    # get raw data file names
    logger.debug(
        f"Get raw data file names from dir FILE {accession} : {settings.MTBLS_FNAME_RESULT_FILES}")
    dataset = get_rawdata_filenames_mtbls(
        os.path.join(local_base_dir, settings.MTBLS_FNAME_RESULT_FILES), dataset)
    # get metabolites names
    logger.debug(f"Get metabolites names from m_*.tsv file {accession}")
    dataset = get_metabolites_names_mtbls(local_base_dir, dataset)
    return dataset


def get_metadata_mtbls(filename, dataset):
    try:
        with open(filename) as f:
            data = f.readlines()
            for line in data:
                # Study Title
                if "Study Title" in line:
                    title = line
                    dataset["Title"] = line.replace("Study Title", "").strip()
                # Study Description
                if "Study Description" in line:
                    title = line
                    dataset["Description"] = line.replace(
                        "Study Description", "").strip()
    except Exception as exc:
        logger.exception(exc)
        raise (exc)
    return dataset


def get_rawdata_filenames_mtbls(filename, dataset):
    rawdata_filenames = []
    with open(filename) as f:
        data = f.readlines()
        for line in data:
            rawdata_filenames.append(line.strip())
    dataset["Rawdata"] = rawdata_filenames
    return dataset


def get_metabolites_names_mtbls(local_base_dir, dataset):
    metabolites_names = []
    metabolites_filename = None
    try:
        for root, dirs, files in os.walk(local_base_dir):
            for file in files:
                if re.match("(m_).+\.(tsv)", file):
                    metabolites_filename = os.path.join(local_base_dir, file)
        if metabolites_filename:
            df = pd.read_csv(metabolites_filename, sep='\t')
            column = df["metabolite_identification"]
            for cell in column:
                if pd.isna(cell):
                    continue
                metabolites_names.append(cell)
    except Exception as exc:
        logger.exception(exc)
        raise (exc)

    dataset["Metabolites"] = metabolites_names
    return dataset


def parse_dataset_data_mtwb(prefix, accession):
    dataset = {}
    dataset["accession"] = accession
    local_base_dir = os.path.join(settings.DATASETS_DIR, prefix, accession)

    # Get metadata parsing STxxx.json file
    local_json_filename = accession + settings.MTWB_FNAME_JSON_SUFIX
    logger.debug(
        f"Get metadata parsing STxxx.json file: {local_json_filename}")
    dataset = get_metadata_mtwb(os.path.join(
        local_base_dir, local_json_filename), dataset)
    # get metabolites names parsing STxxx.json file
    logger.debug(
        f"Get metabolites names parsing STxxx.json file {local_json_filename}")
    dataset = get_metabolites_names_mtwb(os.path.join(
        local_base_dir, local_json_filename), dataset)

    return dataset


def get_metadata_mtwb(filename, dataset):
    try:
        with open(filename, 'r') as json_file:
            json_data = json.load(json_file)
        # get ANALYSIS_ID
        analysis_id = json_data["METABOLOMICS WORKBENCH"]["ANALYSIS_ID"]
        if analysis_id:
            dataset["analysis_id"] = analysis_id
        # get STUDY_TITLE
        study_title = json_data["STUDY"]["STUDY_TITLE"]
        if study_title:
            dataset["Title"] = study_title
        # get STUDY_SUMMARY
        study_description = json_data["STUDY"]["STUDY_SUMMARY"]
        if study_description:
            dataset["Description"] = study_description
    except Exception as exc:
        logger.exception(exc)
        raise (exc)
    return dataset


def get_metabolites_names_mtwb(filename, dataset):
    metabolites_names = []
    try:
        with open(filename, 'r') as json_file:
            json_data = json.load(json_file)
        # get metabolite names
        ms_metabolite_data_list = json_data["MS_METABOLITE_DATA"]["Data"]
        for metabolite_data in ms_metabolite_data_list:
            metabolite_name = metabolite_data["Metabolite"]
            if metabolite_name:
                metabolites_names.append(metabolite_name)
    except Exception as exc:
        logger.exception(exc)
        raise (exc)
    dataset["Metabolites"] = metabolites_names
    return dataset


def parse_dataset_data_mtbk(prefix, accession):
    dataset = {}
    dataset["accession"] = accession
    local_base_dir = os.path.join(settings.DATASETS_DIR, prefix, accession)
    # Get metadata parsing xxx.idf.txt file
    local_idf_filename = accession + \
        settings.MTBK_IDF_FILE_PREFIX + settings.MTBK_FILES_SUFIX
    logger.debug(
        f"Get metadata parsing xxx.idf.txt file: {local_idf_filename}")
    dataset = get_metadata_mtbk(os.path.join(
        local_base_dir, local_idf_filename), dataset)
    # get metabolites names parsing xxx.maf.txt file
    logger.debug(
        f"Get metabolites names parsing xxx.maf.yyy.txt {accession}")
    dataset = get_metabolites_names_mtbk(local_base_dir, dataset)

    # get raw data file names parsing xxx.filelist.txt file
    local_rawdata_filename = accession + \
        settings.MTBK_FILELIST_FILE_PREFIX + settings.MTBK_FILES_SUFIX
    logger.debug(
        f"Get raw data file names from xxx.filelist.txt {accession}")
    dataset = get_rawdata_filenames_mtbk(os.path.join(
        local_base_dir, local_rawdata_filename), dataset)
    return dataset


def get_metadata_mtbk(filename, dataset):
    try:
        with open(filename) as f:
            data = f.readlines()
            for line in data:
                # get Study Title
                if "Study Title" in line:
                    title = line
                    dataset["Title"] = line.replace("Study Title", "").strip()
                # get Study Description
                if "Study Description" in line:
                    title = line
                    dataset["Description"] = line.replace(
                        "Study Description", "").strip()
    except Exception as exc:
        logger.exception(exc)
        raise (exc)
    return dataset


def get_metabolites_names_mtbk(local_base_dir, dataset):
    metabolites_names = []
    metabolites_filename = None
    try:
        for root, dirs, files in os.walk(local_base_dir):
            for file in files:
                if "maf" in file:
                    metabolites_filename = os.path.join(local_base_dir, file)
        if metabolites_filename:
            df = pd.read_csv(metabolites_filename, sep='\t')
            column = df["metabolite_identification"]
            for cell in column:
                if pd.isna(cell):
                    continue
                metabolites_names.append(cell)
    except Exception as exc:
        logger.exception(exc)
        raise (exc)
    dataset["Metabolites"] = metabolites_names
    return dataset


def get_rawdata_filenames_mtbk(filename, dataset):
    rawdata_filenames = []
    try:
        df = pd.read_csv(filename, sep='\t')
        type_column = df["Type"]
        filtered_rows = df.loc[type_column == "raw"]
        name_column = filtered_rows["Name"]
        for cell in name_column:
            if pd.isna(cell):
                continue
            rawdata_filenames.append(cell)
    except Exception as exc:
        logger.exception(exc)
        raise (exc)
    dataset["Rawdata"] = rawdata_filenames
    return dataset
