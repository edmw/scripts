# coding: utf-8

import sys, os, re, term

from galleries_script import *

from galleries.galleries import search_galleries
from galleries.access import Access

from templates import TemplateEngine

template_engine = TemplateEngine(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

TITLE = 'Galleries'

def safe(value):
    import unicodedata
    value = unicodedata.normalize('NFKC', value)
    value = re.sub('[^\w\s-]', '', value, flags=re.U).strip().lower()
    return value

def create_write(fspath, galleries, path='./', title='Index'):
    filename = os.path.join(fspath, 'index.html')
    with open(filename, 'wb') as f:
        html = template_engine.render('galleries_index.html', {
            'path': path,
            'title': title,
            'galleries': galleries
        })
        f.write(html)

def create(users, fspath, wspath, **args):
    term.banner("CREATE INDEXES")

    progress = term.Progress(0, title='Searching:')
    galleries = search_galleries(fspath,
        load_access=True, load_albums=True, progress=progress.progress
    )
    progress.finish()

    create_write(fspath, galleries, path=wspath)

    if users:
        users = collect_users(galleries)
        for user in users:
            user_path = os.path.join(fspath, "~{0}".format(safe(user.name)))
            if not os.path.exists(user_path):
                os.mkdir(user_path)
            if os.path.isdir(user_path):
                user_galleries = collect_galleries_for_user(galleries, user)
                create_write(user_path, user_galleries,
                    path=wspath, title=user.name)
            else:
                raise IOError("CREATE INDEXES: could not write index for user '{0}'".format(str(user)))
    term.banner("DONE", type='INFO')

def install(wspath, fspath, htpasswd, **args):
    """ Install indexes: Create htaccess file with rewrite rules to
        serve user-specific indexes.

        Indexes must be created by executing 'index create' command.

        NOTE: htaccess file will be overwritten!
    """
    term.banner("INSTALL INDEXES")

    galleries = search_galleries(fspath, load_access=True)

    users = collect_users(galleries)
    access = Access(authname=TITLE, authuserfile=htpasswd)
    access.users.extend(users)
    access.conf.append(('RewriteEngine', 'On'))
    access.conf.append(('RewriteBase', wspath))
    access.conf.append(('RewriteCond', '%{REMOTE_user} ^.+$'))
    access.conf.append(('RewriteRule', "^$ {0}~%{{REMOTE_user}} [R,L]".format(wspath)))
    access.write(fspath)
    term.banner("DONE", type='INFO')

