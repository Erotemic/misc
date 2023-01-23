import kwimage

import kwarray
rng = kwarray.ensure_rng(4432)
poly1 = kwimage.Polygon.random(n=5, convex=False, rng=rng)
poly2 = kwimage.Polygon.random(n=5, convex=False, rng=rng)
poly3 = kwimage.Polygon.random(n=5, convex=False, rng=rng)

poly1 = poly1.translate((0.3))
poly2 = poly2.translate((0.3, 0.5))
poly = poly1.union(poly2).union(poly3)

import kwplot
plt = kwplot.autoplt()
kwplot.figure(doclf=1, pnum=(1, 2, 1))

poly.draw(setlim=1, color='kitware_blue')

bigpoly = poly.scale(1.5, about='centroid')
bigpoly.draw(fill=False, border=True, edgecolor='purple', setlim=True)

plt.gca().set_title('Scaling with non-convex region')
plt.scatter(*poly.centroid, s=200, color='orange', marker='*')


kwplot.figure(pnum=(1, 2, 2))
plt.gca().set_title('Scaling with convex region')
poly.draw(setlim=1, color='kitware_blue')
cpoly = poly.convex_hull
cpoly.draw(fill=False, border=True, edgecolor='red')
big_cpoly = cpoly.scale(1.5, about='centroid')
plt.scatter(*cpoly.centroid, s=200, color='orange', marker='*')
big_cpoly.draw(fill=False, border=True, edgecolor='kitware_green', setlim=1)
