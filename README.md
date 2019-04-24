
Domain Fronting Tools
=========

### Summary:

This is a collection of scripts that can be useful if Domain Fronting is required during ESEs or Red Team ops.

#### Requirements

- Python 3.x
- `requests` Python library

#### Tools

##### `cdn-search.py`

This script searches Censys records for certificates whose subject names partially match a CDN endpoint. From this list, a secondary script can parse the list and validate whether the subdomain can be used for Domain Fronting.

###### Usage

```
$ python cdn-search.py -h                                                                                           
usage: cdn-search.py [-h] [-d DOMAIN] [-p PAGES]

optional arguments:
  -h, --help            Show this help message and exit
  -d DOMAIN, --domain DOMAIN
                        Search censys for certs using domain
  -p PAGES, --pages PAGES
                        Number of pages to retrieve (100/page)
```

---

##### `validate-domains.py`

This script takes a text file of subdomains and a C2 CDN domain name and checks that Domain Fronting is operating properly. Good results are saved to a text file. Multiprocessing is very useful here, as the list of subdomains likely contain defunct servers who may take a long time to try and connect. Speed tests averaged around 1k domains validated per minute. Single threaded was considerably slower.

###### Usage

```
$ python validate-domains.py -h
usage: validate-domains.py [-h] [-f DOMAINS_FILE] [-s SSL] [-c CDN_DOMAIN]
                           [-o OUTPUT_FILE]

optional arguments:
  -h, --help            show this help message and exit
  -f DOMAINS_FILE, --domains-file DOMAINS_FILE
                        Path to list of potential frontable domains.
  -s SSL, --ssl SSL     Prepend domain from list with http or https.
  -c CDN_DOMAIN, --cdn-domain CDN_DOMAIN
                        CDN FQDN for C2.
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Save results to file.
```
