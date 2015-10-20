#!python
# coding: utf-8
#
# Dependencies:
# pip install wheezy.template
# pip install colorama

import sys, os, term

from wheezy import template as wheezy

template_engine = wheezy.engine.Engine(
    loader=wheezy.loader.FileLoader(['/home/dreizehn/scripts/source/templates']),
    extensions=[wheezy.ext.core.CoreExtension()]
)

from galleries.galleries import search_galleries, search_gallery

def galleries_list(args):
    term.banner("LIST OF GALLERIES")
    galleries = search_galleries(args.path)
    term.em("{0:40}   {1}".format("Name", "Albums"))
    for gallery in galleries:
        term.p("{0:40} | {1}".format(
            gallery.name,
            ", ".join(str(x) for x in gallery.albums)
        ))

def index_create(args):
    term.banner("CREATE INDEX")
    galleries = search_galleries(args.path)
    template = template_engine.get_template('galleries_index.html')
    print(template.render({'title': 'Index', 'galleries': galleries}))

def access_manage_init(gallery, htpasswd):
    term.banner("INITIALIZE ACCESS TO GALLERY '{0}'".format(gallery))
    access = gallery.access
    if access == None:
        gallery.access_init(htpasswd)
    gallery.access_write()

def access_manage_list(gallery):
    term.banner("LIST ACCESS TO GALLERY '{0}'".format(gallery))
    term.em("{0:40}   {1}".format("Name", "Password"))
    for user in gallery.access.users:
        term.p("{0:40} | {1}".format(
            user,
            "***" if gallery.access.get_password(user) else "???"
        ))

def access_manage_adduser(gallery, username):
    term.banner("ADD ACCESS FOR USER '{1}' TO GALLERY '{0}'".format(gallery, username))
    gallery.access.add_user(username)
    gallery.access_write()

def access_manage(args):
    gallery = search_gallery(args.path, args.gallery_name)
    if gallery:
        if args.access_command == 'init':
            access_manage_init(gallery, args.htpasswd)
        else:
            if gallery.access:
                if args.access_command == 'list':
                    access_manage_list(gallery)
                elif args.access_command == 'adduser':
                    for username in args.username:
                        access_manage_adduser(gallery, username)
            else:
                term.banner("NO ACCESS INFORMATION FOR GALLERY '{0}'".format(gallery),
                    type="ERROR")
    else:
        term.banner("GALLERY {0} NOT FOUND AT {1}".format(args.gallery_name, args.path),
            type='ERROR')

DESCRIPTION = """
This script handles content and access rights for web galleries.
"""

EPILOG = """
"""

def main(args=None):
    import argparse
    import configparser

    config = configparser.ConfigParser()
    config.read('galleries.ini')

    parser = argparse.ArgumentParser(
        prog=os.getenv('SCRIPT'),
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--path', default='/var/www/web',
        help="Path to web galleries. Defaults to '/var/www/web'")
    if 'Defaults' in config:
        parser.set_defaults(**config['Defaults'])
    subparsers = parser.add_subparsers(title='commands', dest='command')
    subparsers.required = True

    # list command
    parser_list = subparsers.add_parser('list',
        help="List all galleries.")
    parser_list.set_defaults(function=galleries_list)

    # access command
    parser_access = subparsers.add_parser('access',
        help="Manage access to web gallery.")
    subparsers_access = parser_access.add_subparsers(
        title='access commands', dest='access_command')
    subparsers_access.required = True
    # access init command
    parser_access_init = subparsers_access.add_parser('init',
        help="Initialize access to web gallery.")
    parser_access_init.set_defaults(function=access_manage)
    parser_access_init.add_argument('--htpasswd', required=True,
        help="Path to htpasswd file for access control")
    parser_access_init.add_argument('gallery_name',
        help="Name of web gallery to manage.")
    # access list command
    parser_access_list = subparsers_access.add_parser('list',
        help="List access to web gallery.")
    parser_access_list.set_defaults(function=access_manage)
    parser_access_list.add_argument('gallery_name',
        help="Name of web gallery to manage.")
    # access adduser command
    parser_access_adduser = subparsers_access.add_parser('adduser',
        help="Add access for user to web gallery.")
    parser_access_adduser.set_defaults(function=access_manage)
    parser_access_adduser.add_argument('username', nargs='+',
        help="Name of user to grant access to web gallery.")
    parser_access_adduser.add_argument('gallery_name',
        help="Name of web gallery to manage.")

    # index command
    parser_index = subparsers.add_parser('index',
        help="Manage indexes for galleries.")
    subparsers_index = parser_index.add_subparsers(
        title='index commands', dest='index command')
    subparsers_index.required = True
    # index create command
    parser_index_create = subparsers_index.add_parser('create',
        help="Create indexes for galleries.")
    parser_index_create.set_defaults(function=index_create)

    try:
        arguments = parser.parse_args() if args == None else parser.parse_args(args)
        arguments.function(arguments)
    except FileNotFoundError as x:
        term.banner("NOT FOUND '{0}'".format(x), type='ERROR')

if __name__ == "__main__":
    main()

