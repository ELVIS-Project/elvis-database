import re
import unicodedata
from django.conf import settings


def normalize_name(name):
    """Remove and replace illegal chars in file names"""
    new_name = re.sub(r"((,| |/) *)", '-', name)
    new_name = unicodedata.normalize('NFKD', new_name).encode('ascii', 'ignore')
    return new_name.decode('utf-8')


def split_ext(name):
    """Split name into (name, ext) tuple if possible.

    If the extension is not recognized or found, will return a tuple
    where the second element is an empty string.
    """
    name_split = name.split(".")
    if "." + name_split[-1] in settings.ELVIS_EXTENSIONS:
        ext = "." + name_split[-1]
        return ".".join(name_split[:-1]), ext
    else:
        ext = ""
        return ".".join(name_split), ""