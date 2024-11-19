#!/usr/bin/env python3

import prompt_toolkit.completion as pmtcomp

import player as pl
import sys
import re

help_msg = """
  A Simple, Easy-To-Use Filesystem-based Music Player.
  Let's assume you have a music dir looks like this:
    Music:
    ---SubMusicDir1:
    ------1.mp3
    ------2.mp3
    ------SubMusicDir2:
    ---------3.mp3
  If you select a sub music dir like SubMusicDir1, then all the music in
  this directory will be recursively added to the playlist, your playlist
  is going to be like this:
    1.mp3
    2.mp3
    3.mp3

NOTE:
  Before you start this program, you'll need to replace the music catalog
  specified in the musiclist.py with your own.
Commands:
  help:                 Print help message like this.
  use ${musiclist-dir}: Switch to target playlist.
  loop:                 Loop a playlist that has already been selected
  next      | n:        Play the next song.
  watch     | w:        Watch part of the current playlist.
  watchall  | wa:       Watch all of the current playlist.
  append    | app:      Append a playlist to current playlist
"""

player = pl.Player()

cmd_completer = pmtcomp.NestedCompleter.from_nested_dict({
  "use":      set(player.get_all_musiclist_name()),
  "loop":     None,
  "watch":    None,
  "watch-all":None,
  "next":     None,
  "prev":     None,
  "backward": None,
  "forward":  None,
  "help":     None,
  "append":   set(player.get_all_musiclist_name()),
})

def parse_command_and_execute(command):
  """
  A simple parser that can read the action and argument from
  the command input.
  """
  for pattern, func in commands.items():
    if not re.match(pattern, command):
      continue
    return func(*(command.split(" ")[1:]))
  raise ValueError("Invalid command")

def show_help_message():
  from colorful import log, LogColor
  log(LogColor.state, help_msg)

commands = {
  "^use +":           player.init_playlist,
  "^loop$":           player.start_loop,
  "^watch-all$|^wa$": player.log_all_playlist,
  "^watch$|^w$":      player.log_part_playlist,
  "^next$|^n$":       player.play_next_music,
  "^prev$|^p$":       player.play_prev_music,
  "^help$|^h$":       show_help_message,
  "^append +|^app +": player.append_playlist,
  "^backward":        player.backward_play,
  "^forward":         player.forward_play
}
