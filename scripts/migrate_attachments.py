
""" Unicode Remover script
Attempts to convert file-names to ascii, if they fail, then rename them
using only ascii. Needed because the django file static server view
does not always play nice with unicode in filenames.
"""
def rename_files_to_ascii():
    import os.path
    import unicodedata
    from django.core.files import File
    path_err = 0
    val_err = 0
    open_err = 0
    to_be_renamed = 0
    a1 = None
    for a in Attachment.objects.all():

        try:
            path, file_name = os.path.split(a.attachment.path)
        #catch Attachments which don't have files and delete them
        except ValueError:
            print("has no value" + str(a.id))
            a.delete()
            val_err += 1
            continue

        try:
            # if its already ascii, skip it
            file_name.encode('ascii')
            continue
        except UnicodeEncodeError:
            if not a1:
                a1 = a
            to_be_renamed += 1
            pass

        old_path = a.attachment.path
        with open(old_path, 'r+b') as f:
            pass
        new_name = unicodedata.normalize('NFKD', file_name).encode('ascii', 'ignore')
        new_name = new_name.decode('utf-8')
        new_path = os.path.join(path, new_name)

        with open('name_changes', 'a') as file:
            file.write(old_path + ", " + new_path)
            file.write("\n")

        new_name = os.path.splitext(new_name)
        a.rename(new_name[0])

    print("Path errors = " + str(path_err) + ", open errors = " + str(open_err)
          + ", to be renamed = " + str(to_be_renamed) + ", val_errs: " + str(val_err))


""" Re-index script
Nukes the solr database and re-indexes everything. Someday I'm sure
this will be useful again.
"""


def reindex_all():
    from elvis.models.collection import Collection
    from elvis.models.composer import Composer
    from elvis.models.genre import Genre
    from elvis.models.instrumentation import InstrumentVoice
    from elvis.models.language import Language
    from elvis.models.location import Location
    from elvis.models.source import Source
    from elvis.models.tag import Tag

    from elvis.models.piece import Piece
    from elvis.models.movement import Movement

    import solr
    from django.conf import settings
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)

    # delete everything
    solrconn.delete_query("*:*")
    solrconn.commit()

    print("Indexing collections...")
    for c in Collection.objects.all():
        c.solr_index(commit=False, solrconn=solrconn)
    solrconn.commit()

    print("Indexing composers...")
    for c in Composer.objects.all():
        c.solr_index(commit=False, solrconn=solrconn)
    solrconn.commit()

    print("Indexing genres...")
    for g in Genre.objects.all():
        g.solr_index(commit=False)
    solrconn.commit()

    print("Indexing instrument voices...")
    for i in InstrumentVoice.objects.all():
        i.solr_index(commit=False, solrconn=solrconn)
    solrconn.commit()

    print("Indexing languages...")
    for l in Language.objects.all():
        l.solr_index(commit=False, solrconn=solrconn)
    solrconn.commit()

    print("Indexing locations...")
    for l in Location.objects.all():
        l.solr_index(commit=False, solrconn=solrconn)
    solrconn.commit()

    print("Indexing sources...")
    for s in Source.objects.all():
        s.solr_index(commit=False, solrconn=solrconn)
    solrconn.commit()

    print("Indexing tags...")
    for t in Tag.objects.all():
        t.solr_index(commit=False, solrconn=solrconn)
    solrconn.commit()

    print("Indexing pieces...")
    for p in Piece.objects.all():
        p.solr_index(commit=False, solrconn=solrconn)
    solrconn.commit()

    print("Indexing movements...")
    for m in Movement.objects.all():
        m.solr_index(commit=False, solrconn=solrconn)
    solrconn.commit()

    from elvis.elvis.tasks import rebuild_suggester_dicts
    rebuild_suggester_dicts()
