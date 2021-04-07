import os
import sys
import json
import pkg_resources
from operator import itemgetter
from collections import defaultdict

if not (sys.version_info.major == 3 and sys.version_info.minor >= 9):
    # Ensure we have the Python 3.9 to avoid missing features

    version = sys.version_info
    print('This script requires Python 3.9 or higher!')
    print(f'You are using Python {version.major}.{version.minor}.')
    sys.exit(0)

with open('requirements.txt') as req_file:
    # Use the requirements.txt file to check if we have all dependencies
    # for this script to run properly.

    requirements = pkg_resources.parse_requirements(req_file)
    try:
        pkg_resources.require([str(r) for r in requirements])

    except pkg_resources.DistributionNotFound as err:
        print(err)
        print('Please run in the current directory:')
        print('python -m pip install -r requirements.txt')
        sys.exit(0)


import argh
import boto3
from terminaltables import AsciiTable

import models
from schema import create_document
from exceptions import DuplicateDocument


CACHE_FOLDER = './cache'
S3_BUCKET_NAME = '1up-coding-challenge-patients'


def load_data(drop_cache: bool = False) -> dict[str, list[dict]]:
    """ Returns a list of documents from cache or from S3 """

    cache_file = CACHE_FOLDER + '/resources.json'

    if not os.path.exists(cache_file) or drop_cache:
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(name=S3_BUCKET_NAME)

        resources = defaultdict(list)
        for o in bucket.objects.all():
            jstr = [
                json.loads(n) for n
                in o.get()['Body'].read().decode("utf-8").split('\n') if n
            ]
            for js in jstr:
                resources[js['resourceType']].append(js)

        with open(cache_file, 'w') as f:
            f.write(json.dumps(resources, indent=2))

    else:
        with open(cache_file) as f:
            resources = json.loads(f.read())

    return resources


def init(drop_cache: bool = False):
    """ Initiate the in-memory database with documents fetched from S3 """

    for resource_type, resources in load_data(drop_cache=drop_cache).items():
        for resource in resources:
            try:
                create_document(resource)

            except DuplicateDocument:
                # Some duplicated documents?
                pass


@argh.arg('resource_type', choices=['patient', 'practitioner'],
          help='Select the resource type to search for')
@argh.arg('terms', help='Enter any ID or combination of words')
@argh.arg('--nocache', '-n', help='Re-fetch documents from S3')
def search(resource_type: str, terms: str, nocache: bool = False) -> None:
    """ Search the in-memory database for documents """

    init(drop_cache=nocache)
    model = getattr(models, resource_type.title())

    if not(result := model.get(terms)):
        results = list(model.find(terms))

        if (nb := len(results)) == 1:
            result = results[0]

        else:
            print(f'Found {nb} {resource_type}s for your search')

            if nb > 9:
                print('Please refine your search.')
                sys.exit(0)

            for i in range(1, nb + 1):
                p = results[i-1]
                print(f"{i}) {p.get_fullname()} ({p.id})")

            while True:
                q = f'Type your choice [1-{i}] (ENTER to exit): '
                selected = input(q)

                if selected is None or selected.strip() == '':
                    sys.exit(0)

                try:
                    result = results[int(selected)-1]
                    break

                except (IndexError, ValueError):
                    print(f'> Enter a valid numeric value [1-{i}]')
                    continue

    if not result:
        print(f'No {resource_type} found for this search')
        return

    connections = result.get_connections()
    resources = [(name, len(inst)) for name, inst in connections.items()]
    resources = sorted(resources, key=itemgetter(1))[::-1]

    headers = ['RESOURCE TYPE', 'COUNT']
    table = AsciiTable([headers, *resources])

    print()
    print(f'Name: {result.get_fullname()}')
    print(f'ID: {result.id}')
    print(table.table)


if __name__ == '__main__':
    parser = argh.ArghParser()
    parser.add_commands([search])
    parser.dispatch()
