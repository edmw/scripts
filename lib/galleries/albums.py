# coding: utf-8

import sys, os, os.path, re

class Album:
  def __init__(self, path, name, label=None):
    self.path = path
    self.name = name
    self.label = label

  def __str__(self):
    return " ".join([self.label])

  def factory(path, name):
    path = os.path.join(path, name)
    if not os.path.isfile(path):
      return None

    a = {}

    # parse name
    m = ALBUM_NAME_PATTERN.match(name)
    if not m:
      return None
    a['label'] = m.group(1)

    return Album(path, name, **a)
      
  factory = staticmethod(factory)

ALBUM_NAME_PATTERN = re.compile('^([p][234])\.html$')

def search_albums(path):
  """ Search albums at the given path.
  """
  albums = []

  names = [name for name in os.listdir(path)
    if os.path.isfile(os.path.join(path, name))
      and ALBUM_NAME_PATTERN.match(name)
  ]

  for name in reversed(sorted(names)):
    album = Album.factory(path, name)
    if album:
      albums.append(album)
  
  return albums

