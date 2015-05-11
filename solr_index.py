import os, sys, django
import solr
import uuid
from elvis.settings import SOLR_SERVER

#from django.conf import settings

'''
Used to populate the Solr database; LM: more fields added, according to models
'''


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elvis.settings")

    django.setup()

    from elvis.models.collection import Collection
    from elvis.models.composer import Composer
    from elvis.models.piece import Piece
    from elvis.models.movement import Movement
    from elvis.models.tag import Tag
    from elvis.models.project import Project
    from elvis.models.comment import Comment
    from elvis.models.discussion import Discussion

    print "Using: {0}".format(SOLR_SERVER)
    solrconn = solr.SolrConnection(SOLR_SERVER)
    solrconn.delete_query("*:*")
    solrconn.commit()


    '''
    Collections: title
    comment, creator
    '''
    collections = Collection.objects.all()
    all_collections = []
    print "Adding collections..."
    for collection in collections:
        doc = {
            'type': 'elvis_collection',
            'id': str(uuid.uuid4()),
            'item_id': int(collection.id),
            'title': unicode(collection.title),
            'parent_collection_names': unicode(collection.title),
            'created': collection.created,
            'updated': collection.updated,
            'comment': collection.comment,
            'creator_name': collection.creator.username,
        }
        all_collections.append(doc)
    solrconn.add_many(all_collections)
    solrconn.commit()
    print "Done adding collections."

    '''
    Composers: name, birthday, death date 
    '''
    composers = Composer.objects.all()
    all_composers = []
    print "Adding composers..."
    for composer in composers:
        doc = {
            'type': 'elvis_composer',
            'id': str(uuid.uuid4()),
            'item_id': int(composer.id), 
            'composer_name': composer.name,
            'birth_date': composer.birth_date,
            'death_date': composer.death_date,
            'created': composer.created,
            'updated': composer.updated,
        }
        all_composers.append(doc)
    solrconn.add_many(all_composers)
    solrconn.commit()
    print "Done adding composers."

    '''
    Pieces: title, composer name, collection names, uploader name, comment, num_voices, date of composition,
    tags, attachments,
    numqueries, numdownloads
    '''
    pieces = Piece.objects.all()
    all_pieces = []
    print "Adding pieces..."
    for piece in pieces:

        user = piece.uploader.first_name + " " + piece.uploader.last_name
        username = piece.uploader.username

        tags = []
        for tag in piece.tags.all():
            tags.append(tag.name)

        collections = []
        for collection in piece.collections.all():
            try:
                collections.append(unicode(collection.title))
            except UnicodeDecodeError:
                collections.append(collection.title.decode('utf-8'))

        doc = {
            'type': 'elvis_piece',
            'id': str(uuid.uuid4()),
            'item_id': int(piece.id),
            'title': unicode(piece.title),
            'date_of_composition': piece.date_of_composition,
            'date_of_composition2': piece.date_of_composition2,
            'number_of_voices': piece.number_of_voices,
            'comment': piece.comment,
            'created': piece.created,
            'updated': piece.updated,
            'parent_collection_names': collections,
            'composer_name': piece.composer.name,
            'uploader_name': piece.uploader.username,
            'tags': tags,
        }

        all_pieces.append(doc)

    solrconn.add_many(all_pieces)
    solrconn.commit()
    print "Done adding pieces."

    '''
    Movements: title, piece title, composer name, collection names, date of composition, num voices, uploader_name
    tags, attachments, comment, numqueries, numdownloads
    '''
    movements = Movement.objects.all()
    all_movements = []
    print "Adding movements..."
    for movement in movements:

        user = movement.uploader.first_name + " " + movement.uploader.last_name
        username = movement.uploader.username
        
        if movement.piece is None:
            parent_piece_name = None
        else:
            parent_piece_name = movement.piece.title

        tags = []
        for tag in movement.tags.all():
            tags.append(tag.name)

        collections = []
        for collection in movement.collections.all():
            try:
                collections.append(unicode(collection.title))
            except UnicodeDecodeError:
                collections.append(collection.title.decode('utf-8'))

        doc = {
            'type': 'elvis_movement',
            'id': str(uuid.uuid4()),
            'item_id': int(movement.id),
            'title': unicode(movement.title),
            'date_of_composition': movement.date_of_composition,
            'date_of_composition2': movement.date_of_composition2,
            'number_of_voices': movement.number_of_voices,
            'comment': movement.comment,
            'created': movement.created,
            'updated': movement.updated,
            'parent_piece_name': parent_piece_name,  
            'parent_collection_names': collections,
            'composer_name': movement.composer.name,
            'uploader_name': movement.uploader.username,
            'tags': tags,
        }

        all_movements.append(doc)

    solrconn.add_many(all_movements)
    solrconn.commit()
    print "Done adding movements."

    '''
    Tags: name, description
    numqueries 
    '''
    tags = Tag.objects.all()
    all_tags = []
    print "Adding tags..."
    for tag in tags:
                
        doc = {
            'type': 'elvis_tag',
            'id': str(uuid.uuid4()),
            'item_id': int(tag.id),
            'name': tag.name,
            'tags': tag.name,
            'description': tag.description,
            'approved': tag.approved,
        }

        all_tags.append(doc)

    solrconn.add_many(all_tags)
    solrconn.commit()
    print "Done adding tags."

    '''
    Projects: name, description 
    users, attachments
    '''
    projects = Project.objects.all()
    all_projects = []
    print "Adding projects..."
    for project in projects:

        doc = {
            'type': 'elvis_project',
            'id': str(uuid.uuid4()),
            'item_id': int(project.id),
            'name': project.name,
            'description': project.description,
            'created': project.created,
            'updated': project.updated,
        }

        all_projects.append(doc)

    solrconn.add_many(all_projects)
    solrconn.commit()
    print "Done adding projects."

    '''
    Discussions: name, comment, user
    '''
    discussions = Discussion.objects.all()
    all_discussions = []
    print "Adding discussions..."
    for discussion in discussions:

         doc = {
            'type': 'elvis_discussion',
            'id': str(uuid.uuid4()),
            'item_id': int(discussion.id),
            'name': discussion.name,
            'comment_text': discussion.text,
            'created': discussion.created,
            'updated': discussion.updated,
            'parent_project_name': discussion.project.name,
         }

         all_discussions.append(doc)

    solrconn.add_many(all_discussions)
    solrconn.commit()
    print "Done adding discussions."

    '''
    Comments: text, user
    discussion
    '''
    comments = Comment.objects.all()
    all_comments = []
    print "Adding comments..."
    for comment in comments:

        user = comment.user.first_name + " " + comment.user.last_name
        username = comment.user.username

        doc = {
            'type': 'elvis_comment',
            'id': str(uuid.uuid4()),
            'item_id': int(comment.id),
            'name': comment.name,
            'comment_text': comment.text,
            'created': comment.created,
            'updated': comment.updated,
         }

        all_comments.append(doc)

    solrconn.add_many(all_comments)
    solrconn.commit()
    print "Done adding discussions."

    print "Closing connection." 

    sys.exit()
