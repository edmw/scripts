#!python
# coding: utf-8
#
# Dependencies:
# pip install beautifulsoup4
# pip install html5lib
# pip install wheezy.template
# pip install wheezy.html
# pip install pytidylib
# pip install pycountry
# pip install colorama
# pip install humanfriendly

import sys, os, re, term, logging, uuid, shutil, humanfriendly

from galleries_script import *
from galleries_script import access
from galleries_script import indexes
from galleries_script import albums
from galleries_script import images

from galleries.galleries import search_galleries
from galleries.access import ACCESS_FILE_NAME

TITLE = 'Galleries'

def safe(value):
    import unicodedata
    value = unicodedata.normalize('NFKC', value)
    value = re.sub('[^\w\s-]', '', value, flags=re.U).strip().lower()
    return value

def gallery_stat(path):
    number_of_pictures = 0
    number_of_thumbnail_pictures = 0
    size_on_disk = 0
    for root, directories, files in os.walk(path):
        if root.endswith('/p'):
            number_of_pictures = len(files)
        if root.endswith('/t'):
            number_of_thumbnail_pictures = len(files)
        size_on_disk = size_on_disk + sum(os.path.getsize(os.path.join(root, name)) for name in files)
    return number_of_pictures, number_of_thumbnail_pictures, size_on_disk

def galleries_list(fspath, stat=False, **args):
    term.banner("LIST OF GALLERIES")

    compact = not stat

    galleries = search_galleries(fspath)

    if compact:
        print_gallery_name('Name', term.em)
        print(term.em("{1}{0}".format('Albums', SYMBOL_SEPARATOR_CLEAR)))
    for gallery in galleries:
        if compact:
            print_gallery_name(gallery.name)
            print(term.p("{1}{0}".format(
                ', '.join(str(x) for x in gallery.albums),
                SYMBOL_SEPARATOR
            )))
        else:
            print_gallery_name(gallery.name, term.em, end='\n')
            print(term.p("{0:>20}: {1}".format('Albums', ', '.join(str(x) for x in gallery.albums))))
            nop, notp, sod = gallery_stat(gallery.path)
            print(term.p("{0:>20}: {1!s}".format("Number of pictures", nop)))
            print(term.p("{0:>20}: {1}".format("Size on disk", humanfriendly.format_size(sod))))
            print()

class GalleryInstaller:
    def __init__(self, fspath, interactive=False):
        self.fspath = fspath

        self.destination_path = None
        self.destination_path_backup = None

        self.interactive = interactive

    def __enter__(self):
        return self

    def __exit__(self, exception, value, traceback):
        if exception is None:
            term.banner("DONE", type='INFO')
            self.__backup_destination_clean()
        else:
            self.__backup_destination_restore()

    def __backup_destination(self, gallery_name):
        assert self.destination_path and os.path.isdir(self.destination_path)
        self.destination_path_backup = os.path.join(
            self.fspath, "{0}-{1}".format(str(uuid.uuid4()), gallery_name)
        )
        shutil.copytree(self.destination_path, self.destination_path_backup)
    def __backup_destination_restore(self):
        assert self.destination_path and os.path.isdir(self.destination_path)
        if self.destination_path_backup and os.path.isdir(self.destination_path_backup):
            shutil.rmtree(self.destination_path)
            shutil.move(self.destination_path_backup, self.destination_path)
    def __backup_destination_clean(self):
        if self.destination_path_backup and os.path.isdir(self.destination_path_backup):
            shutil.rmtree(self.destination_path_backup)

    def __check_destination(self, gallery_name):
        assert self.destination_path
        if os.path.exists(self.destination_path):
            if os.path.isdir(self.destination_path):
                term.banner("GALLERY '{0}' ALREADY EXISTS".format(gallery_name), type='WARN')
                if not self.interactive or not term.ask("OVERWRITE EXISTING GALLERY?"):
                    raise GSAbortError("OVERWRITE EXISTING GALLERY")
                self.__backup_destination(gallery_name)
            else:
                raise GSError(
                    "COULDN'T OVERWRITE EXISTING GALLERY\nAT '{0}'".format(self.destination_path)
                )
        return True

    def __install(self, gallery):
        assert self.destination_path
        if os.path.exists(self.destination_path):
            shutil.rmtree(self.destination_path)
        shutil.copytree(gallery.path, self.destination_path)

    def __restore_access(self):
        assert self.destination_path and os.path.isdir(self.destination_path)
        if self.destination_path_backup:
            path = os.path.join(self.destination_path_backup, ACCESS_FILE_NAME)
            path_restored = os.path.join(self.destination_path, ACCESS_FILE_NAME)
            if os.path.isfile(path):
                shutil.copyfile(path, path_restored)

    def install(self, gallery):
        term.banner("INSTALL GALLERY")

        self.destination_path = os.path.join(self.fspath, gallery.name)

        self.__check_destination(gallery.name)
        self.__install(gallery)
        self.__restore_access()

