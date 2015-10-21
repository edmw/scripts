# coding: utf-8

import sys, os, os.path, shlex

class User:
    def __init__(self, name, pwhash=None):
        self.name = name
        self.pwhash = pwhash

    def __str__(self):
        return self.name

    def __lt__(self, other):
        return self.name < other.name

    __instances = {}

    def factory(name, pwhash=None):
        if not User.__instances.get(name):
            User.__instances[name] = User(name, pwhash)
        return User.__instances.get(name)

    factory = staticmethod(factory)

class Access:
    def __init__(self,
        authname=None,
        authtype=None,
        authbasicprovider=None,
        authuserfile=None,
        usernames=[]
    ):
        self.users = []
        self.conf = []

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
        self.authuserhashes = None
        if self.authuserfile:
            self.authuserhashes = self.__load_authuserfile(self.authuserfile)

        for username in usernames:
            self.add_user(username)

    def __load_authuserfile(self, filename):
        pwhashes = {}
        with open(filename) as f:
            for line in f:
                if ':' in line:
                    name, pwhash = line.rstrip().split(':', 1)
                    pwhashes[name] = pwhash
        return pwhashes

    def add_user(self, name):
        user = User.factory(name, pwhash=self.authuserhashes.get(name))
        if not user in self.users:
            self.users.append(user)

    def get_password(self, user):
        """ Get password (encrypted) for the given user.

            htpasswd must be loaded and its filename must match self.authuserfile.
        """
        return None

    def write(self, path):
        def write_line(f, key=None, values=None, quote=True):
            if key and values:
                if isinstance(values, list):
                    v = " ".join(values)
                else:
                    v = values
                if quote:
                    f.write('{0} {2}{1}{2}'.format(key, v, '"' if ' ' in v else ''))
                else:
                    f.write('{0} {1}'.format(key, v))
            f.write('\n')
        
        path = os.path.join(path, ACCESS_FILE_NAME)
        with open(path, 'w') as f:
            write_line(f, 'AuthName', self.authname)
            write_line(f, 'AuthType', self.authtype)
            if self.authbasicprovider:
                write_line(f, 'AuthBasicProvider', self.authbasicprovider)
            if self.authuserfile:
                write_line(f, 'AuthUserFile', self.authuserfile)
            for user in self.users:
                write_line(f, 'Require user', user.name)
            write_line(f)
            for c in self.conf:
                write_line(f, c[0], c[1], quote=False)

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

        a = { 'usernames': [] }
        for line in lines:
            key, values = parse(line)
            if key:
                if key == 'user':
                    a['usernames'].append(values)
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

