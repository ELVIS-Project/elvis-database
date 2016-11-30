In November of 2016, we deleted a large number of duplicated files from the database. This directory contains
a record of how these files were discovered and which files were ultimately deleted.

The command in elvis.management.generate_file_reports was used to generate a list of duplicated files on the
database. It works by hashing all files, then grouping together attachments with have the same file hash. The result
of running this function is found in `duplicated_file_report.json`.

This list of duplicated files was further processed to organize them by composer and piece rather than by hash. This
final list contains all the files that were deleted on this day. The hope is that this list will make it easier to
reason about which files need to be replaced. This list is found in `deleted_files.json`.
