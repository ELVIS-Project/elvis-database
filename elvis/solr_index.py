import os, sys
import solr
import uuid

#from django.conf import settings

'''
Used to populate the Solr database
'''


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elvis.settings")

    from elvis.models.corpus import Corpus
    from elvis.models.composer import Composer
    from elvis.models.piece import Piece
    from elvis.models.movement import Movement
    from elvis.models.tag import Tag
    from elvis.models.project import Project
    from elvis.models.comment import Comment
    from elvis.models.discussion import Discussion

    SOLR_SERVER = "http://localhost:8983/solr"
    print "Using: {0}".format(SOLR_SERVER)
    solrconn = solr.SolrConnection(SOLR_SERVER)
    solrconn.delete_query("*:*")
    solrconn.commit()


    '''
    Corpora: title
    comment, creator
    '''
    corpora = Corpus.objects.all()
    all_corpora = []
    print "Adding corpora..."
    for corpus in corpora:
        doc = {
            'type': 'elvis_corpus',
            'id': str(uuid.uuid4()),
            'corpus_id': int(corpus.id),
            'corpus_name': corpus.title,
        }
        all_corpora.append(doc)
    solrconn.add_many(all_corpora)
    solrconn.commit()
    print "Done adding corpora."

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
            'composer_id': int(composer.id),
            'composer_name': composer.name,
            'composer_birth': composer.birth_date,
            'composer_death': composer.death_date
        }
        all_composers.append(doc)
    solrconn.add_many(all_composers)
    solrconn.commit()
    print "Done adding composers."

    '''
    Pieces: title, composer name, corpus name, uploader name, comment, num_voices, date of composition,
    tags, attachments,
    numqueries, numdownloads
    '''
    pieces = Piece.objects.all()
    all_pieces = []
    print "Adding pieces..."
    for piece in pieces:

        user = piece.uploader.first_name + " " + piece.uploader.last_name
        username = piece.uploader.username
        corpus = piece.corpus.title if piece.corpus else ""
                
        doc = {
            'type': 'elvis_piece',
            'id': str(uuid.uuid4()),
            'piece_id': int(piece.id),
            'piece_title': piece.title,
            'composer_name': piece.composer.name,
            'corpus_name': corpus,
            'user': user,
            'username': username,
            'num_voices': piece.number_of_voices,
            'date_of_composition': piece.date_of_composition
        }

        all_pieces.append(doc)

    solrconn.add_many(all_pieces)
    solrconn.commit()
    print "Done adding pieces."

    '''
    Movements: title, piece title, composer name, corpus name, date of composition, num voices, uploader_name
    tags, attachments, comment, numqueries, numdownloads
    '''
    movements = Movement.objects.all()
    all_movements = []
    print "Adding movements..."
    for movement in movements:

        user = movement.uploader.first_name + " " + movement.uploader.last_name
        username = movement.uploader.username
        corpus = movement.corpus.title if movement.corpus else ""
                
        doc = {
            'type': 'elvis_movement',
            'id': str(uuid.uuid4()),
            'movement_id': int(movement.id),
            'movement_title': movement.title,
            'piece_title': movement.piece,
            'composer_name': movement.composer.name,
            'corpus_name': corpus,
            'num_voices': movement.number_of_voices,
            'date_of_composition': movement.date_of_composition,
            'user':user,
            'username':username
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
            'tag_id': int(tag.id),
            'tag_title': tag.name,
            'tag_description': tag.description
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
            'project_id': int(project.id),
            'project_name': project.name,
            'project_description': project.description
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
            'discussion_id': int(discussion.id),
            'discussion_name': discussion.name,
            'discussion_comment': discussion.comment,
            'user': discussion.user.name
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
            'comment_id': int(comment.id),
            'comment_text': comment.text,
            'user': comment.user.name
         }

        all_comments.append(doc)

    solrconn.add_many(all_comments)
    solrconn.commit()
    print "Done adding discussions."

    print "Closing connection." 

    sys.exit()