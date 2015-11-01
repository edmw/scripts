# coding: utf-8

import sys, os, os.path, re, logging, gettext

import pycountry

from galleries.albums import search_albums
from galleries.access import Access, read_access

class Gallery:
    def __init__(self, path, name,
        label=None,
        year=None,
        month=None,
        day=None,
        countries=None,
        albums=None,
        access=None
    ):
        self.path = path
        self.name = name
        self.label = label
        self.year = year
        self.month = month
        self.day = day
        self.countries = countries
        self.albums = albums
        self.access = access

    def __str__(self):
        return " ".join([
            "".join([self.year, self.month, self.day]),
            "".join(self.countries),
            self.label
        ]).strip()

    def date_str(self):
        return "{0}.{1}.{2}".format(self.day, self.month, self.year)

    def countries_str(self):
        c = []
        for alpha2 in self.countries:
            country = pycountry.countries.get(alpha2=alpha2)
            if country:
                c.append(_(country.name))
        return ' '.join(c)

    def get_album(self, label):
        for album in self.albums:
            if label == album.label:
                return album
        return None

    def access_init(self, authname, authuserfile):
        self.access = Access(authname=authname, authuserfile=authuserfile)

    def access_write(self):
        if self.access:
            self.access.write(self.path)

    def factory(path, name, load_access=False, load_albums=False):
        path = os.path.join(path, name)
        if not os.path.isdir(path):
            return None

        g = {}
        g['albums'] = None
        g['access'] = None

        # parse name
        m = GALLERY_NAME_PATTERN.match(name)
        if not m:
            return None
        g['year'] = m.group(1)
        g['month'] = m.group(2)
        g['day'] = m.group(3)
        # parse name: split country codes into iso codes of two characters
        t = m.group(4)
        g['countries'] = [t[x:x+2] for x in range(0, len(t), 2)]
        # parse name: gallery label
        t = m.group(6) or ""
        g['label'] = " ".join(word.title() for word in t.split("_"))

        # search albums
        g['albums'] = search_albums(path, load=load_albums)

        # read access
        if load_access:
            try:
                g['access'] = read_access(path)
            except ValueError as x:
                logging.warning("{0}".format(x))

        return Gallery(path, name, **g)
      
    factory = staticmethod(factory)

GALLERY_NAME_PATTERN = re.compile('^(\d\d\d\d)(\d\d)(\d\d)_([A-Z]+)(_(.*)){0,1}$')

def search_galleries(path, load_access=False, load_albums=False, progress=None):
    """ Search galleries at the given path.

        A gallery is a directory with its name matching the gallery name pattern.
    """
    galleries = []

    if not os.path.exists(path) or not os.path.isdir(path):
        raise FileNotFoundError(path)

    names = [name for name in os.listdir(path)
        if os.path.isdir(os.path.join(path, name))
            and GALLERY_NAME_PATTERN.match(name)
    ]
    non = len(names)
    ion = 0
    for name in reversed(sorted(names)):
        gallery = Gallery.factory(path, name,
            load_access=load_access, load_albums=load_albums
        )
        if gallery:
            galleries.append(gallery)
        if progress:
            progress(ion, non)
        ion = ion + 1

    return galleries

def search_gallery(path, name, load_access=False):
    """ Search gallery with the given name at the given path.
    """
    return Gallery.factory(path, name, load_access=load_access)

