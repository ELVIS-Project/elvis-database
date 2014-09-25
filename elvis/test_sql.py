import os
import datetime, pytz
import MySQLdb
from django.core.files import File
from MySQLdb.cursors import DictCursor

import django

import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elvis.settings")

django.setup()

from elvis.models.tag import Tag
from elvis.models.tag_hierarchy import TagHierarchy
from elvis.models.composer import Composer
from django.contrib.auth.models import User
from elvis.models.collection import Collection
from elvis.models.piece import Piece
from elvis.models.attachment import Attachment
from elvis.models.movement import Movement
from elvis.models.download import Download

DRUPAL_FILE_PATH = "elvis-files"  # path to the old drupal files.

ELVIS_USERS = """SELECT DISTINCT u.uid, u.name, u.mail, u.created, u.access, u.login FROM users u
                LEFT JOIN users_roles ur ON u.uid = ur.uid
                LEFT JOIN role r ON ur.rid = r.rid
                WHERE ur.rid IN (5, 6, 4)"""

COMPOSERS_QUERY = """SELECT td.tid AS old_id, td.name, dt.field_dates_value AS birth_date,
                      dt.field_dates_value2 AS death_date FROM taxonomy_term_data td
                     LEFT JOIN field_data_field_dates dt on td.tid = dt.entity_id
                     WHERE td.vid = 3"""

