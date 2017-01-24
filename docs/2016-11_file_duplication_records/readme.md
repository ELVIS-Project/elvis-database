In November of 2016, we deleted a large number of duplicated files from the database. This directory containsa record of how these files were discovered and which files were ultimately deleted.

The command in elvis.management.generate_file_reports was used to generate a list of duplicated files on thedatabase. It works by hashing all files, then grouping together attachments with have the same file hash. The result
of running this function is found in `duplicated_file_report.json`.

This list of duplicated files was further processed to organize them by composer and piece rather than by hash. Thisfinal list contains all the files that were deleted on this day. The hope is that this list will make it easier toreason about which files need to be replaced. This list is found in `deleted_files.json`.


The following is the full script used to delete files. This was used in the shell interface provided by django.

```python
import json

from elvis.models import Attachment

with open('deleted_files.json', 'r') as f:
    deleted_files = json.load(f)

Attachments_to_delete = []
for composer_pieces in deleted_files.values():
    for piece in composer_pieces:
        attachments = composer_pieces[piece]
        for att_dict in attachments:
            attachment = Attachment.objects.get(pk=att_dict['att_id'])
            Attachments_to_delete.append(attachment)
            
len(Attachments_to_delete) # Make sure we're not deleting everything!
for a in Attachments_to_delete:
    a.delete()
```

Backups of the database and media files before this operation was run exist on the shared backup server under `/mnt/elvis_database/pre_dupe_delete_dump`.
