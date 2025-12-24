# Find the SC2 directory:
#
fd StarCraft "$HOME"/.steam | grep "Documents/StarCraft II"
fd StarCraft "$HOME"/.steam | grep "1353877"

python -c "if 1:
    import os
    import pathlib
    steam_dpath = pathlib.Path('~/.steam').expanduser()
    for r, ds, fs in os.walk(steam_dpath):
        r = pathlib.Path(r)
        if 'StarCraft II' in ds:
            print(r)
"


#tree "$HOME/.local/share/Steam/steamapps/compatdata/3733590677/pfx/drive_c/ProgramData/Microsoft/Windows/Start Menu/Programs/StarCraft II/"
"$HOME/.local/share/Steam/steamapps/compatdata/3733590677/pfx/drive_c/users/steamuser/Documents/StarCraft II/Accounts/1353877/Hotkeys/"


$HOME/".steam/debian-installation/steamapps/compatdata/2341778848/pfx/drive_c/users/steamuser/Documents/StarCraft II/Accounts/1353877/Hotkeys/ErotemicFleetKeys.SC2Hotkeys"
$HOME/".steam/debian-installation/steamapps/compatdata/2341778848/pfx/drive_c/users/steamuser/Documents/StarCraft II/Accounts/1353877/Hotkeys/DefaultHotkeys.SC2Hotkeys"

cd /home/joncrall/misc/data/ErotemicFleetKeys.SC2Hotkeys "$HOME/.local/share/Steam/steamapps/compatdata/3733590677/pfx/drive_c/users/steamuser/Documents/StarCraft II/Accounts/1353877/Hotkeys/"


