from elvis.models.piece import Piece
from elvis.models.movement import Movement
from elvis.models.tag import Tag
from elvis.models.composer import Composer
from elvis.models.genre import Genre
from elvis.models.instrumentation import InstrumentVoice
from elvis.models.language import Language
from elvis.models.source import Source
from elvis.views import abstract_model_factory
import csv
import pdb


def migrate_tags(csv_file):
    missing_tags = []

    with open(csv_file, 'rU') as open_file:
        reader = csv.DictReader(open_file)
        for row in reader:
            t = Tag.objects.filter(name=row['tag'])
            if not t:
                print("Tag " + row['tag'] + " not found.")
                missing_tags.append(row['tag'])
                continue
            # Some modificatins are '2 tags' or similar. These need to be done by hand, so are just skipped in the function.
            if 'tags' in row['mod']:
                continue
            print("Handling tag " + row['tag'] + " on pieces")
            handle_pieces(row)
            print("Handling tag " + row['tag'] + " on movements")
            handle_movements(row)

    with open("missing_tags.txt", "w+") as output:
        for item in missing_tags:
            output.write(item + "\n")


def handle_pieces(csv_row):
    tag_query = Tag.objects.filter(name=csv_row['tag'])
    if not tag_query:
        raise Exception("No tag named " + csv_row['tag'])
    for tag_object in tag_query:
        for piece in tag_object.pieces.all():
            handle_tag(csv_row, tag_object, piece)


def handle_movements(csv_row):
    tag_query = Tag.objects.filter(name=csv_row['tag'])
    if not tag_query:
        raise Exception("No tag named " + csv_row['tag'])
    for tag_object in tag_query:
        for movement in tag_object.movements.all():
            handle_tag(csv_row, tag_object, movement)


def handle_tag(csv_row, tag_object, model):

    if csv_row['field'] == "Composer":
        if csv_row['mod']:
            composer = Composer.objects.filter(name=csv_row['tag'])
            if composer:
                composer[0].name = csv_row['mod']
                composer.save()

        if not model.composer:
            if csv_row['mod']:
                composer = abstract_model_factory(csv_row['mod'], "Composer")[0]
            else:
                composer = abstract_model_factory(csv_row['tag'], "Composer")[0]
            model.composer.add(composer)
        model.tags.remove(tag_object)
        model.save()

    if csv_row['field'] == "Country / City of Composer":
        if csv_row['mod']:
            location = abstract_model_factory(csv_row['mod'], "Location")[0]
        else:
            location = abstract_model_factory(csv_row['tag'], "Location")[0]
        model.locations.add(location)
        model.tags.remove(tag_object)
        model.save()

    if csv_row['field'] == "Free":
        if csv_row['mod']:
            tag = Tag.objects.filter(name=csv_row['tag'])
            if tag:
                tag[0].name = csv_row['mod']
                tag[0].save()
        else:
            return

    if csv_row['field'] == "Genre / Sub-genre":
        if csv_row['mod']:
            genre = Genre.objects.filter(name=csv_row['tag'])
            if genre:
                genre[0].name = csv_row['mod']
                genre[0].save()
            else:
                genre = abstract_model_factory(csv_row['mod'], "Genre")[0]
        else:
            genre = abstract_model_factory(csv_row['tag'], "Genre")[0]
        model.genres.add(genre)
        model.tags.remove(tag_object)
        model.save()

    if csv_row['field'] == "Instruments / Voices":
        if csv_row['mod']:
            instrument = InstrumentVoice.objects.filter(name=csv_row['tag'])
            if instrument:
                instrument[0].name = csv_row['mod']
                instrument[0].save()
            else:
                instrument = abstract_model_factory(csv_row['mod'], "InstrumentVoice")[0]
        else:
            instrument = abstract_model_factory(csv_row['tag'], "InstrumentVoice")[0]
        model.instruments_voices.add(instrument)
        model.tags.remove(tag_object)
        model.save()

    if csv_row['field'] == "Language":
        if csv_row['mod']:
            language = Language.objects.filter(name=csv_row['tag'])
            if language:
                language[0].name = csv_row['mod']
                language[0].save()
            else:
                language = abstract_model_factory(csv_row['mod'], "Language")[0]
        else:
            language = abstract_model_factory(csv_row['tag'], "Language")[0]
        model.languages.add(language)
        model.tags.remove(tag_object)
        model.save()

    if csv_row['field'] == "Provenance":
        if csv_row['mod']:
            source = Source.objects.filter(name=csv_row['tag'])
            if source:
                source[0].name = csv_row['mod']
                source[0].save()
            else:
                source = abstract_model_factory(csv_row['mod'], "Source")[0]
        else:
            source = abstract_model_factory(csv_row['tag'], "Source")[0]
        model.sources.add(source)
        model.tags.remove(tag_object)
        model.save()

    if csv_row['field'] == "Sacred/secular/ambiguous":
        model.religiosity = csv_row['tag'].title()
        model.tags.remove(tag_object)
        model.save()

    if csv_row['field'] == "x":
        model.tags.remove(tag_object)
        model.save()


def delete_unused_tags():
    for tag in Tag.objects.all():
        if not tag.pieces.all() and not tag.movements.all():
            tag.delete()