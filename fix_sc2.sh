doc="
https://www.reddit.com/r/wine_gaming/comments/bzr2gu/lutris_dxvk_uses_wrong_gpu/
https://www.reddit.com/r/wine_gaming/comments/azyuwz/elite_dangerous_is_using_the_wrong_gpu_with_proton/
https://github.com/doitsujin/dxvk/issues/534
"

lspci | grep GeForce

export DXVK_FILTER_DEVICE_NAME="GeForce RTX 3090"
DXVK_FILTER_DEVICE_NAME="GeForce RTX 3090" lutris
