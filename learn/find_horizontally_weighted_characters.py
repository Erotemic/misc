"""
References:
    https://www.python.org/dev/peps/pep-3131/
    https://docs.python.org/3/reference/lexical_analysis.html#identifiers
"""
import numpy as np


def render_glyph(unicode_text):
    """
    Render a unicode character on an image canvas

    References:
        https://stackoverflow.com/questions/18942605/how-to-use-unicode-characters-with-pil
    """
    from PIL import Image, ImageDraw, ImageFont
    font_size = 36
    width = 64
    height = 64
    back_ground_color = (0, 0, 0)
    font_size = 36
    font_color = (255, 255, 255)

    im  =  Image.new("RGB", (width, height), back_ground_color )
    draw  =  ImageDraw.Draw( im )
    unicode_font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    draw.text((10, 10), unicode_text, font=unicode_font, fill=font_color)
    data = np.asarray(im).sum(axis=2)
    return data


def unicode_feature(unicode_text):
    """
    Measure visual unicode features
    """
    data = render_glyph(unicode_text)
    feature = {
        'vdev': data.std(axis=1).sum(),
        'hdev': data.std(axis=0).sum(),
    }
    return feature


def generate_unicode_characters():
    """
    Generates all possible unicode characaters

    References:
        https://stackoverflow.com/questions/1477294/generate-random-utf-8
    """
    max_val = 0x110000
    for int_ in range(32, max_val):
        chr_ = chr(int_)
        if chr_.isprintable():
            yield chr_


def find_horizontally_weighted_unicode_characters():
    for cand in generate_unicode_characters():
        # Only consider characters that could be used as a variable
        if cand.isidentifier():
            # Measure visual features of this unicode character
            feature = unicode_feature(cand)
            # If it is horizontally weighted, print it as a candiate
            if feature['hdev'] > feature['vdev'] * 1.4:
                print(f'cand = {repr(cand)} - {str(feature)}')
