# coding: utf-8

import sys, os, re, term

from galleries_script import *

from galleries.galleries import search_galleries

SYMBOL_CHECKED = '✔'

def show(fspath, **args):
    term.banner("ACCESS TO WEB GALLERIES")

    galleries = search_galleries(fspath, load_access=True)

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
            print_gallery_name('Name' if i == 0 else '', term.em)
            print(term.em("{1}{0}".format(
                '   '.join(c),
                SYMBOL_SEPARATOR_CLEAR
            )))
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
            print_gallery_name(gallery.name, term.p if gallery.access else term.negative)
            print(term.p("{1}{0}".format(
                SYMBOL_SEPARATOR.join(c),
                SYMBOL_SEPARATOR_CLEAR
            )))
    else:
        term.banner("NO ACCESS FOR GALLERIES", type='ERROR')

def manage_init(gallery, htpasswd):
    term.banner("INITIALIZE ACCESS TO GALLERY '{0}'".format(gallery))
    access = gallery.access
    if access == None:
        gallery.access_init("Galleries", htpasswd)
    else:
        access.authname = "Galleries"
        access.authuserfile = htpasswd
    gallery.access_write()
    term.banner("DONE", type='INFO')

def manage_list(gallery):
    term.banner("LIST ACCESS TO GALLERY '{0}'".format(gallery))
    print_gallery_name('Name', term.em)
    print(term.em("{1}{0}".format('Password', SYMBOL_SEPARATOR_CLEAR)))
    for user in gallery.access.users:
        print_gallery_name(str(user))
        print(term.p("{1}{0}".format(
            '***' if gallery.access.get_password(user) else '???',
            SYMBOL_SEPARATOR
        )))

def manage_adduser(gallery, username):
    term.banner("ADD ACCESS FOR USER '{1}' TO GALLERY '{0}'".format(gallery, username))
    gallery.access.add_user(username)
    gallery.access_write()
    term.banner("DONE", type='INFO')

def manage_removeuser(gallery, username):
    term.banner("REMOVE ACCESS FOR USER '{1}' TO GALLERY '{0}'".format(gallery, username))
    if gallery.access.has_user(username):
        gallery.access.remove_user(username)
        gallery.access_write()
        term.banner("DONE", type='INFO')
    else:
        raise GSError("ACCESS: USER '{0}' NOT FOUND IN GALLERY '{1}'".format(username, gallery.name))

def manage(gallery_name, fspath, access_command, username=None, htpasswd=None, **args):
    gallery = get_gallery(fspath, gallery_name, load_access=True)
    if access_command == 'init':
        manage_init(gallery, htpasswd)
    else:
        if gallery.access:
            if access_command == 'list':
                manage_list(gallery)
            elif access_command == 'adduser':
                for username in username:
                    manage_adduser(gallery, username)
            elif access_command == 'removeuser':
                for username in username:
                    manage_removeuser(gallery, username)

        else:
            term.banner("NO ACCESS INFORMATION FOR GALLERY '{0}'".format(gallery),
                type="ERROR")

