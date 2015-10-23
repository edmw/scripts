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

import sys, os, re, term

from galleries.galleries import search_galleries, search_gallery
from galleries.access import Access

from templates import TemplateEngine

template_engine = TemplateEngine(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

TITLE = 'Galleries'

SYMBOL_SEPARATOR = ' │ '
SYMBOL_SEPARATOR_CLEAR = '   '

def safe(value):
    import unicodedata
    value = unicodedata.normalize('NFKC', value)
    value = re.sub('[^\w\s-]', '', value, flags=re.U).strip().lower()
    return value

def collect_users(galleries):
    """ Collect list of all users in all galleries.
    """
    u = set()
    for gallery in galleries:
        access = gallery.access
        if access:
            u = u | set(access.users)
    return u

def collect_galleries(galleries, user):
    """ Collect list of galleries for given user.
    """
    g = []
    for gallery in galleries:
        if gallery.access and user in gallery.access.users:
            g.append(gallery)
    return g

def galleries_list(args):
    term.banner("LIST OF GALLERIES")
    galleries = search_galleries(args.fspath)
    term.em("{0:40}   {1}".format('Name', 'Albums'))
    for gallery in galleries:
        term.p("{0:40}{2}{1}".format(
            gallery.name,
            ', '.join(str(x) for x in gallery.albums),
            SYMBOL_SEPARATOR
        ))

def index_create_write(fspath, galleries, path='./', title='Index'):
    filename = os.path.join(fspath, 'index.html')
    with open(filename, 'wb') as f:
        html = template_engine.render('galleries_index.html', {
            'path': path,
            'title': title,
            'galleries': galleries
        })
        f.write(html)

def index_create(args):
    term.banner("CREATE INDEXES")

    galleries = search_galleries(args.fspath)
    index_create_write(args.fspath, galleries, path=args.wspath)

    if args.users:
        users = collect_users(galleries)
        for user in users:
            user_path = os.path.join(args.fspath, "~{0}".format(safe(user.name)))
            if not os.path.exists(user_path):
                os.mkdir(user_path)
            if os.path.isdir(user_path):
                user_galleries = collect_galleries(galleries, user)
                index_create_write(user_path, user_galleries,
                    path=args.wspath, title=user.name)
            else:
                raise IOError("CREATE INDEXES: could not write index for user '{0}'".format(str(user)))
    term.banner("DONE", type='INFO')

def index_install(args):
    """ Install indexes: Create htaccess file with rewrite rules to
        serve user-specific indexes.

        Indexes must be created by executing 'index create' command.

        NOTE: htaccess file will be overwritten!
    """
    term.banner("INSTALL INDEXES")
    galleries = search_galleries(args.fspath)
    users = collect_users(galleries)
    access = Access(authname=TITLE, authuserfile=args.htpasswd)
    access.users.extend(users)
    access.conf.append(('RewriteEngine', 'On'))
    access.conf.append(('RewriteBase', args.wspath))
    access.conf.append(('RewriteCond', '%{REMOTE_user} ^.+$'))
    access.conf.append(('RewriteRule', "^$ {0}~%{{REMOTE_user}} [R,L]".format(args.wspath)))
    access.write(args.fspath)
    term.banner("DONE", type='INFO')

SYMBOL_CHECKED = '✔'

def access_show(args):
    term.banner("ACCESS TO WEB GALLERIES")
    galleries = search_galleries(args.fspath)
    # create list of all usernames in all galleries
    users = collect_users(galleries)
    if len(users):
        users = sorted(users)
        # find the maximum length of any username
        m = max(len(user.name) for user in users)
        # print useernames
        for i in reversed(range(m)):
            c = []
            for user in users:
                name = user.name
                if i < len(name):
                    c.append(name[len(name) - 1 - i])
                else:
                    c.append(' ')
            term.em("{0:40}{2}{1}".format(
                'Name' if i == 0 else '',
                '   '.join(c),
                SYMBOL_SEPARATOR_CLEAR
            ))
        # print galleries
        for gallery in galleries:
            c = []
            for user in users:
                if gallery.access and user in gallery.access.users:
                    # user has access to gallery
                    if user.pwhash:
                        # user has password
                        c.append(term.positive(SYMBOL_CHECKED))
                    else:
                        # user has no password
                        c.append(term.negative(SYMBOL_CHECKED))
                else:
                    # user has no access to gallery
                    c.append(' ')
            term.p("{0:40}   {1}".format(
                gallery.name,
                SYMBOL_SEPARATOR.join(c)
            ))
    else:
        term.banner("NO ACCESS FOR GALLERIES", type='ERROR')

def access_manage_init(gallery, htpasswd):
    term.banner("INITIALIZE ACCESS TO GALLERY '{0}'".format(gallery))
    access = gallery.access
    if access == None:
        gallery.access_init("Galleries", htpasswd)
    else:
        access.authname = "Galleries"
        access.authuserfile = htpasswd
    gallery.access_write()
    term.banner("DONE", type='INFO')

def access_manage_list(gallery):
    term.banner("LIST ACCESS TO GALLERY '{0}'".format(gallery))
    term.em("{0:40}{2}{1}".format("Name", "Password", SYMBOL_SEPARATOR_CLEAR))
    for user in gallery.access.users:
        term.p("{0:40}{2}{1}".format(
            str(user),
            '***' if gallery.access.get_password(user) else '???',
            SYMBOL_SEPARATOR
        ))

def access_manage_adduser(gallery, username):
    term.banner("ADD ACCESS FOR USER '{1}' TO GALLERY '{0}'".format(gallery, username))
    gallery.access.add_user(username)
    gallery.access_write()
    term.banner("DONE", type='INFO')

def access_manage(args):
    gallery = search_gallery(args.fspath, args.gallery_name)
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
        term.banner("GALLERY {0} NOT FOUND AT {1}".format(args.gallery_name, args.fspath),
            type='ERROR')

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
    # access show command
    parser_access_show = subparsers_access.add_parser('show',
        help="Show access to web galleries.")
    parser_access_show.set_defaults(function=access_show)
    # access init command
    config_htpasswd = config['Access'].get('htpasswd') if 'Access' in config else None
    parser_access_init = subparsers_access.add_parser('init',
        help="Initialize access to web gallery.")
    parser_access_init.set_defaults(function=access_manage)
    parser_access_init.add_argument('--htpasswd',
        required=(config_htpasswd is None), default=config_htpasswd,
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
        help="Manage indexes for web galleries.")
    subparsers_index = parser_index.add_subparsers(
        title='index commands', dest='index command')
    subparsers_index.required = True
    # index create command
    parser_index_create = subparsers_index.add_parser('create',
        help="Create indexes for web galleries.")
    parser_index_create.add_argument('--users', action='store_true', default=False,
        help="Create indexes for users.")
    parser_index_create.set_defaults(function=index_create)
    # index install command
    config_htpasswd = config['Access'].get('htpasswd') if 'Access' in config else None
    parser_index_install = subparsers_index.add_parser('install',
        help="Install indexes for web galleries.")
    parser_index_install.add_argument('--htpasswd',
        required=(config_htpasswd is None), default=config_htpasswd,
        help="Path to htpasswd file for access control")
    parser_index_install.set_defaults(function=index_install)

    try:
        arguments = parser.parse_args() if args == None else parser.parse_args(args)
        arguments.function(arguments)
    except FileNotFoundError as x:
        term.banner("NOT FOUND '{0}'".format(x), type='ERROR')

if __name__ == "__main__":
    main()

