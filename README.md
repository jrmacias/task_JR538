# Software Developer JR538 - Task

Sample application to retrieve metabolomics public dataset (metadata and result files) from the relevant repositories.

- The following frameworks and libraries were used:

    | Library | Version | Description |
    | :------ |--------:| :-----------|
    | [Django](https://www.djangoproject.com/) | `4.2.20` | main project and application framework |
    | [Django REST framework](https://www.django-rest-framework.org/) | `3.15.2` | REST API management |
    | [drf-yasg](https://drf-yasg.readthedocs.io/) | `1.21.10` | Swagger and ReDoc API documentation |
    | [pandas](https://pandas.pydata.org/) | `2.2.3` | parsing *.csv and *.tsv files |
    | [python-dotenv](https://pypi.org/project/python-dotenv/) | `1.0.1` | loading evironment variables from .env file |
    | *ftplib*, [Requests](https://pypi.org/project/requests/) |  | tfp and http(s) queries |
    | *HTMLParser*, *json* |  | parsing HTML and JSON responses |
    | *RegEx* | | searching filename patterns using regular expressions |
    | [Bootstrap](https://getbootstrap.com/) | `5.3.3` | web UI framework |
    | [django-crispy-forms](https://django-crispy-forms.readthedocs.io/) | `2.3` | for better looking web forms |
- other general purpose libraries (see the [requirements.txt](requirements.txt) file)

<br/>

[Visual Studio Code](https://code.visualstudio.com/) (VSC) was used to edit, compile and debug the application code. 
- Following relevant VSC extensions were used:

    | Extension | Description |
    | :-------- | :-----------|
    | [Pylint](https://marketplace.visualstudio.com/items?itemName=ms-python.pylint) | syntax and bug hunting |
    | [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance), [autopep8](https://marketplace.visualstudio.com/items/ms-python.autopep8/), [isort](https://marketplace.visualstudio.com/items?itemName=ms-python.isort) | code formatting in Python and imports sorting and handling |
    | [Gitflow](https://marketplace.visualstudio.com/items?itemName=vector-of-bool.gitflow), [Git-Graph](https://marketplace.visualstudio.com/items?itemName=mhutchie.git-graph) | help with git actions management |



\* no LLM's where used to generate code.


## Installation & Setup:
This instructions are provided for a Linux or Mac OS environment. The application could also work in a Windows system, but it has not been tested.
- Clone the application repository to a suitable local folder
    ``` bash
    git clone https://github.com/jrmacias/task_jr538 task_jr538
    cd task_jr538
    ```
- Create a new virtual environment and install required libraries
    ``` bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
- copy .env_example to .env and change variables content as required using your editor of preference
    ``` bash
    cp .env_example .env
    nano .env
    ```
- Set up a database, populating tables with initial data and create an administrator account to get access to the admin section of the web UI
    ``` bash
    python manage.py migrate
    python manage.py createsuperuser
    ```
- Finally, start the server, replacing local IP and port if needed
    ``` bash
    python manage.py runserver 127.0.0.1:8000
    ```
- Go to http://127.0.0.1:8000/ in your favorite web browser

## Parsing Metadata & Result files:

### [MetaboLights](https://www.ebi.ac.uk/metabolights)
- s_xxx.txt, i_xxx.txt, a_xxx.txt and m_xxx.tsv files are downloaded from:
    - https://ftp.ebi.ac.uk/pub/databases/metabolights/studies/public/
using a ftp connection.
- metadata is parsed from s_xxx.txt file.
- the list of metabolites is obtained from m_xxx.tsv file.
- the list of rawdata filenames is obtained from the corresponding FILES directory:
    - https://ftp.ebi.ac.uk/pub/databases/metabolights/studies/public/MTBLSxxx/FILES


### [Metabolomics Workbench](https://www.metabolomicsworkbench.org)
- STUDY_ID and ANALYSIS_ID are obtained from: https://www.metabolomicsworkbench.org/rest/study/study_id/STxxx/analysis
which returns a JSON-formated response.
- with that, both queries can be done to download:
    - STxxx.json:		https://www.metabolomicsworkbench.org/data/study_textformat_view.php?JSON=YES&STUDY_ID={STxxx}&ANALYSIS_ID={ANxxx}&MODE=d
    - STxxx.mwtab.txt:		https://www.metabolomicsworkbench.org/data/study_textformat_view.php?STUDY_ID={STxxx}&ANALYSIS_ID={ANxxx}&MODE=d
- then, metadata and the list of metabolites are parsed from STxxx.json file


### [Metabobank](https://www.ddbj.nig.ac.jp/metabobank)
- xxx.idf.txt, xxx.srdf.txt and xxx.filelist.txt files where downloaded from:
    - https://ddbj.nig.ac.jp/public/metabobank/study/{accession}/{accession}.{idf|srdf|filelist}.txt
- HTMLParser was used to parse html response from:
    - https://ddbj.nig.ac.jp/public/metabobank/study/MTBKxxx/ in order to find all xxx.maf.yyy.txt files and then be downloaded
- metadata is parsed from xxx.idf.txt file.
- the list of metabolites is obtained from xxx.maf.txt files.
- the list of rawdata filenames is obtained from the xxx.filelist.txt file, filtering for Type='raw'.

\* After first query for an accession code, all metadata files are stored locally to be reused in future requests.
