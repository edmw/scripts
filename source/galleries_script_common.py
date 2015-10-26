# coding: utf-8

import sys, os, re, term

from galleries.galleries import search_galleries, search_gallery

class GSError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "{0}".format(self.value)

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

