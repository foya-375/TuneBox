#!/usr/bin/env python3

from enum import Enum
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.styles import Style

class LogColor(Enum):
  state     = "<ansiyellow>%s</ansiyellow>"
  emphasize = "<ansired>%s</ansired>"
  playing   = "<ansigreen>%s</ansigreen>"
  listing   = "<ansiblue>%s</ansiblue>"

playing_style = Style.from_dict({
  "indicator":  "ansicyan",
  "music_name": "ansired underline"
})

def log(log_color: LogColor, msg):
  print_formatted_text(HTML(log_color.value % msg))

def log_listing(list_item, playing_flag: bool):
  if playing_flag:
    print_formatted_text(HTML("<indicator>-></indicator> <music_name>(%s)</music_name>" % list_item),
                         style=playing_style)
  else:
    log(LogColor.listing, list_item)
