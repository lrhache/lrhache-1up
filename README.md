# 1UP Coding Challenge

## Design

I had 3 considerations before starting this project:
1. How the documents would be organized, manipulated and retrieved
2. How the documents would reference each others (ability to find parents and children documents)
3. Reusability and extendability of the data models

#### Data structure
I have opted to load the documents into dataclasses model as this would be the closest python datastructure mimicking modern database ORM data model.

This data structure creates the effect of a virtual object database that can be used and accessed intuitively.

With the use of the metaclass applied on the data model, we can intercept the creation of new objects,
create the search index and finding the back references.

Each models can be extended easily as seen with the `Patient` and `Practitioner` models with the `get_fullname` method.

#### Foreign relations
During the document initialization, if there is any references to foreign documents, we create a back reference to those objects and store the references also into the created model.

This simple process allow a quick access to referenced documents with little overhead.

I have also implemented a dotkey notation for increase readability of the document models. This notation allow the reader to quickly understand the values accessed. IE: `index = ['name.given', 'name.family']`

#### Search
As a proof of concept, I initialized the practitioner search as well by simply adding the `index` attribute to the `Practitioner` model. Working the same way as the patient search, you can also access an aggregated count of documents related to the selected practitioner.

When I can, I like to remove any restrictions that have no obvious reason to exists. For this reason, I wrote the script to allow any search terms without having to specify the type (no --firstname or --id flags needed). If your search yield more than one document, you will be prompt with suggestions.

#### Tests
I wrote a few unit test cases, they are not exhaustive but they represent well the major parts of the system (load data, search, reference backlinking).

Overall, this was a fun project with the hope it demonstrate well my personality as a SWE!

Louis.


## Run

#### Docker
I've included a dockerfile for your convenience, or you can install through a virtual env.

Build app:
```bash
docker build -t lrhache-1up-challenge .
```

Run app:
```bash
docker run -it --rm lrhache-1up-challenge python3 tests.py
docker run -it --rm lrhache-1up-challenge python3 app.py help
docker run -it --rm lrhache-1up-challenge python3 app.py help search
```

#### Virtual env

Create a virtual environment with python >= 3.9.0

Install requirements:
```bash
pip install -r requirements.txt
```

## Usage

Run tests:
```bash
python3 tests.py
docker run -it --rm lrhache-1up-challenge python3 tests.py
```

MyPy:
```bash
mypy app.py
docker run -it --rm lrhache-1up-challenge mypy app.py
```

Search for any patients:
```bash
python3 app.py search patient <your query>
docker run -it --rm lrhache-1up-challenge python3 app.py search patient <your query>
```

Search for any practitioner:
```bash
python3 app.py search practitioner <your query>
docker run -it --rm lrhache-1up-challenge python3 app.py search practitioner <your query>
```

I would suggest a few patient searches:
* Single ID: "c4768f2a-f932-4ab6-a4a5-6e8ae0f9da8d"
* Part of ID: "c4768f2a"
* Single letter: "a"
* Some letters: "ab"
* Some letters combination: "ab tree"
* Full name: "Abernathy"


## Task

Create a program to fetch patients' data, order, search and retrieve a single patient findings aggregate.

## Plan

1. Fetch the data file from S3 Bucket (boto3) (s3://1up-coding-challenge-patients)
2. Parse the file to extract each resources (JSON)
3. Load each resources into a defined data model per patients or referenced object
4. Allow search and indexing (register primary field to search, register all resources across all models)
5. Write a CLI taking the input (patient id, first name, last name) and return the aggregated findings

