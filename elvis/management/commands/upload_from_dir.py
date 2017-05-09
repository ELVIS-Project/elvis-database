import os
import json
import requests

from django.core.management.base import BaseCommand
from django.conf import settings


def getSuggestions(query, suggestor):
    """Tries to find an item already in the database with a similar name.

    Experiment to see if we can properly rename composers on the way into
    the elvis database.

    Args:
        query: The query string to match against.
        suggestor: String denoting Which suggestor to query. Options in settings.SOLR_SUGGESTORS
    Returns: A list of suggestions.
    """
    if suggestor not in settings.SOLR_SUGGESTORS:
        raise ValueError("'{}' is not a valid solr suggestor".format(suggestor))

    url = "{}/suggest/?wt=json&suggest.dictionary={}&q={}".format(settings.SOLR_SERVER, suggestor, query)
    try:
        resp = requests.get(url)
    except requests.RequestException:
        print("Failed to reach suggestion server.")
        return [query]
    resp_json = resp.json()
    return [sugg['term'] for sugg in resp_json['suggest'][suggestor][query]['suggestions']]


def mapChoralToElvis(metadata):
    """Map the choral metadata json-dump format to what Elvis expects for a piece upload.

    Args:
        metadata: A dict of metadata in the format from the choral wiki scrape.

    Returns: A new dict in a format ready to be POST'd to /pieces.
    """
    elvis_metadata = {}

    import pdb; pdb.set_trace()
    elvis_metadata['title'] = metadata.get('Title', {}).get('text')
    elvis_metadata['']


    # Determine which scores are part of the piece and which are part of movements.
    piece_scores = []
    movement_scores = []
    for score in metadata['scores']:
        if score['meta']['CPDL#'] in metadata['movements']:
            movement_scores.append(score)
        else:
            piece_scores.append(score)

    return elvis_metadata


def import_from_dir(root_dir):
    """Import a piece from a directory on the file system.

    Args:
        root_dir: Path to a directory containing symbolic music files
                  and a files called meta.json

    Returns: Tuple (boolean:succeeded, string:error_message)
    """
    if not os.path.isdir(root_dir):
        return False, "{} is not a directory".format(root_dir)

    file_list = os.listdir(root_dir)
    if 'meta.json' not in file_list:
        return False, "No file named 'meta.json' in {}".format(root_dir)

    with open(os.path.join(root_dir, 'meta.json'), 'r') as f:
        meta_json = json.load(f)

    metadata = mapChoralToElvis(meta_json)


class Command(BaseCommand):
    """Import a piece into the database from a directory."""

    help = """Upload a Piece to the database from a directory. Expects there to be a file
     called `meta.json` in the directory. Currently only supports the metadata format created
     by the choralwiki scrape effort."""

    def add_arguments(self, parser):
        """Add the 'file' required argument to this command."""
        parser.add_argument("file", nargs=1, help="Path to directory to upload.")

    def handle(self, *args, **options):
        import pdb; pdb.set_trace()
        for file in options['file']:
            self.import_from_dir(file)

    def import_from_dir(self, root_dir):
        """Import a piece from a directory on the file system.

        Args:
            root_dir: Path to a directory containing symbolic music files
                      and a file called meta.json

        Returns: Tuple (boolean:succeeded, string:error_message)
        """
        if not os.path.isdir(root_dir):
            return False, "{} is not a directory".format(root_dir)

        file_list = os.listdir(root_dir)
        if 'meta.json' not in file_list:
            return False, "No file named 'meta.json' in {}".format(root_dir)

        with open(os.path.join(root_dir, 'meta.json'), 'r') as f:
            meta_json = json.load(f)

        metadata = mapChoralToElvis(meta_json)
