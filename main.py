import json

import tools


def fail(message):
    # This is a simple failure message generator for generic ADAMA adapters
    # It will eventually be replaced with a system-wide fail function
    return 'text/plaintext; charset=ISO-8859-1', message


def search(args):
    q = args['q']
    chrom = args['chr']
    start = args['start']
    end = args['end']
    if start >= end:
        fail('End coordinate must be greater than start')
    featuretype = args['featuretype']
    cstate = 1 if 'cstate' not in args else \
        args['cstate']

    if q == 'features':
        data = tools.parse_gff(chrom=chrom, start=start, \
            end=end, featuretype=featuretype, chromatin_state=cstate)

        if not data:
            return fail('Failed to parse gff')
    elif q == 'globalStats':
        data = { 'scoreMin': -1, 'scoreMax': 1 }

    return 'application/json', tools.sendJBrowse(data)


def list(args):
    import requests

    url = 'https://api.araport.org/community/v0.3/aip/get_sequence_by_coordinate_v0.3/list'
    token = args['_token']

    response = requests.get(url, \
        headers={ 'Authorization': 'Bearer {0}'.format(token) })

    # Raise exception and abort if requests is not successful
    response.raise_for_status()

    data = None
    try:
        # Try to convert result to JSON
        # abort if not possible
        data = response.json()
    except ValueError:
        raise Exception('not a JSON object: {}'.format(response.text))

    return 'application/json', data
