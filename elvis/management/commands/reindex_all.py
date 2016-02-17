import solr

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

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


class Command(BaseCommand):
    """
    A management command to reindex all of the database content into Solr.
    """
    def handle(self, *args, **options):
        reindex_all()
        print("Successfully reindexed everything.")


def reindex_all():
    """ Re-index script
    Nukes the solr database and re-indexes everything. Someday I'm sure
    this will be useful again.
    """
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

    from elvis.tasks import rebuild_suggester_dicts
    rebuild_suggester_dicts()