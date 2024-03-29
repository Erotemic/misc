__doc__="
Lutris has a hard time figuring out the 3090, so need this custom CLI to run
Starcraft 2
grep keywords: sc2 SC2

https://www.reddit.com/r/wine_gaming/comments/bzr2gu/lutris_dxvk_uses_wrong_gpu/
https://www.reddit.com/r/wine_gaming/comments/azyuwz/elite_dangerous_is_using_the_wrong_gpu_with_proton/
https://github.com/doitsujin/dxvk/issues/534


# Requires this patch as of 2023, not sure why
# https://github.com/lutris/lutris/commit/072e72a4aefd91101b79dd05d8ce9f100a4b6b0c
https://forums.lutris.net/t/all-games-stuck-on-launching/14749/1
"

lspci | grep GeForce

export DXVK_FILTER_DEVICE_NAME="GeForce RTX 3090"
#DXVK_FILTER_DEVICE_NAME="GeForce RTX 3090" lutris
DXVK_FILTER_DEVICE_NAME="GeForce RTX 3090" lutris -d
