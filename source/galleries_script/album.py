# coding: utf-8

import sys, os, re, shutil, term

from galleries_script import get_gallery, get_album_in_gallery

def setcover(args):
    gallery = get_gallery(args.fspath, args.gallery_name)
    album = get_album_in_gallery(gallery, args.album_name)

    term.banner("SET ALBUM COVER")

    image_filename = os.path.join(gallery.path, 't', "{0}.jpg".format(args.image_name))
    if not os.path.exists(image_filename) or not os.path.isfile(image_filename):
        term.banner("IMAGE '{0}' NOT FOUND IN GALLERY '{1}'\nAT '{2}'".format(
                args.image_name, gallery.name, image_filename),
            type='ERROR')
        return

    shutil.copyfile(image_filename, os.path.join(gallery.path, "{0}.jpg".format(album.label)))

    term.banner("DONE", type='INFO')

