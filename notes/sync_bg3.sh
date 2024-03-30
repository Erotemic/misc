#!/bin/bash


if test -e $HOME/.local/share/Steam/steamapps ; then
    ln -s /flash/steam/steamapps "$HOME/.local/share/Steam/steamapps"
fi

TOOTHBRUSH_STEAM_ROOT=/media/joncrall/flash1/steam/steamapps
OOO_STEAM_ROOT=/flash/steam/steamapps
STEAM_ROOT=$TOOTHBRUSH_STEAM_ROOT
STEAM_ROOT=$OOO_STEAM_ROOT

DECK_LOC=".local/share/Steam/steamapps/compatdata/1086940/pfx/drive_c/users/steamuser/AppData/Local/Larian Studios/Baldur's Gate 3/PlayerProfiles/Public/Savegames/Story"

OOO_LOC="/flash/steam/steamapps/compatdata/1086940/pfx/drive_c/users/steamuser/AppData/Local/Larian Studios/Baldur's Gate 3/PlayerProfiles/Public/Savegames/"

# Between ooo / steamdeck
rsync -vrPR \
    "steamdeck:.local/share/Steam/steamapps/compatdata/1086940/pfx/drive_c/users/steamuser/AppData/Local/Larian Studios/Baldur's Gate 3/PlayerProfiles/Public/Savegames/./Story" \
    "/flash/steam/steamapps/compatdata/1086940/pfx/drive_c/users/steamuser/AppData/Local/Larian Studios/Baldur's Gate 3/PlayerProfiles/Public/Savegames/"


ls "$TOOTHBRUSH_STEAM_ROOT/compatdata/1086940/pfx/drive_c/users/steamuser/AppData/Local/Larian Studios/Baldur's Gate 3/PlayerProfiles/Public/Savegames"

# Between toothbrush / steamdeck
TOOTHBRUSH_STEAM_ROOT=/media/joncrall/flash1/steam/steamapps
rsync -vrPRn \
    "steamdeck:.local/share/Steam/steamapps/compatdata/1086940/pfx/drive_c/users/steamuser/AppData/Local/Larian Studios/Baldur's Gate 3/PlayerProfiles/Public/Savegames/./Story" \
    "$TOOTHBRUSH_STEAM_ROOT/compatdata/1086940/pfx/drive_c/users/steamuser/AppData/Local/Larian Studios/Baldur's Gate 3/PlayerProfiles/Public/Savegames/"

#steam -applaunch 1086940 --help

__doc__="

Add to launch options

SteamDeck=0 %command%
"
