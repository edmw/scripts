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
    return "{0}{1}".format(BG.RESET + FG.RESET + Style.NORMAL, text)

def em(text):
    return "{0}{1}".format(BG.RESET + FG.RESET + Style.BRIGHT, text)

def positive(text):
    return BG.RESET + FG.GREEN + Style.NORMAL + text + FG.RESET
def negative(text):
    return BG.RESET + FG.RED + Style.NORMAL + text + FG.RESET

def message(message):
    print(BG.RESET + FG.RESET + message)
    print()

def ask(message):
    value = input("{0} [Y/N] ".format(BG.RESET + FG.RESET + message))
    print()
    return value and value.lower() == 'y'

def in_password(prompt):
    password = getpass.getpass(prompt)
    print()
    return password

class Progress():
    def __init__(self, total, size=72, title='Progress:', bar=True):
        self.total = total
        self.size = size
        self.hashes = None
        self.title = title
        self.bar = bar
    def progress(self, index, total = None):
        if not total:
            total = self.total

        percent = 1
        if total > 0:
            percent = float(index) / total

        if self.bar:
            hashes = '#' * int(round(percent * self.size))
            if self.hashes == None or self.hashes != hashes:
                self.hashes = hashes
                spaces = ' ' * (self.size - len(hashes))
                sys.stdout.write(
                    "\r{2} [{0}] {1:3.0f}%".format(hashes + spaces, 100 * percent, self.title)
                )
                sys.stdout.flush()
        else:
            print(p("{0} {1:3.2f}%".format(self.title, 100 * percent)))
            
    def finish(self, total = None):
        if not total:
            total = self.total
            self.progress(total)

        if self.bar:
            sys.stdout.write("\n\n")
            sys.stdout.flush()

colorama_init();

