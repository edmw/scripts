# coding: utf-8

import sys, os, re, fnmatch, shutil, subprocess, term

from galleries_script import get_gallery
from galleries_script import GSError

def images(gallery_name, fspath, **args):
    gallery = get_gallery(fspath, gallery_name)

    term.banner("OPTIMIZE IMAGES (JPEG)")

    dry = args.get('dry_run')

    try:
        subprocess.call(['djpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.call(['cjpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError as x:
        term.banner("MOZJPEG MUST BE INSTALLED", type='INFO')
        raise GSError("OPTIMIZE: {0}".format(x))

    if dry:
        term.banner("DRY RUN", type='INFO')

    for directory in ['p', 't']:
        path = os.path.join(gallery.path, directory)
        for root, directories, files in os.walk(path):
            for filename in sorted(fnmatch.filter(files, '*.jpg')):
                path = os.path.join(root, filename)
                size = os.path.getsize(path)

                if size:
                    djpeg = subprocess.Popen(['djpeg', path],
                        stdout=subprocess.PIPE)
                    cjpeg = subprocess.Popen(['cjpeg',
                            '-quality', '92',
                            '-opt',
                            '-sample', '1x1',
                            '-notrellis'
                        ],
                        stdin=djpeg.stdout, stdout=subprocess.PIPE)

                    new_size = 0
                    new_path = None

                    if dry:
                        with cjpeg:
                            for chunk in iter(lambda: cjpeg.stdout.read(4096), b''):
                                new_size = new_size + len(chunk)
                    else:
                        new_path = path + ".new"
                        with cjpeg, open(new_path, 'wb') as f:
                            for chunk in iter(lambda: cjpeg.stdout.read(4096), b''):
                                f.write(chunk)
                                new_size = new_size + len(chunk)

                    ratio = 100 / size * new_size
                    print(term.p("{0:32} {1:.2f}% {2:8} {3:8}".format(filename, ratio, size, new_size)))

                    if new_path:
                        shutil.move(new_path, path)

    term.banner("DONE", type='INFO')

