Requires:

+ to install try:

% sudo pip install --install-option="--install-purelib=/usr/lib/python2.7/site-packages" --ignore-installed weechat_notifier

so the library gets into the python 2.7 site-packages as weechat uses
python 2.x not 3.x.

+ External Dependencies:

++ libnotify

  such that shell commands like: 
   
  notify-send -h string:bgcolor:#ff0000 -h string:fgcolor:#ff444 'Hello world!' 'This is an example notification.' --icon=dialog-information
   
  would work.

++ play

  uses linux 'play' command to play sounds.

