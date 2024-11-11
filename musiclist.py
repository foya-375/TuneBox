#!/usr/bin/env python3

import os
import functools as fc

class MusicList:
  """
  Tree-like structure for the music-list, a music-list can contain a sub-music-list and raw music files
  """
  __allowed_extension = [
    ".mp3", ".wav"
  ]

  def __init__(self, path: os.path):
    self.music_list_names = []
    self.music_list = self._parse_music_list(path)

  def _parse_music_list(self, path: os.path):
    def is_playable(path):
      return os.path.splitext(path)[1] in self.__allowed_extension if not isinstance(path, dict) else True
    ml = []
    for item in os.listdir(path):
      f_d = os.path.join(path, item)
      ml.append(f_d if os.path.isfile(f_d) else self._parse_music_list(f_d))

    ml.sort(key=lambda x: isinstance(x, dict))
    self.music_list_names.append(os.path.basename(path))

    return {"name": os.path.basename(path), "list": list(filter(is_playable, ml))}

  def get_all_lists(self):
    """
    Return the entire music-list-tree
    """
    return self.music_list

  def get_all_listname(self, ml=None):
    """
    Return the names of the music-lists
    """
    return self.music_list_names

  @classmethod
  def get_raw_music_list(cls, music_item):
    """
    Generate a raw list of music from the given musiclist-tree
    """
    if isinstance(music_item, dict):
      for value in music_item.get("list"):
        for subvalue in cls.get_raw_music_list(value):
          yield subvalue
    else:
      yield music_item

  def find_musiclist(self, plname: str):
    def rec_search(plname, ml=None):
      if len(plname) == 0:
        return self.get_all_lists()

      ml = self.music_list if ml is None else ml
      if ml.get("name") == plname:
        return ml
      else:
        for i in ml.get("list"):
          if isinstance(i, dict):
            target = rec_search(plname, i)
            if target is not None:
              return target
    target = rec_search(plname)
    if target is None:
      raise ValueError("Could not find playlist: %s" % plname)
    return target
