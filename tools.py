import json
import requests
import os.path as op

gff_file_prefix = op.join(op.dirname(__file__), 'data', 'tpc124578_SupplementalDS2-state')
config_data_file = op.join(op.dirname(__file__), 'data', 'chromatin_states_color_description.tsv')

def read_index(gff_file, inmemory=False):
    """
    Read in a gffutils index for fast retrieval of features.
    """
    import gffutils
    from subprocess import call

    gff_file_db = "{0}.db".format(gff_file)
    gff_file_db_gz = "{0}.gz".format(gff_file_db)

    if inmemory:
        return gffutils.create_db(gff_file, ':memory:')

    if op.exists(gff_file_db_gz):
        call('gunzip {0}'.format(gff_file_db_gz), \
            shell=True, executable='/bin/bash')

    if op.exists(gff_file_db):
        return gffutils.FeatureDB(gff_file_db)

    return gffutils.create_db(gff_file, gff_file_db)


def parse_gff(chrom, start, end, featuretype, chromatin_state):
    """Parse GFF and return JSON."""

    gff_file = "{0}_{1}.gff3".format(gff_file_prefix, chromatin_state)
    db = read_index(gff_file)

    response_body = { 'features' : [] }
    region = "{0}:{1}-{2}".format(chrom, start, end)
    for feat in db.region(region=region, featuretype=featuretype):
        _strand = 1 if feat.strand == '+' else \
            (-1 if feat.strand == '-' else 0)
        pfeat = {
            'start' : feat.start,
            'end' : feat.end,
            'strand' : _strand,
            'uniqueID' : feat.id,
            'name' : feat.attributes.get('Name', [feat.id])[0],
            'description' : feat.attributes.get('Note', [None])[0],
            'type' : featuretype,
            'score' : feat.score if (isinstance(feat.score, (int, float))) else 0,
            'subfeatures': []
        }

        response_body['features'].append(pfeat)

    return response_body


def generate_config(api_endpoint):
    """Generate the required trackList.json config stanzas for JBrowse"""

    config_template = {
        "style" : {
            "color" : "%(color)s"
        },
        "displayMode": "compact",
        "key" : "Chromatin State %(state)s",
        "storeClass" : "Araport/Store/SeqFeature/REST",
        "baseUrl" : "%(endpoint)s",
        "type" : "JBrowse/View/Track/CanvasFeatures",
        "category" : "Community Data / Sequeira-Mendes et al. 2014",
        "metadata" : {
            "Description" : "%(description)s",
            "Source" : "Sequeira-Mendes, et al. 2014 (Plant Cell)",
            "URL" : "http://www.plantcell.org/content/early/2014/06/11/tpc.114.124578"
        },
        "glyph" : "JBrowse/View/FeatureGlyph/Box",
        "label" : "chromatin_state_%(state)s",
        "query" : {
            "chromatin_state" : "%(state)s"
        }
    }

    config = []
    fp = open(config_data_file)
    for row in fp:
        if row[0] == '#':
            continue
        if row.strip() == "":
            continue
        atoms = row.rstrip("\r\n").split("\t")
        config.append(replace_in_dict(config_template, \
              { 'state': str(atoms[0]),
                'color' : atoms[1],
                'description' : atoms[2],
                'endpoint' : api_endpoint
              })
        )

    fp.close()

    return config


def replace_in_dict(input, variables):
    """
    Method to replace placeholders in dict
    source: http://stackoverflow.com/questions/33046828/string-replace-format-placeholder-values-in-a-nested-python-dictionary
    """
    result = {}
    for key, value in input.iteritems():
        if isinstance(value, dict):
            result[key] = replace_in_dict(value, variables)
        else:
            result[key] = value % variables
    return result


def do_request(url, token, **kwargs):
    """Perform a request to SITE and return response."""

    headers = {"Authorization": "Bearer %s" % token}
    response = requests.get(url, headers=headers, params=kwargs)

    # Raise exception and abort if requests is not successful
    response.raise_for_status()

    try:
        # Try to convert result to JSON
        # abort if not possible
        return response.json()
    except ValueError:
        raise Exception('not a JSON object: {}'.format(response.text))


def sendJBrowse(data):
    """Display `data` in the format required by JBrowse.

    """
    return json.dumps(data)


def sendList(data):
    """Display `data` in the format required by Adama.

    :type data: list

    """

    for elt in data:
        print json.dumps(elt)
        print '---'


def send(data):
    """Display `data` in the format required by Adama.

    """
    print json.dumps(data)
    print '---'