def galleries_install(gallery_path, fspath, htpasswd=None, interactive=False, **args):
    gallery = load_gallery(gallery_path)

    with GalleryInstaller(fspath, interactive) as installer:
        installer.install(gallery)

        if htpasswd:
            access.manage(gallery_name=gallery.name, fspath=fspath, htpasswd=htpasswd,
                access_command='init')
        if args['set_albums_cover']:
            for a in gallery.albums:
                album.setcover(gallery_name=gallery.name, album_name=a.label,
                    image_name=args['set_albums_cover'], fspath=fspath)

DESCRIPTION = """
This script handles content and access rights for web galleries.
"""

EPILOG = """
"""

import argparse
import configparser

def path_argument(value):
    if not value.endswith('/'):
        raise argparse.ArgumentError(None,
            "{0} must end with a slash '/'".format('path'))
    return value

def main(args=None):
    config = configparser.ConfigParser()
    config.read('galleries.ini')

    config_htpasswd = config['Access'].get('htpasswd') if 'Access' in config else None

    parser = argparse.ArgumentParser(
        prog=os.getenv('SCRIPT'),
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--fspath', type=path_argument, default='/var/www/web/',
        help="Path to web galleries on filesystem. Defaults to '/var/www/web/'.")
    parser.add_argument('--wspath', type=path_argument, default='/',
        help="Path to web galleries on webserver. Defaults to '/'.")
    if 'Defaults' in config:
        parser.set_defaults(**config['Defaults'])
    subparsers = parser.add_subparsers(title='commands', dest='command')
    subparsers.required = True

    parser_interactive = argparse.ArgumentParser(add_help=False)
    parser_interactive.add_argument('-i', '--interactive', action='store_true', default=False,
        help="enable interactive mode and ask for input")
    parser_verbose = argparse.ArgumentParser(add_help=False)
    parser_verbose.add_argument('-v', '--verbose', action='store_true', default=False,
        help="enable verbose output")
    parser_dryrun = argparse.ArgumentParser(add_help=False)
    parser_dryrun.add_argument('-n', '--dry-run', action='store_true', default=False,
        help="simulate actions only and print expected results")

    # list command
    parser_list = subparsers.add_parser('list',
        help="List all web galleries.")
    parser_list.set_defaults(function=galleries_list)
    parser_list.add_argument('--stat', action='store_true', default=False,
        help="Print statistics for web galleries.")

    # install command
    parser_install = subparsers.add_parser('install', parents=[parser_interactive],
        help="Install web gallery.")
    parser_install.set_defaults(function=galleries_install)
    parser_install.add_argument('--htpasswd', default=config_htpasswd,
        help="Path to htpasswd file for access control.")
    parser_install.add_argument('--set-albums-cover', metavar='image_name',
        help="Set cover for albums of web gallery.")
    parser_install.add_argument('gallery_path',
        help="Path to web gallery to install.")

    # access command
    parser_access = subparsers.add_parser('access',
        help="Manage access to web gallery.")
    subparsers_access = parser_access.add_subparsers(
        title='access commands', dest='access_command')
    subparsers_access.required = True
    # access show command
    parser_access_show = subparsers_access.add_parser('show',
        help="Show access to web galleries.")
    parser_access_show.set_defaults(function=access.show)
    # access init command
    parser_access_init = subparsers_access.add_parser('init',
        help="Initialize access to web gallery.")
    parser_access_init.set_defaults(function=access.manage)
    parser_access_init.add_argument('--htpasswd',
        required=(config_htpasswd is None), default=config_htpasswd,
        help="Path to htpasswd file for access control.")
    parser_access_init.add_argument('gallery_name',
        help="Name of web gallery to manage.")
    # access list command
    parser_access_list = subparsers_access.add_parser('list',
        help="List access to web gallery.")
    parser_access_list.set_defaults(function=access.manage)
    parser_access_list.add_argument('gallery_name',
        help="Name of web gallery to manage.")
    # access adduser command
    parser_access_adduser = subparsers_access.add_parser('adduser',
        help="Add access for user to web gallery.")
    parser_access_adduser.set_defaults(function=access.manage)
    parser_access_adduser.add_argument('username', nargs='+',
        help="Name of user to grant access to web gallery.")
    parser_access_adduser.add_argument('gallery_name',
        help="Name of web gallery to manage.")
    # access deluser command
    parser_access_removeuser = subparsers_access.add_parser('removeuser',
        help="Remove access for user to web gallery.")
    parser_access_removeuser.set_defaults(function=access.manage)
    parser_access_removeuser.add_argument('username', nargs='+',
        help="Name of user to revoke access to web gallery.")
    parser_access_removeuser.add_argument('gallery_name',
        help="Name of web gallery to manage.")

    # indexes command
    parser_indexes = subparsers.add_parser('indexes',
        help="Manage indexes of web galleries.")
    subparsers_indexes = parser_indexes.add_subparsers(
        title='indexes commands', dest='indexes command')
    subparsers_indexes.required = True
    # indexes create command
    parser_indexes_create = subparsers_indexes.add_parser('create', parents=[parser_verbose],
        help="Create indexes for web galleries.")
    parser_indexes_create.add_argument('--users', action='store_true', default=False,
        help="Create indexes for users.")
    parser_indexes_create.set_defaults(function=indexes.create)
    # indexes install command
    config_htpasswd = config['Access'].get('htpasswd') if 'Access' in config else None
    parser_indexes_install = subparsers_indexes.add_parser('install',
        help="Install indexes for web galleries.")
    parser_indexes_install.add_argument('--htpasswd',
        required=(config_htpasswd is None), default=config_htpasswd,
        help="Path to htpasswd file for access control.")
    parser_indexes_install.set_defaults(function=indexes.install)

    # albums command
    parser_albums = subparsers.add_parser('albums',
        help="Manage albums of web gallery.")
    subparsers_albums = parser_albums.add_subparsers(
        title='albums commands', dest='albums command')
    subparsers_albums.required = True
    # albums setcover command
    parser_albums_setcover = subparsers_albums.add_parser('setcover',
        help="Set cover for album of web gallery.")
    parser_albums_setcover.set_defaults(function=albums.setcover)
    parser_albums_setcover.add_argument('image_name',
        help="Name of image to be used as cover (must exist inside gallery).")
    parser_albums_setcover.add_argument('album_name',
        help="Name of album inside web gallery.")
    parser_albums_setcover.add_argument('gallery_name',
        help="Name of web gallery to manage.")

    # images command
    parser_images = subparsers.add_parser('images',
        help="Manage images of web gallery.")
    subparsers_images = parser_images.add_subparsers(
        title='images commands', dest='images_command')
    subparsers_images.required = True
    # images optimize command
    parser_images_optimize = subparsers_images.add_parser('optimize', parents=[parser_dryrun],
        help="Optimize images of web gallery.")
    parser_images_optimize.set_defaults(function=images.optimize)
    parser_images_optimize.add_argument('gallery_name',
        help="Name of web gallery to manage.")

    try:
        arguments = parser.parse_args() if args == None else parser.parse_args(args)
        if 'verbose' in arguments and arguments.verbose == True:
            logging_level = logging.INFO
        else:
            logging_level = logging.WARNING
        logging.basicConfig(level=logging_level,
            format='[%(levelname)s][%(funcName)s] %(message)s')
        arguments.function(**vars(arguments))
    except GSError as x:
        term.banner(str(x), type='ERROR')
    except FileNotFoundError as x:
        term.banner("NOT FOUND '{0}'".format(x), type='ERROR')

if __name__ == "__main__":
    main()

