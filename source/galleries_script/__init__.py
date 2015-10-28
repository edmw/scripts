# coding: utf-8

import sys, os, re, term

from galleries.galleries import search_galleries, search_gallery

SYMBOL_CHECKED = '✔'
SYMBOL_SEPARATOR = ' │ '
SYMBOL_SEPARATOR_CLEAR = '   '

NAME_LENGTH = 40

class GSError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "{0}".format(self.value)

class GSAbortError(GSError):
    def __str__(self):
        return "ABORTED: {0}".format(self.value)

def load_gallery(path, load_access=False):
    if os.path.exists(path) and os.path.isdir(path):
        fspath, gallery_name = os.path.split(os.path.normpath(path))
        gallery = search_gallery(fspath, gallery_name, load_access=load_access)
        if not gallery:
            raise GSError("GALLERY '{0}' NOT FOUND AT '{1}'".format(gallery_name, fspath))
        return gallery
    raise GSError("NO GALLERY FOUND AT '{0}'".format(path))

def get_gallery(fspath, gallery_name, load_access=False):
    gallery = search_gallery(fspath, gallery_name, load_access=load_access)
    if not gallery:
        raise GSError("GALLERY '{0}' NOT FOUND AT '{1}'".format(gallery_name, fspath))
    return gallery

def get_album_in_gallery(gallery, album_name):
    album = gallery.get_album(album_name)
    if not album:
        raise GSError("ALBUM '{0}' NOT FOUND IN GALLERY '{1}'".format(album_name, gallery.name))
    return album

def collect_users(galleries):
    """ Collect list of all users in all galleries.
    # coding: utf-8"""
    u = set()
    for gallery in galleries:
        access = gallery.access
        if access:
            u = u | set(access.users)
    return u

def collect_galleries_for_user(galleries, user):
    """ Collect list of galleries for given user.
    """
    g = []
    for gallery in galleries:
        if gallery.access and user in gallery.access.users:
            g.append(gallery)
    return g

def print_gallery_name(name, transform=term.p):
    if len(name) > NAME_LENGTH:
        name = "{0}...".format(name[0:NAME_LENGTH - 3])
    else:
        name = name + ' ' * (NAME_LENGTH - len(name))
    name = name if not transform else transform(name)
    print("{0}".format(name), end='')

