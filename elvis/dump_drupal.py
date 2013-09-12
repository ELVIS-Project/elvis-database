import os
import datetime
import MySQLdb
from django.core.files import File
from MySQLdb.cursors import DictCursor

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elvis.settings")
from elvis.models.tag import Tag
from elvis.models.tag_hierarchy import TagHierarchy
from elvis.models.composer import Composer
from django.contrib.auth.models import User
from elvis.models.corpus import Corpus
from elvis.models.piece import Piece
from elvis.models.attachment import Attachment
from elvis.models.movement import Movement

DRUPAL_FILE_PATH = ""  # path to the old drupal files.

ELVIS_USERS = """SELECT DISTINCT u.uid, u.name, u.mail, u.created, u.access, u.login FROM users u
                LEFT JOIN users_roles ur ON u.uid = ur.uid
                LEFT JOIN role r ON ur.rid = r.rid
                WHERE ur.rid IN (5, 6, 4)"""

COMPOSERS_QUERY = """SELECT td.tid AS old_id, td.name, dt.field_dates_value AS birth_date,
                      dt.field_dates_value2 AS death_date FROM taxonomy_term_data td
                     LEFT JOIN field_data_field_dates dt on td.tid = dt.entity_id
                     WHERE td.vid = 3"""

PIECE_MOVEMENT_QUERY = """SELECT rv.title, cp.field_composer_tid AS composer_id, rv.nid AS old_id,
                 rv.uid AS uploader, fd.field_date_value AS date_of_composition,
                 fv.field_voices_value AS number_of_voices, fc.field_comment_value AS comment,
                 n.created AS created, n.changed AS updated, b.bid AS book_id FROM node n
                  LEFT JOIN node_revision rv ON (n.vid = rv.vid)
                  LEFT JOIN field_data_field_composer cp ON (rv.vid = cp.revision_id)
                  LEFT JOIN field_data_field_date fd ON (fd.revision_id = rv.vid)
                  LEFT JOIN field_data_field_voices fv ON (fv.revision_id = rv.vid)
                  LEFT JOIN field_data_field_comment fc ON (fc.revision_id = rv.vid)
                  LEFT JOIN book b ON (n.nid = b.nid)
                  WHERE n.type=\"{0}\""""

CORPUS_QUERY = """SELECT rv.title, rv.nid AS old_id, rv.uid AS creator, cc.field_corpus_comment_value AS comment,
                  n.created AS created, n.changed AS updated FROM node n
                  LEFT JOIN node_revision rv ON (n.vid = rv.vid)
                  LEFT JOIN field_revision_field_corpus_comment cc ON (cc.revision_id = n.vid)
                  WHERE n.type=\"corpus\""""

TAG_QUERY = """SELECT td.name, td.description, td.tid AS old_id FROM taxonomy_term_data td"""

TAG_HIERARCHY_QUERY = """SELECT * FROM taxonomy_term_hierarchy"""

ATTACHMENT_QUERY = """"""


