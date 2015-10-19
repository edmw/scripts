#!python
# coding: utf-8
#
# Dependencies:
# pip install python-augeas
# pip install BeautifulSoup
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
  print("{0:40} | {1}".format("Name", "Albums"))
  for gallery in galleries:
    print("{0:40} | {1}".format(gallery.name, ", ".join(str(x) for x in gallery.albums)))

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
  access = gallery.access
  if access:
    print("{0:40} | {1}".format("Name", "Password"))
    for user in access.users:
      print("{0:40} | {1}".format(user, "***" if access.get_password(user) else "???"))
  else:
    term.banner("NO ACCESS INFORMATION FOR GALLERY '{0}'".format(gallery), type="ERROR")

def access_manage(args):
  gallery = search_gallery(args.path, args.gallery_name)
  if gallery:
    if args.command == 'init':
      access_manage_init(gallery, args.htpasswd)
    elif args.command == 'list':
      access_manage_list(gallery)
  else:
    term.banner("GALLERY {0} NOT FOUND AT {1}".format(args.gallery_name, args.path), type='ERROR')

DESCRIPTION = """
This script handles content and access rights for web galleries.
"""

EPILOG = """
"""

def main(args=None):
  import argparse

  parser = argparse.ArgumentParser(
    prog=os.getenv('SCRIPT'),
    description=DESCRIPTION,
    epilog=EPILOG,
    formatter_class=argparse.RawDescriptionHelpFormatter
  )
  parser.add_argument('--path', default='/var/www/web/privat',
    help="Path to web galleries. Defaults to '/var/www/web/privat'")
  subparsers = parser.add_subparsers(title='commands')

  # list command
  parser_list = subparsers.add_parser('list',
    help='List all galleries.')
  parser_list.set_defaults(function=galleries_list)

  # access command
  parser_access = subparsers.add_parser('access',
    help="Manage access to web gallery.")
  subparsers_access = parser_access.add_subparsers(title='access commands')
  # access init command
  parser_access_init = subparsers_access.add_parser('init',
    help="Initialize access to web gallery.")
  parser_access_init.add_argument('--htpasswd', required=True,
    help="Path to htpasswd file for access control")
  parser_access_init.set_defaults(function=access_manage)
  parser_access_init.set_defaults(command='init')
  # access list command
  parser_access_list = subparsers_access.add_parser('list',
    help="List access to web gallery.")
  parser_access_list.set_defaults(function=access_manage)
  parser_access_list.set_defaults(command='list')
  parser_access.add_argument('gallery_name',
    help="Name of web gallery to manage.")

  # index command
  parser_index = subparsers.add_parser('index',
    help='Manage indexes for galleries.')
  subparsers_index = parser_index.add_subparsers(title='index commands')
  # index create command
  parser_index_create = subparsers_index.add_parser('create',
    help='Create indexes for galleries.')
  parser_index_create.set_defaults(function=index_create)

  arguments = parser.parse_args() if args == None else parser.parse_args(args)
  arguments.function(arguments)

if __name__ == "__main__":
  main()

