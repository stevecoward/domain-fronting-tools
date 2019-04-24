#!/usr/bin/env python
import urllib3
import json
import requests
import multiprocessing
import copy
import argparse
from contextlib import closing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

""" Censys URL and API settings """
base_url = 'https://censys.io/api/v1'
auth_uid = 'e8c59fea-3545-4700-b335-a46aad4d4ab7'
auth_secret = 'nmqCn5Vu2OmU9ikFJyahSDKsksQNMdr2'

""" Proxies for requests. Useful for debugging, but you can make an empty dict to ignore """
proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080',
}

def make_request(endpoint, query):
    """Make an API request to Censys

    Takes an API endpoint (e.g. /search/certificates) and retrieves a JSON object of results.

    Keyword arguments:
    endpoint -- Censys search endpoint (e.g. `/search/[certificates|websites|ipv4]`).
    query -- A search term to request from Censys.

    Returns:
    A JSON object or an empty dict if no results were returned.
    """
    response = requests.post(f'{base_url}{endpoint}', auth=(
        auth_uid, auth_secret), json=query, proxies=proxies, verify=False)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print(f'request failed with status: {response.status_code}')
        return {}


def trim_results(domain, data):
    """Parse a JSON object and remove unwanted results
    
    Keyword arguments:
    domain -- A user-supplied domain name.
    data -- A JSON object of Censys results.

    Returns:
    A list of subdomains matching the domain variable.
    """
    return [subdomain for subdomain in [item for sublist in [result['parsed.names'] for result in data] for item in sublist] if domain in subdomain]


def get_results(options):
    """Facilitate API request and processing of results

    Keyword arguments:
    options -- A tuple consisting of a Censys API endpoint, the domain to be searched and a search query.

    Returns:
    A list of subdomains matching the domain variable for the given search query.
    """
    endpoint, domain, query = options
    data = make_request(endpoint, query)
    return trim_results(domain, data['results'])


def main(domain, pages):
    """The magic happens here"""
    endpoint = '/search/certificates'
    query = {'query': f'parsed.names: {domain}',
             'page': 1, "fields": ["parsed.names"]}
    queries = []

    """Create a list of dictionaries for the number
    of pages of results we want to return using
    the default `query` variable above.
    """
    for page_num in range(1, pages+1):
        page_query = copy.copy(query)
        page_query['page'] = page_num
        queries.append((endpoint, domain, page_query))

    # Use multiprocessing to quickly pull and process the api results.
    pool = multiprocessing.Pool(8)
    map_results = pool.map(get_results, queries)
    pool.close()

    """Flatten the results returned from map(), otherwise `results_list`
    will be a list of lists.
    """
    results_list = [record for sublist in map_results for record in sublist]
    for subdomain in results_list:
        print(subdomain)
    print(f'\nretrieved: {len(results_list)} possible frontable domains')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--domain', help='Search censys for certs using domain')
    parser.add_argument('-p', '--pages', type=int,
                        help='Number of pages to retrieve (100/page)')
    args = parser.parse_args()

    main(args.domain, args.pages)
