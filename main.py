#!/usr/bin/env python3

import prompt_toolkit as pmt

import sys
import re
import command


session = pmt.PromptSession(completer=command.cmd_completer)

while True:
  try:
    inst = session.prompt(pmt.HTML("<ansicyan>Command ></ansicyan> "),
                          cursor=pmt.cursor_shapes.CursorShape.BLOCK)
  except KeyboardInterrupt:
    continue
  except EOFError:
    break
  else:
    try:
      if len(inst) > 0:
        command.parse_command_and_execute(inst)
    except Exception as err:
      print(err)
