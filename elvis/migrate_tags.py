from elvis.models.piece import Piece
from elvis.models.movement import Movement
from elvis.models.tag import Tag
from elvis.models.genre import Genre
from elvis.views import abstract_model_factory
import pdb
import csv


def migrate_tags(csv_file):
    #First check all tag names exist in DB
    with open(csv_file, 'r') as open_file:
        reader = csv.DictReader(open_file)
        for row in reader:
            t = Tag.objects.get(name=row['tag'])
    with open(csv_file, 'r') as open_file:
        pdb.set_trace()
        reader = csv.DictReader(open_file)
        for row in reader:
            handle_pieces(row)


def handle_pieces(csv_row):
    tag_query = Tag.objects.filter(name=csv_row['tag'])
    if not tag_query:
        raise Exception("No tag named " + csv_row['tag'])
    for tag_object in tag_query:
        for piece in tag_object.pieces.all():
            handle_tag(csv_row, tag_object, piece)


def handle_movements(csv_row):
    pass


def handle_tag(csv_row, tag_object, model):
    print("Handling " + model.title + " and tag " + csv_row['tag'])
    if csv_row['field'] == "Country / City of Composer":
        location = abstract_model_factory(csv_row['tag'], "Location")[0]
        model.locations.add(location)
        model.tags.remove(tag_object)
        model.save()

