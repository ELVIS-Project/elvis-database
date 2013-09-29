#!/usr/bin/env python
import os
import sys
import solr
import uuid

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elvis.settings")
    from elvis.models.composer import Composer

    print "Emptying Solr"
    solrconn = solr.SolrConnection("http://localhost:8080/elvis-solr")
    solrconn.delete_query("*:*")
    solrconn.commit()

    print "Adding composers"
    composers = Composer.objects.all()
    all_composers = []
    for composer in composers:
        d = {
            'type': 'composer',
            'id': str(uuid.uuid4()),
            'composer_name': composer.name,
            'composer_birth': composer.birth_date,
            'composer_death': composer.death_date
        }
        all_composers.append(d)
    solrconn.add_many(all_composers)
    solrconn.commit()
    print "Done adding composers"


    print "Done!"
    sys.exit()
