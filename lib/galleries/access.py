# coding: utf-8

import sys, os, os.path, shlex

class Access:
    def __init__(self,
        authname=None,
        authtype=None,
        authbasicprovider=None,
        authuserfile=None,
        users=[]
    ):
        self.authname = authname
        if not self.authname:
            self.authname = 'access'
        self.authtype = authtype
        if not self.authtype:
            self.authtype = 'basic'
        self.authbasicprovider = authbasicprovider
        if not self.authbasicprovider:
            self.authbasicprovider = 'file'
        self.authuserfile = authuserfile
        if self.authuserfile:
            self.__load_authuserfile(self.authuserfile)
        self.users = users

    def __load_authuserfile(self, filename):
        pass

    def add_user(self, name):
        if not name in self.users:
            self.users.append(name)

    def get_password(self, user):
        """ Get password (encrypted) for the given user.

            htpasswd must be loaded and its filename must match self.authuserfile.
        """
        return None

    def write(self, path):
        def write_line(f, key, values):
            if isinstance(values, list):
                v = " ".join(values)
            else:
                v = values
            f.write('{0} {2}{1}{2}\n'.format(key, v, '"' if ' ' in v else ''))
        
        path = os.path.join(path, ACCESS_FILE_NAME)
        with open(path, 'w') as f:
            write_line(f, 'AuthName', self.authname)
            write_line(f, 'AuthType', self.authtype)
            if self.authbasicprovider:
                write_line(f, 'AuthBasicProvider', self.authbasicprovider)
            if self.authuserfile:
                write_line(f, 'AuthUserFile', self.authuserfile)
            for user in self.users:
                write_line(f, 'Require user', user)
  
    def factory(lines):
        def unpack(sequence, n):
            it = iter(sequence)
            for x in range(n):
                yield next(it, None)
            yield tuple(it)

        def parse(line):
            key, values = unpack(shlex.split(line), 1)
            if key:
                k = key.upper()
                if k in [
                    'AUTHTYPE',
                    'AUTHNAME',
                    'AUTHBASICPROVIDER',
                    'AUTHUSERFILE',
                ]:
                    if len(values) == 1:
                        values = values[0]
                    return k.lower(), values
                elif k == 'REQUIRE':
                    subkey, values = unpack(values, 1)
                    if subkey:
                        k = subkey.upper()
                        if k == 'USER' and len(values) == 1:
                            return 'user', values[0]
            return None, None

        a = { 'users': [] }
        for line in lines:
            key, values = parse(line)
            if key:
                if key == 'user':
                    a['users'].append(values)
                else:
                    a[key] = values

        if a.get('authname') == None:
            raise ValueError("No AuthName given")
        if a.get('authtype') != 'basic':
            raise ValueError("Invalid AuthType '{0}'".format(a.get('authtype')))
        if a.get('authbasicprovider') != 'file':
            raise ValueError("Invalid AuthBasicProvider '{0}'".format(a.get('authbasicprovider')))
        if a.get('authuserfile') == None:
            raise ValueError("No AuthFile given")
  
        return Access(**a)

    factory = staticmethod(factory)
            
ACCESS_FILE_NAME = '.htaccess'

def read_access(path):
    path = os.path.join(path, ACCESS_FILE_NAME)
    if os.path.isfile(path):
        with open(path) as f:
            return Access.factory(f.readlines())
    return None

