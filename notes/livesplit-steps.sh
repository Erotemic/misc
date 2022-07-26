#https://one.livesplit.org/

#https://github.com/CryZe/obs-livesplit-one


# 16 Star Timer
# https://one.livesplit.org/#/splits-io/u9


mkdir -p ~/tmp/lso-setup
cd ~/tmp/lso-setup
wget https://github.com/CryZe/obs-livesplit-one/releases/download/v0.2.0/obs-livesplit-one-v0.2.0-x86_64-unknown-linux-gnu.tar.gz

mkdir -p "$HOME"/.config/obs-studio/plugins
sudo apt install libobs-dev
tar -zxvf obs-livesplit-one-*-x86_64-unknown-linux-gnu.tar.gz -C "$HOME"/.config/obs-studio/plugins/

# https://github.com/christofsteel/pyautosplit
# OBS works well enough

git clone https://github.com/Toufool/Auto-Split.git
