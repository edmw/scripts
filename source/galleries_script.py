#!python
# coding: utf-8

import sys, os

from wheezy import template as wheezy

template_engine = wheezy.engine.Engine(
  loader=wheezy.loader.FileLoader(['/home/dreizehn/scripts/source/templates']),
  extensions=[wheezy.ext.core.CoreExtension()]
)

from galleries.galleries import search_galleries

def galleries_list(args):
  galleries = search_galleries(args.path)
  for gallery in galleries:
    print("{0:40} | {1}".format(gallery, ", ".join(str(x) for x in gallery.albums)))

def index_create(args):
  galleries = search_galleries(args.path)
  template = template_engine.get_template('galleries_index.html')
  print(template.render({'galleries': galleries}))

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
  parser_list.set_defaults(func=galleries_list)

  # index command
  parser_index = subparsers.add_parser('index',
    help='Manage index html.')
  subparsers_index = parser_index.add_subparsers(title='index commands')
  # index create command
  parser_index_create = subparsers_index.add_parser('create',
    help='Create index html.')
  parser_index_create.set_defaults(func=index_create)

  arguments = parser.parse_args() if args == None else parser.parse_args(args)
  arguments.func(arguments)

if __name__ == "__main__":
  main()

