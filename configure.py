#!/usr/bin/env python3

"""
Simple implementation of config-file parsing, the default location of the config file
is "~/.tuneboxrc.ini", you can modify it by variable "configure_filename"
"""

from prompt_toolkit import prompt, HTML

import os
import configparser

__all__ = ["root_music_path"]

msg_dict = {
  "error_on_config": "An error occured when parsing config:\n\t{}\nre-configuring...",
  "path_invalid":    "The path:{} is invalid, please choose another path",
  "config_prompt":    "<ansigreen>Root music path:</ansigreen> "
}

conf = configparser.ConfigParser()
configure_filename = os.path.join(os.path.expanduser("~"), ".tuneboxrc.ini")

root_music_path = None

try:
  conf.read_file(open(configure_filename, encoding="utf-8"))
  root_music_path = conf["tunebox_conf_root"]["root_dir"]
  os.access(root_music_path, os.R_OK)

except Exception as err:
  from colorful import log, LogColor
  from prompt_toolkit.completion.filesystem import PathCompleter
  from prompt_toolkit.completion import FuzzyCompleter

  log(LogColor.emphasize, msg_dict.get("error_on_config").format(err))

  while True:
    root_music_path = prompt(HTML(msg_dict.get("config_prompt")),
                             completer=FuzzyCompleter(PathCompleter(only_directories=True)))
    if len(root_music_path) == 0:
      continue
    if os.path.isdir(root_music_path):
      conf["tunebox_conf_root"] = {"root_dir": root_music_path}
      with open(configure_filename, "w", encoding="utf-8") as file:
        conf.write(file)
      break
    log(LogColor.emphasize, msg_dict.get("path_invalid").format(root_music_path))
