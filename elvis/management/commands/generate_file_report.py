import os
import hashlib
from collections import defaultdict
import json

from django.core.management import BaseCommand
from elvis.models import Attachment, Piece, Movement
from elvis.models.attachment import ParentResolveError


class Command(BaseCommand):
    """Find missing and duplicated media files and output a report"""

    help = """Generate a report on missing and duplicated files. Use shell
    redirection to save as file of your choice. """

    def handle(self, *args, **options):
        missing, dupes = self.generate_missing_and_dupes()
        results = self.normalize_results(missing, dupes)
        jdump = json.dumps(results, indent=4, sort_keys=True)
        print(jdump)

    @staticmethod
    def generate_missing_and_dupes():
        """Create a list of missing files, and a dict of duplicated files.

        The dict of duplicated files will have hash values as keys, and
        lists of Attachment objects as values. Each Attachment object in
        the list points to a file with the same hash.

        :return (list, defaultdict(list))
        """
        missing = []
        possible_dupes = defaultdict(list)
        for a in Attachment.objects.all():
            path = a.attachment.path
            if not os.path.exists(path):
                missing.append(a)
                continue
            with open(path, 'rb') as f:
                hasher = hashlib.md5()
                hasher.update(f.read())
                file_hash = hasher.hexdigest()
                possible_dupes[file_hash].append(a)
        real_dupes = {k: v for k, v in possible_dupes.items() if len(v) > 1}
        return missing, real_dupes

    @staticmethod
    def normalize_results(missing, dupes):
        """Make a json-serializable dict out of missing and dupes."""
        result = {'dupes': [], 'missing': []}

        for a in missing:
            res = Command._get_att_info_dict(a)
            res['path'] = a.attachment.path
            result['missing'].append(res)

        # Create a list of dupes grouped together by hashes.
        sorted_keys = sorted(dupes.keys(), key=lambda x: -len(dupes[x]))
        for k in sorted_keys:
            dupe_dict = {'count': len(dupes[k]), 'hash': k, 'lst': []}
            for a in dupes[k]:
                res = Command._get_att_info_dict(a)
                dupe_dict['lst'].append(res)
            result['dupes'].append(dupe_dict)

        # Eliminate any dupes from the list that are all from the same composer.
        def is_real_dupe(dupe_lst):
            """True if dupe spans multiple composers or has more than 10 files."""
            if len(dupe_lst) >= 10:
                return True
            first_composer = dupe_lst[0]['composer']

            if len(dupe_lst) > 2:
                for d in dupe_lst:
                    if d['composer'] != first_composer:
                        return True
            return False

        pruned_dupes = []
        for dupe in result['dupes']:
            if is_real_dupe(dupe['lst']):
                pruned_dupes.append(dupe)
        result['dupes'] = pruned_dupes

        return result

    @staticmethod
    def _get_att_info_dict(att):
        """Return a small dict with the attachments info."""
        base = {'piece': None, 'piece_id': None, 'movement': None, 'movement_id': None}
        try:
            parent = att.parent
        except ParentResolveError:
            return base
        if isinstance(parent, Piece):
            base['piece'] = parent.title
            base['piece_id'] = str(parent.pk)
        elif isinstance(parent, Movement):
            base['piece'] = parent.piece.title if parent.piece else None
            base['piece_id'] = str(parent.piece.pk) if parent.piece else None
            base['movement'] = parent.title
            base['movement_id'] = str(parent.pk)
        else:
            raise TypeError("Expected Movement or Piece as parent.")
        base['composer'] = parent.composer.title
        base['att_id'] = str(att.id)
        base['path'] = att.attachment.path
        return base

    @staticmethod
    def organize_dupes(results):
        """Organize duplicate list as a hierarchical dict.

        This function is used to make it easy to turn the report generated
        by generate_missing_and_dupes() into an human-readable hierarchy of
        instances that need to be replaced.

        Args:
            results: The results of generate_missing_and_dupes()
        Returns: An  dict of dupes indexed by piece id.
        """
        organized_results = defaultdict(dict)
        for duplicates in results['dupes']:
            for dupe_instance in duplicates['lst']:
                composer = dupe_instance.get("composer")
                piece_title = dupe_instance.get('piece', 'NO_PIECE')
                stripped_instance = {
                    'att_id': dupe_instance['att_id'],
                    'att_title': dupe_instance['path'].split('/')[-1],
                    'movement': dupe_instance['movement']
                }
                if not organized_results[composer].get(piece_title):
                    organized_results[composer][piece_title] = []
                organized_results[composer][piece_title].append(stripped_instance)

        return organized_results
