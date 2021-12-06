"""
Requirements:
    pip install kwarray kwimage[headless] kwplot ubelt numpy scipy
"""
import kwarray
import kwimage
import kwplot
import ubelt as ub
import numpy as np
from scipy import integrate

fpath = ub.grabdata('https://i.redd.it/ywip9sbwysy71.jpg')
data = kwimage.imread(fpath)

subdata = data[242:-22, 22:300]

img = subdata

inty = integrate.cumtrapz(img, axis=0)
intx = integrate.cumtrapz(img, axis=1)

dery = np.gradient(img, axis=0)
derx = np.gradient(img, axis=1)

der_canvas = kwarray.normalize(kwimage.stack_images([dery, derx], axis=0))
int_canvas = kwarray.normalize(kwimage.stack_images([inty, intx], axis=0))
der_canvas = kwimage.ensure_uint255(der_canvas)
int_canvas = kwimage.ensure_uint255(int_canvas)

der_canvas = kwimage.draw_header_text(der_canvas, 'derivative', color='white')
int_canvas = kwimage.draw_header_text(int_canvas, 'antiderivative', color='white')

canvas = kwimage.stack_images([der_canvas, int_canvas], axis=1)

# kwimage.imwrite('ftfy.jpg', canvas)

kwplot.autompl()
kwplot.imshow(canvas)
