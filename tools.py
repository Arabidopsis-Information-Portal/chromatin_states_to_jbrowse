import json
import os.path as op

gff_file_prefix = op.join(op.dirname(__file__), 'data', 'tpc124578_SupplementalDS2-state')

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
