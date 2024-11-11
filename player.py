#!/usr/bin/env python3

import os
import subprocess
import threading
import prompt_toolkit as pmt

import musiclist as ml
from colorful import LogColor, log, log_listing

class Player:
  __musics = ml.MusicList("/home/foya/music")

  def __init__(self):
    self.playing_index = 0
    self.is_looping    = False
    self.play_prog     = None
    self.playlist      = []

    self.playlist_opt_lock = threading.Lock()

  @classmethod
  def get_all_musiclist_name(cls):
    return cls.__musics.get_all_listname()

  def _play(self, music: os.path):
    """
    Open a subprocess to play the music within thread, a handler is given to switch music on end of playing
    """
    def play_music_in_thread():
      self.play_prog = subprocess.Popen(["ffplay", "-nodisp", "-autoexit", music],
                                           stdin=subprocess.DEVNULL,
                                           stdout=subprocess.DEVNULL,
                                           stderr=subprocess.DEVNULL)
      log(LogColor.playing, "Playing {}...".format(os.path.basename(music)))
      self.play_prog.wait()
      if self.is_looping and self.play_prog and self.play_prog.returncode == 0:
        self.play_prog = None
        self.get_next_music()
        self.loop_handler()

    thread = threading.Thread(target=play_music_in_thread)
    thread.start()

  def loop_handler(self):
    """
    A handler function for music looping, this function gets a infinitly music loop
    """
    if self.is_music_playing() or not self.is_looping:
      return
    self._play(self.playlist[self.playing_index])

  def _log_playlist(self, log_all: bool=False):
    if len(self.playlist) < 5:
      log_all = True
    iterator = range(len(self.playlist)) if log_all else \
               range(self.playing_index, min(len(self.playlist), self.playing_index + 5))
    for i in iterator:
      log_listing(os.path.basename(self.playlist[i]),
                  self.is_music_playing() and i == self.playing_index)
    if not log_all:
      log(LogColor.listing, "...")

  def start_loop(self):
    """
    If there is music playing, just kill it and start a new loop
    """
    if self.is_music_playing():
      self.stop_playing()
    self.is_looping = True
    return self.loop_handler()

  def stop_playing(self):
    if self.is_music_playing():
      try:
        self.play_prog.kill()
      except Exception:
        pass
      finally:
        self.play_prog = None

  def play_next_music(self):
    if self.is_music_playing():
      self.stop_playing()
    self.get_next_music()
    self.start_loop()

  def get_playlist(self):
    return self.playlist

  def is_music_playing(self) -> bool:
    return self.play_prog is not None

  def get_next_music(self):
    with self.playlist_opt_lock:
      if self.playing_index + 1 < len(self.playlist):
        self.playing_index += 1
      else:
        self.playing_index = 0

  def get_playlist_by_name(self, playlist_name):
    return list(
      filter(
        lambda item: item is not None,
        ml.MusicList.get_raw_music_list(self.__musics.find_musiclist(playlist_name))
      )
    )

  def init_playlist(self, playlist_name):
    """
    Initialize the playlist and kill the subprocess that is playing
    """
    try:
      self.playlist = self.get_playlist_by_name(playlist_name)
      self.playing_index = 0
      if self.is_music_playing():
        self.stop_playing()
      log(LogColor.state, "Already switched to playlist: {}.".format(os.path.basename(playlist_name)))
    except Exception as err:
      log(LogColor.emphasize, err)

  def append_playlist(self, playlist_name):
    """
    Append a playlist to current playlist
    """
    try:
      self.playlist.extend(self.get_playlist_by_name(playlist_name))
      self.playlist = list(dict.fromkeys(self.playlist)) # remove duplicates
    except Exception as err:
      log(LogColor.emphasize, err)

  def log_all_playlist(self):
    self._log_playlist(True)

  def log_part_playlist(self):
    self._log_playlist(False)
