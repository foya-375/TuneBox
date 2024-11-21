#!/usr/bin/env python3

import os
import time
import subprocess
import functools
import threading
import prompt_toolkit as pmt

import musiclist as ml
from colorful import LogColor, log, log_listing
from configure import root_music_path

class Player:
  __musics = ml.MusicList(root_music_path)

  def __init__(self):
    self.playing_index = 0
    self.is_looping    = False
    self.play_prog     = None
    self.playlist      = []

    self.start_time    = None
    self.forward_times = 0 # positive=forward, negative=backward

    self.playlist_opt_lock = threading.Lock()

  @classmethod
  def get_all_musiclist_name(cls):
    return cls.__musics.get_all_listname()

  def _play(self, music: os.path, start_second: float = 0):
    """
    Open a subprocess to play the music within thread, a handler is given to switch music on end of playing
    """
    def play_music_in_thread():
      self.play_prog = subprocess.Popen(["ffplay", "-ss", str(start_second), "-nodisp", "-autoexit", music],
                                        stdin=subprocess.DEVNULL,
                                        stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL)
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

    # initialize the timestamps that would be used for future playing forward or backward
    self.start_time = time.time()
    self.forward_times = 0

    self._play(self.playlist[self.playing_index])
    log(LogColor.playing, "Playing {}...".format(os.path.basename(self.playlist[self.playing_index])))

  def _log_playlist(self, log_all: bool=False):
    # Currently we just log 5 musics begin with the playing music if you want to log part part of the playlist
    if len(self.playlist) < 5:
      log_all = True
    iterator = range(len(self.playlist)) if log_all else \
               range(self.playing_index, min(len(self.playlist), self.playing_index + 5))
    for i in iterator:
      log_listing(os.path.basename(self.playlist[i]),
                  self.is_music_playing() and i == self.playing_index)
    if not log_all:
      log(LogColor.listing, "...")

  def stop_playing(self):
    if self.is_music_playing():
      try:
        self.play_prog.kill()
      except Exception:
        pass
      finally:
        self.play_prog = None

  def stop_playing_before_call(func):
    """
    A decorator that stops the player before a function is called
    """
    @functools.wraps(func)
    def wrapper_stop(self, *args, **kwargs):
      if self.is_music_playing():
        self.stop_playing()
      return func(self, *args, **kwargs)
    return wrapper_stop

  @stop_playing_before_call
  def start_loop(self):
    """
    If there is music playing, just kill it and start a new loop
    """
    if len(self.playlist) == 0:
      log(LogColor.state, "Please specify a playlist using 'use' before playing")
    else:
      self.is_looping = True
      return self.loop_handler()

  @stop_playing_before_call
  def play_next_music(self):
    self.get_next_music()
    self.start_loop()

  @stop_playing_before_call
  def play_prev_music(self):
    self.get_prev_music()
    self.start_loop()

  def get_current_time(self):
    """
    Return the playing time of the current playing music, if there is no music playing,
    return -1 instead
    """
    if not self.is_music_playing():
      return -1
    return max(0, time.time() - self.start_time + self.forward_times * 10)

  def time_switcher(swicher_func):
    """
    Decorator for forwarding and backwarding, just get the current time, then stop the player,
    execute the forwarding/backwarding function and then log.
    """
    @functools.wraps(swicher_func)
    def wrapper(self, *args, **kwargs):
      current_time = self.get_current_time()
      if current_time < 0:
        return
      self.stop_playing()
      swicher_func(self, current_time, *args, **kwargs)
      time.sleep(0.01) # make sure the thread is already started and the logging is correct.
      log(LogColor.state, "Now you are at time: {}s".format(self.get_current_time()))
      return swicher_func
    return wrapper

  @time_switcher
  def backward_play(self, current_time):
    self.forward_times -= 1
    self._play(music=self.playlist[self.playing_index], start_second=(current_time - 10))

  @time_switcher
  def forward_play(self, current_time):
    self.forward_times += 1
    self._play(music=self.playlist[self.playing_index], start_second=(current_time + 10))

  def get_playlist(self):
    return self.playlist

  def is_music_playing(self) -> bool:
    return self.play_prog is not None

  def get_next_music(self):
    with self.playlist_opt_lock:
      self.playing_index = (self.playing_index + 1) % len(self.playlist)

  def get_prev_music(self):
    with self.playlist_opt_lock:
      self.playing_index = (self.playing_index - 1 + len(self.playlist)) % len(self.playlist)

  def get_playlist_by_name(self, playlist_name):
    return list(
      filter(
        lambda item: item is not None,
        ml.MusicList.get_raw_music_list(self.__musics.find_musiclist(playlist_name))
      )
    )

  @stop_playing_before_call
  def init_playlist(self, playlist_name):
    """
    Initialize the playlist and kill the subprocess that is playing
    """
    try:
      self.playlist = self.get_playlist_by_name(playlist_name)
      self.playing_index = 0
      log(LogColor.state, "Already switched to playlist: {}.".format(os.path.basename(playlist_name)))
    except Exception as err:
      log(LogColor.emphasize, err)

  def append_playlist(self, playlist_name):
    """
    Append a playlist to current playlist, this does not stop the playing music.
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

  @stop_playing_before_call
  def terminate_for_exit(self):
    # Simply stop the playing thread for exiting the program
    pass
