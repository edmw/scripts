#!python
# coding: utf-8

import sys, os

from galleries.galleries import search_galleries

def galleries_list(args):
  galleries = search_galleries(args.path)
  for gallery in galleries:
    print gallery
    for album in gallery.albums:
      print "", album

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

  arguments = parser.parse_args() if args == None else parser.parse_args(args)
  arguments.func(arguments)

if __name__ == "__main__":
  main()