class DumpDrupal(object):
    def __init__(self):
        self.get_tags()
        self.get_composers()
        self.get_users()
        self.get_corpus()
        self.get_pieces_movements("piece")
        self.get_pieces_movements("movement")

    def __connect(self):
        self.conn = MySQLdb.connect(host="localhost", user="root", cursorclass=DictCursor, db="ddmal_elvis")
        self.curs = self.conn.cursor()

    def __disconnect(self):
        self.curs.close()
        self.conn.close()

    def __get_ddmal_users(self):
        conn = MySQLdb.connect(host="localhost", user="root", cursorclass=DictCursor, db="ddmal_drupal")
        curs = conn.cursor()

        curs.execute(ELVIS_USERS)
        u = curs.fetchall()
        curs.close()
        conn.close()
        return u

    def get_corpus(self):
        users = self.__get_ddmal_users()
        self.__connect()

        self.curs.execute(CORPUS_QUERY)
        corpus = self.curs.fetchall()
        print "Deleting corpora"
        Corpus.objects.all().delete()

        print "Adding corpora"
        for corp in corpus:
            for user in users:
                if corp.get('creator') == user.get('uid'):
                    u = User.objects.get(username=user.get('name'))
                    break
            corp['creator'] = u

            corp['created'] = datetime.datetime.fromtimestamp(corp['created'])
            corp['updated'] = datetime.datetime.fromtimestamp(corp['updated'])
            x = Corpus(**corp)
            x.save()

        self.__disconnect()

    def get_users(self):
        conn = MySQLdb.connect(host="localhost", user="root", cursorclass=DictCursor, db="ddmal_drupal")
        curs = conn.cursor()

        curs.execute(ELVIS_USERS)
        users = curs.fetchall()
        for user in users:
            print "Creating {0}".format(user.get('name'))
            u = {
                'is_active': True,
                'username': user.get('name'),
                'last_login': datetime.datetime.fromtimestamp(user.get('login')),
                'date_joined': datetime.datetime.fromtimestamp(user.get('created')),
                'email': user.get('mail')
            }
            x = User(**u)
            x.save()

        curs.close()
        conn.close()

    def get_composers(self):
        self.__connect()
        self.curs.execute(COMPOSERS_QUERY)
        composers = self.curs.fetchall()

        print "Deleting composer objects"
        Composer.objects.all().delete()

        print "Adding composers"
        for composer in composers:
            c = Composer(**composer)
            c.save()
        self.__disconnect()

    def get_tags(self):
        self.__connect()
        self.curs.execute(TAG_QUERY)
        tags = self.curs.fetchall()

        print "Deleting all tags"
        Tag.objects.all().delete()

        print "Adding tags"
        for tag in tags:
            t = Tag(**tag)
            t.save()

        print "Deleting tag hierarchy"
        TagHierarchy.objects.all().delete()

        print "Adding tag hierarchy"
        self.curs.execute(TAG_HIERARCHY_QUERY)
        tag_hierarchy = self.curs.fetchall()
        for t in tag_hierarchy:
            tag = Tag.objects.get(old_id=t.get('tid', None))
            if not t.get('parent') == 0:
                parent = Tag.objects.get(old_id=t.get('parent', None))
            else:
                parent = None
            t = TagHierarchy(tag=tag, parent=parent)
            t.save()

        self.__disconnect()

    def get_attachments(self):
        self.curs.execute(ATTACHMENT_QUERY)

    def get_pieces_movements(self, rettype):
        users = self.__get_ddmal_users()
        query = PIECE_MOVEMENT_QUERY.format(rettype)
        self.__connect()
        self.curs.execute(query)

        objects = self.curs.fetchall()

        print "Deleting {0}".format(rettype)
        if rettype == "piece":
            Piece.objects.all().delete()
        elif rettype == "movement":
            Movement.objects.all().delete()

        print "Adding {0}".format(rettype)
        for item in objects:
            composer_obj = Composer.objects.get(old_id=item['composer_id'])
            for user in users:
                if item.get('uploader') == user.get('uid'):
                    user_obj = User.objects.get(username=user.get('name'))
                    break

            if rettype == "piece":
                parent_obj = Corpus.objects.filter(old_id=item['book_id'])
                if not parent_obj.exists():
                    parent_obj = None
                else:
                    parent_obj = parent_obj[0]
            elif rettype == "movement":
                parent_obj = self.__resolve_movement_parent(item['old_id'])
                corpus_obj = Corpus.objects.filter(old_id=item['book_id'])
                if not corpus_obj.exists():
                    corpus_obj = None
                else:
                    corpus_obj = corpus_obj[0]

            p = {
                'uploader': user_obj,
                'composer': composer_obj,
                'old_id': item.get('old_id', None),
                'title': item.get('title', None),
                'date_of_composition': item.get('date_of_composition', None),
                'number_of_voices': item.get('number_of_voices', None),
                'comment': item.get('comment', None),
                'created': datetime.datetime.fromtimestamp(item.get('created')),
                'updated': datetime.datetime.fromtimestamp(item.get('updated'))
            }

            if rettype == "piece":
                p.update({'corpus': parent_obj})
                x = Piece(**p)
            elif rettype == "movement":
                p.update({'piece': parent_obj, 'corpus': corpus_obj})
                x = Movement(**p)
            x.save()
        self.__disconnect()

        print "Tagging {0}".format(rettype)
        # filters out composers (tid 3)
        ITEM_TAG_QUERY = """SELECT ti.nid, ti.tid FROM taxonomy_index ti
                             LEFT JOIN taxonomy_term_data td ON td.tid = ti.tid
                             WHERE ti.nid = %s"""

        if rettype == "piece":
            objects = Piece.objects.all()
        elif rettype == "movement":
            objects = Movement.objects.all()

        for item in objects:
            self.__connect()
            self.curs.execute(ITEM_TAG_QUERY, item.old_id)
            tags = self.curs.fetchall()
            for tag in tags:
                tag_obj = Tag.objects.filter(old_id=tag.get('tid'))
                if not tag_obj.exists():
                    continue
                item.tags.add(tag_obj[0])
                item.save()

            self.__disconnect()

        ITEM_ATTACHMENT_QUERY = """SELECT ff.field_files_description AS description, fm.timestamp AS created,
                                    fm.uid AS uploader, fm.filename AS filename, fm.uri AS uri FROM field_data_field_files ff
                                    LEFT JOIN file_managed fm ON ff.field_files_fid = fm.fid
                                    WHERE ff.entity_id = %s"""

        print "Attaching files to {0}".format(rettype)
        if rettype == "piece":
            objects = Piece.objects.all()
        elif rettype == "movement":
            objects = Movement.objects.all()

        print "Deleting attachments"
        Attachment.objects.all().delete()

        self.__connect()
        for item in objects:
            self.curs.execute(ITEM_ATTACHMENT_QUERY, item.old_id)
            attachments = self.curs.fetchall()
            for attachment in attachments:
                for user in users:
                    if attachment.get('uploader') == user.get('uid'):
                        user_obj = User.objects.get(username=user.get('name'))
                        break

                a = Attachment()
                a.save()  # ensure we've got a PK before we try and attach a file.

                # filename = attachment.get('filename')[9:]  # lop the 'public://' off.
                filename = "test_file.mei"  # for testing.

                filepath = os.path.join(DRUPAL_FILE_PATH, filename)
                f = open(filepath, 'rb')

                # attached_file = os.path.join(a.attachment_path, filename)
                s = {
                    'uploader': user_obj,
                    'description': attachment.get('description', None),
                    'created': datetime.datetime.fromtimestamp(attachment.get('created')),
                    'old_id': attachment.get('old_id', None)
                }
                a.__dict__.update(**s)
                a.save()

                a.attachment.save(filename, File(f))
                a.save()
                f.close()
                item.attachments.add(a)

        self.__disconnect()

    def __resolve_movement_parent(self, old_id):
        q = """SELECT REPLACE(ml1.link_path, 'node/', '') AS parent_nid,
               REPLACE(ml2.link_path, 'node/', '') AS nid
               FROM menu_links ml1
               LEFT JOIN menu_links ml2 ON ml2.plid = ml1.mlid
               WHERE ml2.link_path = \"node/%s\""""
        self.curs.execute(q, old_id)
        pp = self.curs.fetchone()
        # import pdb
        # pdb.set_trace()
        if not pp:
            return None
        parent_obj = Piece.objects.filter(old_id=pp['parent_nid'])
        if parent_obj.exists():
            return parent_obj[0]
        else:
            return None

if __name__ == "__main__":
    x = DumpDrupal()
