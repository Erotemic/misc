import networkx as nx

nodes = [p.strip() for p in """
utool
ibeis
vtool_ibeis
dtool_ibeis
plottool_ibeis
guitool_ibeis
ubelt
hotspotter
xdev
xdoctest
geowatch
kwcoco
kwarray
kwplot
liberator
torch_liberator
vimtk
timerit
progiter
pyhesaff
pyflann_ibeis
kwutil
git_well
netharn
ndsampler
delayed_image
shitspotter
scriptconfig
cmd_queue
""".strip().split(chr(10)) if p.strip()]


# Caused to exist
causedby_edges = [p.strip().split(' ') for p in """
hotspotter ibeis

ibeis utool
ibeis vtool_ibeis
ibeis dtool_ibeis
ibeis plottool_ibeis
ibeis guitool_ibeis
ibeis pyhesaff
ibeis pyflann_ibeis
ibeis graphid

utool ubelt
utool xdev
utool xdoctest
utool mkinit
utool vimtk
utool timerit
utool progiter

geowatch shitspotter
geowatch scriptconfig
geowatch cmd_queue
geowatch delayed_image
geowatch torch_liberator

netharn kwarray
netharn kwimage
netharn kwcoco
netharn ndsampler
netharn torch_liberator
netharn scriptconfig
ndsampler kwcoco
ndsampler delayed_image

xdev kwutil
ubelt kwutil
geowatch kwutil

netharn torch_liberator
torch_liberator liberator
torch_liberator networkx_algo_common_subtree

vtool_ibeis kwarray
vtool_ibeis kwimage
plottool_ibeis kwplot

kwcoco geowatch
""".strip().split(chr(10)) if p.strip()]


dependency_edges = [p.strip().split(' ') for p in """
utool ubelt

dtool_ibeis utool
dtool_ibeis ubelt

vtool_ibeis utool
vtool_ibeis ubelt

guitool_ibeis utool
guitool_ibeis ubelt
guitool_ibeis vtool_ibeis

plottool_ibeis utool
plottool_ibeis vtool_ibeis
plottool_ibeis guitool_ibeis

graphid ubelt

pyhesaff ubelt

ibeis utool
ibeis vtool_ibeis
ibeis dtool_ibeis
ibeis plottool_ibeis
ibeis guitool_ibeis
ibeis pyhesaff
ibeis pyflann_ibeis
ibeis graphid
ibeis ubelt

xdev ubelt
xdev scriptconfig

netharn kwcoco
netharn kwimage
netharn kwarray
netharn kwplot
netharn ndsampler

kwarray ubelt

kwimage ubelt
kwimage kwarray

kwplot ubelt
kwplot kwimage

kwcoco ubelt
kwcoco scriptconfig
kwcoco kwarray
kwcoco kwplot
kwcoco kwimage
kwcoco delayed_image

ndsampler kwcoco

kwutil ubelt
kwutil progiter

scriptconfig ubelt

shitspotter geowatch

cmd_queue ubelt

delayed_image kwimage

geowatch scriptconfig
geowatch ubelt
geowatch kwarray
geowatch kwimage
geowatch kwcoco
geowatch cmd_queue
geowatch kwutil
geowatch delayed_image

git_well ubelt
git_well scriptconfig

liberator ubelt
torch_liberator liberator
torch_liberator networkx_algo_common_subtree
""".strip().split(chr(10)) if p.strip()]

graph = nx.DiGraph()
graph.add_nodes_from(nodes)
graph.add_edges_from(causedby_edges)

nx.write_network_text(graph)

# print('Reverse')
# nx.write_network_text(graph.reverse())

# import kwplot
# kwplot.autompl()
# nx.draw_networkx(graph)

from graphid import util
# util.show_nx(graph)


graph2 = nx.DiGraph()
graph2.add_nodes_from(nodes)
graph2.add_edges_from(dependency_edges)

nx.write_network_text(graph2)

import kwplot
kwplot.autompl()
kwplot.figure(fnum=1, doclf=1)
# util.show_nx(nx.transitive_reduction(graph2.reverse()), fnum=1)
from graphid import util
util.util_graphviz.dump_nx_ondisk(graph2.reverse(), 'crall_pkgs_dependencies.png')

