#!/usr/bin/env python
import urllib3
import requests
import multiprocessing
import argparse
from contextlib import closing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

""" Proxies for requests. Useful for debugging, but you can make an empty dict to ignore """
proxies = {
    # 'http': 'http://127.0.0.1:8080',
    # 'https': 'http://127.0.0.1:8080',
}

def test_domain(options):
    """Validate Domain Fronting of a given subdomain with the target C2 `Host` header

    Keyword Arguments:
    options -- A tuple consisting of a subdomain to test and the `Host` header value.

    Returns:
    A string value of the validated subdomain or `None`.
    """
    domain, headers = options
    response = None
    try:
        response = requests.get(domain, headers=headers,
                                proxies=proxies, verify=False, timeout=10)
        if response.status_code == 200:
            return domain
        else:
            raise Exception((response.status_code, domain))
    except Exception as ex:
        message_partial = f'000 - {domain} - FAIL'
        # Catch an exception when the response was made but the return code != 200.
        if type(ex.args[0]) == tuple:
            status_code, domain = ex.args[0]
            message_partial = f'{status_code} - {domain}'
        # Catch an exception when the requests library encounters an error and return gracefully.
        elif ex.response:
            message_partial = f'{ex.response.status_code} - {domain}'
        # Catch an exception when requests cannot make a connection.
        elif type(ex) == requests.exceptions.ConnectionError:
            message_partial = f'XXX - {domain} - No connection'
        print(f'[!] - {message_partial}')
        return None

def main(path, ssl, cdn_domain, output_path):
    """The magic happens here

    Uses the requests Python library to test a list of subdomains to
    validate that the C2 infrastructure can communicate through Domain Fronting.

    Keyword arguments:
    path -- The path to the list of subdomains to be tested.
    ssl -- True|False value to determine the protocol used during testing.
    cdn_domain -- The FQDN of the CDN used to mask the C2.
    output_path -- The file to write successful results to.
    """
    contents = ''
    domains = []
    headers = {
        'Host': cdn_domain,
    }

    with open(path, 'r') as fh:
        contents = fh.read()
        domains = contents.split('\n')

    # Build a list of tuples to pass to the mapped test_domains method.
    test_options = [(f'{"https" if ssl else "http"}://{domain}', headers)
                    for domain in domains]

    # Use multiprocessing make things quicker.
    pool = multiprocessing.Pool(16)
    map_results = pool.map(test_domain, test_options)
    pool.close()

    # Filter out any subdomains that were found bad.
    trimmed_results = [result for result in map_results if result is not None]

    with open(output_path, 'a+') as fh:
        for domain in trimmed_results:
            fh.write(f'{domain}\n')

    print(f'saved {len(trimmed_results)} valid subdomains to file')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--domains-file',
                        help='Path to list of potential frontable domains.')
    parser.add_argument('-s', '--ssl', type=bool,
                        help='Prepend domain from list with http or https.')
    parser.add_argument('-c', '--cdn-domain', help='CDN FQDN for C2.')
    parser.add_argument('-o', '--output-file', help='Save results to file.')
    args = parser.parse_args()

    main(args.domains_file, args.ssl, args.cdn_domain, args.output_file)