PIECE_MOVEMENT_QUERY = """SELECT rv.title, cp.field_composer_tid AS composer_id, rv.nid AS old_id,
                 rv.uid AS uploader, fd.field_date_value AS date_of_composition, fd.field_date_value2 AS date_of_composition2,
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

TAG_DICT = {"Composer": "pass", 
            "Source Information": "Source", 
            "Instruments / Voices": "InstrumentVoice", 
            "Country / City of Composer": "Location", 
            "Free": "pass", 
            "Language": "Language", 
            "Provenance": "Source",
            }

TAG_CSV_PATH = 'old_tags.csv'

FIELD_INSTRUCTIONS = ()



# There may be even more problems dumping the database on different oses... this attempts to decode in utf-8 and then latin-1
def my_decoder(text):
        if not text is None:
            try:
                text = unicode(text)
            except UnicodeDecodeError:
                try:
                    text = text.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        text = text.decode('latin-1')
                    except UnicodeDecodeError:
                        print "decode error..."
            return text
        else:
            return None
     

class DumpDrupal(object):

    def __init__(self):
        # IMPORTANT: Choose which objects to add here
        # LM: Would want to run tags, users only if db doesnt have previous users, corpus, piece, movement, in that order

        self.get_tags()
        self.get_composers()
        self.get_users()
        self.get_collection()
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

    def __write_tags_to_csv(self, tags):
        with open(TAG_CSV_PATH, 'wb') as csv_file:
            csv_writer = csv.writer(csv_file, dialect='excel')
            csv_writer.writerow(['Old Tag', 'Tag Description', 'New Parent Field', 'New Name'])
            for tag in tags:
                csv_writer.writerow([(tag['name']), (tag['description']), '', ''])
        with open(TAG_CSV_PATH, 'rb') as csv_file:
            csv_reader = csv.reader(csv_file, dialect='excel')
            # Check that you're done
            for row in csv_reader:
                print row

    def __read_tags_in_csv(self,tags):
        pass
        with open(TAG_CSV_PATH, 'rb') as csv_file:
            csv_reader = csv.reader(csv_file, dialect='excel')
            # Check that you're done
            for row in csv_reader:
                print row


    def get_collection(self):
        users = self.__get_ddmal_users()
        self.__connect()

        self.curs.execute(CORPUS_QUERY)
        collection = self.curs.fetchall()


        print "====== Testing collections ======"
        print("number", len(collection))
        for coll in collection:
            for user in users:
                if coll.get('creator') == user.get('uid'):
                    u = User.objects.get(username=user.get('name'))
                    break
            coll['creator'] = u
            coll['title'] = my_decoder(coll['title'])
            coll['comment'] = my_decoder(coll['comment'])
            coll['created'] = datetime.datetime.fromtimestamp(coll['created'])
            coll['updated'] = datetime.datetime.fromtimestamp(coll['updated'])

        self.__disconnect()

    def get_users(self):
        conn = MySQLdb.connect(host="localhost", user="root", cursorclass=DictCursor, db="ddmal_drupal")
        curs = conn.cursor()

        curs.execute(ELVIS_USERS)
        users = curs.fetchall()

        print "====== Testing Users ======"
        print ("number", len(users))
        for user in users:
            u = {
                'is_active': True,
                'username': my_decoder(user.get('name')),
                'last_login': datetime.datetime.fromtimestamp(user.get('login')),
                'date_joined': datetime.datetime.fromtimestamp(user.get('created')),
                'email': user.get('mail')
            }

        curs.close()
        conn.close()

    def get_composers(self):
        self.__connect()
        self.curs.execute(COMPOSERS_QUERY)
        composers = self.curs.fetchall()


        print "====== Testing composers ======"
        print ("number", len(composers))
        self.__disconnect()

    def get_tags(self):
        self.__connect()
        self.curs.execute(TAG_QUERY)
        tags = self.curs.fetchall()

        print "====== Testing tags ======"
        print ("number", len(tags))
        for tag in tags:
            t = Tag(**tag)
            t.name = my_decoder(t.name)
            t.description = my_decoder(t.description)

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

        self.__disconnect()

    def get_attachments(self):
        self.curs.execute(ATTACHMENT_QUERY)

    def get_pieces_movements(self, rettype):
        users = self.__get_ddmal_users()
        
        query = PIECE_MOVEMENT_QUERY.format(rettype)
        self.__connect()
        self.curs.execute(query)

        objects = self.curs.fetchall()

        print("====== Testing " + rettype + " ======")
        print("number", len(objects))
        print "Adding {0}".format(rettype)
        for item in objects:
            # LM: composer may be none
            try:
                composer_obj = Composer.objects.get(old_id=item['composer_id'])
            except Composer.DoesNotExist:
                composer_obj = None

            for user in users:
                if item.get('uploader') == user.get('uid'):
                    user_obj = User.objects.get(username=user.get('name'))
                    break

            if rettype == "piece":
                collection_objs = Collection.objects.filter(old_id=item['book_id'])
                if not collection_objs.exists():
                    collection_objs = None
                else:
                    collection_objs = collection_objs
            elif rettype == "movement":
                parent_obj = self.__resolve_movement_parent(item['old_id'])
                collection_objs = Collection.objects.filter(old_id=item['book_id'])
                if not collection_objs.exists():
                    collection_objs = None
                else:
                    collection_objs = collection_objs

            p = {
                'uploader': user_obj,
                'composer': composer_obj,
                'old_id': item.get('old_id', None),
                'title': my_decoder(item.get('title', None)),
                'date_of_composition': pytz.utc.localize(item.get('date_of_composition', None)),
                'date_of_composition2': pytz.utc.localize(item.get('date_of_composition2', None)),  
                'number_of_voices': item.get('number_of_voices', None),
                'comment': my_decoder(item.get('comment', None)),
                'created': datetime.datetime.fromtimestamp(item.get('created')),
                'updated': datetime.datetime.fromtimestamp(item.get('updated'))
            }

        self.__disconnect()
        
        print "====== Testing Tags for {0} =======".format(rettype)
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
            self.curs.execute(ITEM_TAG_QUERY, [item.old_id])
            tags = self.curs.fetchall()
            for tag in tags:
                tag_obj = Tag.objects.filter(old_id=tag.get('tid'))
                if not tag_obj.exists():
                    continue
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

        

        print("Attaching for real - LM")

        self.__connect()
        failures = 0
        tries_with_0s = 0
        for item in objects:
            self.curs.execute(ITEM_ATTACHMENT_QUERY, [item.old_id])
            attachments = self.curs.fetchall()
            for attachment in attachments:
                for user in users:
                    if attachment.get('uploader') == user.get('uid'):
                        user_obj = User.objects.get(username=user.get('name'))
                        break

                # LM filename from old attachment objects
                filename = attachment.get('filename')  
                #filename = "test_file.mei"  # for testing.
                
                # LM Catch IO Error when trying to find file
                try:
                    filepath = os.path.join(DRUPAL_FILE_PATH, filename)
                    f = open(filepath, 'rb')
                except IOError:
                    # print('Failed to open: ' + filename)
                    # Some files have _0 appended to name before extension.... try that
                    try:
                        filename_temp, extension_temp = os.path.splitext(filename)
                        filename = filename_temp + '_0' + extension_temp
                        filepath = os.path.join(DRUPAL_FILE_PATH, filename)
                        f = open(filepath)
                        print('Trying to attach ' + filename)
                        tries_with_0s = tries_with_0s + 1
                    # If that doesn't work then pass
                    except IOError:
                        print('Failure: ' + filename)
                        failures = failures + 1
                        continue     

                date_created = pytz.utc.localize(datetime.datetime.fromtimestamp(attachment.get('created')))

                s = {
                    'uploader': user_obj,
                    'description': attachment.get('description', None),
                    'created': date_created,
                    'old_id': attachment.get('old_id', None)
                }

        self.__disconnect()
        print('tries with 0s', tries_with_0s)
        print('failed attachments', failures)
        
    def __resolve_movement_parent(self, old_id):
        q = """SELECT REPLACE(ml1.link_path, 'node/', '') AS parent_nid,
               REPLACE(ml2.link_path, 'node/', '') AS nid
               FROM menu_links ml1
               LEFT JOIN menu_links ml2 ON ml2.plid = ml1.mlid
               WHERE ml2.link_path = \"node/%s\""""
        self.curs.execute(q, [old_id])
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
