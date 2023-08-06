Requires:

+ libnotify

  such that shell commands like: 
   
  notify-send -h string:bgcolor:#ff0000 -h string:fgcolor:#ff444 'Hello world!' 'This is an example notification.' --icon=dialog-information
   
  would work.

+ play

  uses linux 'play' command to play sounds.

Weechat uses python 2.7 so creating a virtual env for this project
with python 2.7:

    v.mk -p /usr/bin/python2 wcn

The code is python 3 code so installed 3to2 to convert to 2.x
compliant python.
