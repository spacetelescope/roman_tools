import requests
from urllib.parse import urlencode
import json

MAST_API_URL = 'https://mast.stsci.edu/api/v0/invoke'

def _api_request(payload):
    response = requests.post(MAST_API_URL, {'request': json.dumps(payload)})
    if response.status_code == 200:
        return response.json()
    else:
        raise RuntimeError('MAST API returned status {} for payload {}'.format(response.status_code, payload))

def lookup_name(name):
    payload = {'service': 'Mast.Name.Lookup',
                    'params': {'input': name, 'format':'json'}}
    response = _api_request(payload)
    if len(response['resolvedCoordinate']) == 0:
        raise ValueError("Could not resolve target name {}".format(name))
    elif len(response['resolvedCoordinate']) > 1:
        raise ValueError("Multiple target coordinates for target name {}".format(name))
    else:
        coords = response['resolvedCoordinate'][0]
        return {
            'canonicalName': coords['canonicalName'],
            'ra': coords['ra'],
            'dec': coords['decl'],
        }
    return response

def cone_search(ra, dec, radius_arcsec=0.2):
    payload = {
        'service': 'Mast.Caom.Cone',
        'params': {'ra': ra, 'dec': dec, 'radius':0.2},
        'format': 'json',
        'pagesize': 2000,
        'page': 1,
        'removenullcolumns': True,
        'removecache': True
    }
    response = _api_request(payload)
    return response

def filtered_search(ra, dec, filters=None, radius_arcsec=0.2):
    payload = {
        'service': 'Mast.Caom.Filtered.Position',
        'format': 'json',
        'params': {
            'columns': '*',
            'filters': [
                {'paramName': key, 'values': values}
                for key, values
                in filters.items()
            ],
            'position': '{ra}, {dec}, {radius_arcsec}'.format(
                ra=ra, dec=dec, radius_arcsec=radius_arcsec
            ),
        }
    }
    return _api_request(payload)

def _retrieve_obsid(obsid, verbose=False):
    payload = {
        'service': 'Mast.Caom.Products',
        'params': {'obsid': obsid},
        'format': 'json'
    }
    response = _api_request(payload)
    filenames = []
    if verbose:
        print("Found", len(response['data']), "products")
    for data_product in response['data']:
        if verbose:
            print("Retrieving", data_product['dataURI'])
        assert 'https://' in data_product['dataURI']
        r = requests.get(data_product['dataURI'])
        filename = data_product['productFilename']
        with open(filename, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
            filenames.append(filename)
            if verbose:
                print("Done with", filename)
    return filenames

def retrieve(obsids, verbose=False):
    filenames = []
    for obsid in obsids:
        filenames.extend(_retrieve_obsid(obsid, verbose=verbose))
    return filenames
