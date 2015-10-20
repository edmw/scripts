# coding: utf-8

import sys, getpass

from colorama import init as colorama_init, Fore as FG, Back as BG, Style

def banner(*args, **kwargs):
    if len(args):
        color = FG.GREEN + Style.BRIGHT
        if kwargs:
            banner_type = kwargs.get('type')
            if banner_type == 'INFO':
                color = FG.WHITE + Style.DIM
            elif banner_type == 'HINT':
                color = FG.MAGENTA + Style.DIM
            elif banner_type == 'WARN':
                color = FG.YELLOW + Style.BRIGHT
            elif banner_type == 'ERROR':
                color = FG.RED + Style.BRIGHT
        print(color + args[0] + Style.NORMAL)
        if len(args) > 1:
            print(color + '\n'.join(str(arg) for arg in args[1:]))
        print(BG.RESET + FG.RESET)

def p(text):
    print("{0}{1}".format(BG.RESET + FG.RESET + Style.NORMAL, text))

def em(text):
    print("{0}{1}".format(BG.RESET + FG.RESET + Style.BRIGHT, text))

def message(message):
    print(BG.RESET + FG.RESET + message)
    print

def in_password(prompt):
    password = getpass.getpass(prompt)
    print
    return password

class Progress():
    def __init__(self, total, size = 72):
        self.total = total
        self.size = size
        self.hashes = None
    def progress(self, index, total = None):
        if not total:
            total = self.total
        percent = 1
        if total > 0:
            percent = float(index) / total
        hashes = '#' * int(round(percent * self.size))
        if self.hashes == None or self.hashes != hashes:
            self.hashes = hashes
            spaces = ' ' * (self.size - len(hashes))
            sys.stdout.write("\rProgress: [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
            sys.stdout.flush()
    def finish(self, total = None):
        if not total:
            total = self.total
            self.progress(total)
        sys.stdout.write("\n\n")
        sys.stdout.flush()

colorama_init();

