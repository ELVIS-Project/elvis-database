import os
import json
import requests
import re

from django.core.management.base import BaseCommand
from django.conf import settings


def get_suggestions(query, suggester):
    """Tries to find an item already in the database with a similar name.

    Experiment to see if we can properly rename composers on the way into
    the elvis database.

    Args:
        query: The query string to match against.
        suggester: String denoting Which suggestor to query. Options in settings.SOLR_SUGGESTERS
    Returns: A list of suggestions.
    """
    if suggester not in settings.SOLR_SUGGESTERS:
        raise ValueError("'{}' is not a valid solr suggestor".format(suggester))

    url = "{}/suggest/?wt=json&suggest.dictionary={}&q={}".format(settings.SOLR_SERVER, suggester, query)
    try:
        resp = requests.get(url)
    except requests.RequestException:
        print("Failed to reach suggestion server.")
        return [query]
    resp_json = resp.json()
    suggestions = [sugg['term'] for sugg in resp_json['suggest'][suggester][query]['suggestions']]
    return suggestions if suggestions else [query]


def get_published_date(metadata):
    """Gets the year of publication from the published key in the metadata. Defaults to 0000."""
    published_metadata_links = metadata.get('Published', {}).get('links')
    if published_metadata_links:
        for link in published_metadata_links:
            if link[0].isdigit():
                return link[0]
    # Use '0000' to refer to unknown dates as this field is required.
    return '0000'


def get_num_voices(metadata):
    """Gets the number of voices from the metadata. Defaults to 0."""
    num_voices = metadata.get('Number of voices', {}).get('text', {})
    if not num_voices:
        return '0'
    #  Strip out anything not a number, as voices is stored as an int on elvisdb.
    only_digits =  re.sub('[^0-9]', '', num_voices)
    return only_digits if only_digits.isdigit() else '0'


def get_metadata_list(metadata, key, suggester=None, default=''):
    """Transform a list of some metadata on CW dump to representation for Elvis."""
    cw_list = metadata.get(key, {}).get('links', [])
    if not cw_list:
        return default

    elvis_list = []
    for item in cw_list:

        if suggester:
            elvis_list.append(get_suggestions(item[0], suggester)[0])
        else:
            elvis_list.append(item[0])

    return '; '.join(elvis_list)


def map_choral_to_elvis(metadata):
    """Map the choral metadata json-dump format to what Elvis expects for a piece upload.

    Args:
        metadata: A dict of metadata in the format from the choral wiki scrape.

    Returns: A new dict in a format ready to be POST'd to /pieces.
    """
    elvis_metadata = {
        'title': metadata.get('Title', {}).get('text', ''),
        'composer': get_suggestions(metadata.get('Composer', {}).get('text'), 'composerSuggest')[0],
        'composition_end_date': get_published_date(metadata),
        'collections': 'Unverified CW Collection',
        'number_of_voices': get_num_voices(metadata),
        'genres': get_metadata_list(metadata, 'Genre', 'genreSuggest', default='Unknown'),
        'instruments': get_metadata_list(metadata, 'Instruments', 'instrumentSuggest'),
        'languages': get_metadata_list(metadata, 'Languages', 'languageSuggest'),
        'comment': metadata.get('Description', {}).get('text', '')
    }
    elvis_metadata['comment'] += '\n\n From http://www3.cpdl.org{}'.format(metadata['url'])

    # Try to interpret whether its sacred or secular
    if 'sacred' in elvis_metadata['genres'].lower():
        elvis_metadata['religiosity'] = 'Sacred'
    elif 'secular' in elvis_metadata['genres'].lower():
        elvis_metadata['religiosity'] = 'Secular'
    else:
        elvis_metadata['religiosity'] = 'Uncategorized'

    # Try to interpret whether its vocal or not.
    if 'a cappella' in elvis_metadata['instruments'].lower():
        elvis_metadata['vocalization'] = 'Vocal'
    else:
        elvis_metadata['vocalization'] = 'Unknown'

    import pdb; pdb.set_trace()
    return elvis_metadata


def open_media_files(root_dir, metadata):
    piece_scores = []
    movement_scores = []
    for score in metadata['scores']:
        if score['meta']['CPDL#'] in metadata['movements']:
            movement_scores.append(score)
        else:
            piece_scores.append(score)

    file_counter = 1
    for piece_score in piece_scores:
        files = [x.split('/')[-1] for x in files['dl_links']]
        for file in files:
            with open(os.path.join(root_dir, file), 'rb') as f:
                metadata['files_file_{}'.format(str(file_counter))] = f
            metadata['files_parent_{}'.format(str(file_counter))] = "piece"
            metadata['files_source_{}'.format(str(file_counter))] = "Choral Wiki"
            ## TODO finish this function.


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

    metadata = map_choral_to_elvis(meta_json)


class Command(BaseCommand):
    """Import a piece into the database from a directory."""

    help = """Upload a Piece to the database from a directory. Expects there to be a file
     called `meta.json` in the directory. Currently only supports the metadata format created
     by the choralwiki scrape effort."""

    def add_arguments(self, parser):
        """Add the 'file' required argument to this command."""
        parser.add_argument("file", nargs=1, help="Path to directory to upload.")

    def handle(self, *args, **options):
        for file in options['file']:
            import_from_dir(file)
