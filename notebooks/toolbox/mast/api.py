from __future__ import division, absolute_import, print_function
import requests
import json
import os.path

from .. import utils

MAST_API_URL = 'https://mast.stsci.edu/api/v0/invoke'

__all__ = (
    'MAST_API_URL',
    'lookup_name',
    'cone_search',
    'filtered_search',
    'retrieve',
    'update_header_from_fitscut',
    '_api_request',
)


def _noop(*_):
    pass


def update_header_from_fitscut(header, obs_id):
    new_wcs = requests.get('http://hla.stsci.edu/cgi-bin/fitscut.cgi',
                           {'red': obs_id, 'getWCS': 1}).json()
    for idx, keyword in enumerate(('CD1_1', 'CD1_2', 'CD2_1', 'CD2_2')):
        header[keyword] = new_wcs['cdmatrix'][idx]
    header['CRPIX1'], header['CRPIX2'] = new_wcs['crpix']
    header['CRVAL1'], header['CRVAL2'] = new_wcs['crval']
    assert header['NAXIS1'] == new_wcs['imsize'][0]
    assert header['NAXIS2'] == new_wcs['imsize'][1]
    return header


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


def retrieve(obsids, directory=None, verbose=False):
    if directory is not None:
        utils.ensure_dir(directory)
    if verbose:
        log = print
    else:
        log = _noop
    payload = {
        'service': 'Mast.Caom.Products',
        'params': {'obsid': ','.join(map(str, obsids))},
        'format': 'json'
    }
    response = _api_request(payload)
    filenames = []
    log("Found", len(response['data']), "products")
    for data_product in response['data']:
        if directory is not None:
            filename = os.path.join(directory, data_product['productFilename'])
        else:
            filename = data_product['productFilename']
        if not os.path.exists(filename):
            log("Retrieving", data_product['dataURI'])
            assert 'https://' in data_product['dataURI']
            r = requests.get(data_product['dataURI'])
            with open(filename, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=128):
                    fd.write(chunk)
        else:
            log("Using existing", filename)
        filenames.append(filename)
        log("Done with", filename)
    return filenames
