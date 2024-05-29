import ubelt as ub
import networkx as nx
from graphid import util
import xdev
import kwplot
kwplot.autompl()

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
xinspect
xdoctest
geowatch
kwcoco
kwimage
kwimage_ext
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
bioharn
ndsampler
delayed_image
shitspotter
scriptconfig
cmd_queue
pypogo
xcookie
sm64-random-assets
line_profiler
mathutf
networkx_algo_common_subtree
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
bioharn netharn
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


def parse_requirements(fname="requirements.txt", versions=False):
    """
    Parse the package dependencies listed in a requirements file but strips
    specific versioning information.

    Args:
        fname (str): path to requirements file
        versions (bool | str, default=False):
            If true include version specs.
            If strict, then pin to the minimum version.

    Returns:
        List[str]: list of requirements items

    CommandLine:
        python -c "import setup, ubelt; print(ubelt.urepr(setup.parse_requirements()))"
    """
    from os.path import exists, dirname, join
    import re
    require_fpath = fname

    def parse_line(line, dpath=""):
        """
        Parse information from a line in a requirements text file

        line = 'git+https://a.com/somedep@sometag#egg=SomeDep'
        line = '-e git+https://a.com/somedep@sometag#egg=SomeDep'
        """
        # Remove inline comments
        comment_pos = line.find(" #")
        if comment_pos > -1:
            line = line[:comment_pos]

        if line.startswith("-r "):
            # Allow specifying requirements in other files
            target = join(dpath, line.split(" ")[1])
            for info in parse_require_file(target):
                yield info
        else:
            # See: https://www.python.org/dev/peps/pep-0508/
            info = {"line": line}
            if line.startswith("-e "):
                info["package"] = line.split("#egg=")[1]
            else:
                if "--find-links" in line:
                    # setuptools doesnt seem to handle find links
                    line = line.split("--find-links")[0]
                if ";" in line:
                    pkgpart, platpart = line.split(";")
                    # Handle platform specific dependencies
                    # setuptools.readthedocs.io/en/latest/setuptools.html
                    # #declaring-platform-specific-dependencies
                    plat_deps = platpart.strip()
                    info["platform_deps"] = plat_deps
                else:
                    pkgpart = line
                    platpart = None

                # Remove versioning from the package
                pat = "(" + "|".join([">=", "==", ">"]) + ")"
                parts = re.split(pat, pkgpart, maxsplit=1)
                parts = [p.strip() for p in parts]

                info["package"] = parts[0]
                if len(parts) > 1:
                    op, rest = parts[1:]
                    version = rest  # NOQA
                    info["version"] = (op, version)
            yield info

    def parse_require_file(fpath):
        dpath = dirname(fpath)
        with open(fpath, "r") as f:
            for line in f.readlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    for info in parse_line(line, dpath=dpath):
                        yield info

    def gen_packages_items():
        if exists(require_fpath):
            for info in parse_require_file(require_fpath):
                yield info

    packages = list(gen_packages_items())
    return packages


def find_real_dependency_edges(pkgname, nodes=None):
    import ubelt as ub
    dpath = ub.Path(f'$HOME/code/{pkgname}').expand()
    edges = []
    if not dpath.exists():
        print('{dpath=} does not exist')
    else:
        req_dpath = dpath / 'requirements'
        if not req_dpath.exists():
            print(f'{req_dpath=} does not exist')

        run_fpath = dpath / 'requirements/runtime.txt'
        if not run_fpath.exists():
            print(f'{run_fpath=} does not exist')

        for info in parse_requirements(run_fpath):
            if nodes is None or info['package'] in nodes:
                edges.append((pkgname, info['package'], {'type': 'runtime'}))

        if 1:
            run_fpath = dpath / 'requirements/tests.txt'
            if not run_fpath.exists():
                print(f'{run_fpath=} does not exist')

            for info in parse_requirements(run_fpath):
                if nodes is None or info['package'] in nodes:
                    edges.append((pkgname, info['package'], {'type': 'test'}))

        if 1:
            run_fpath = dpath / 'requirements/optional.txt'
            if not run_fpath.exists():
                print(f'{run_fpath=} does not exist')

            for info in parse_requirements(run_fpath):
                if nodes is None or info['package'] in nodes:
                    edges.append((pkgname, info['package'], {'type': 'optional'}))
    return edges


real_edges = list(ub.flatten([list(find_real_dependency_edges(pkgname, nodes)) for pkgname in nodes]))

graph = nx.DiGraph()
graph.add_nodes_from(nodes)
graph.add_edges_from(causedby_edges)

# nx.write_network_text(graph)
util.util_graphviz.dump_nx_ondisk(graph, 'crall_pkgs_causal.png')
xdev.startfile('crall_pkgs_causal.png')

# print('Reverse')
# nx.write_network_text(graph.reverse())

# import kwplot
# kwplot.autompl()
# nx.draw_networkx(graph)

# util.show_nx(graph)


graph2 = nx.DiGraph()
graph2.add_nodes_from(nodes)
graph2.add_edges_from(dependency_edges)

# nx.write_network_text(graph2)

# kwplot.figure(fnum=1, doclf=1)
# util.show_nx(nx.transitive_reduction(graph2.reverse()), fnum=1)
util.util_graphviz.dump_nx_ondisk(graph2.reverse(), 'crall_pkgs_dependencies.png')


graph3 = nx.DiGraph()
graph3.add_nodes_from(nodes)
graph3.add_edges_from(real_edges)

# nx.write_network_text(graph3)

# kwplot.figure(fnum=1, doclf=1)
graph3t = nx.transitive_reduction(graph3.reverse())
util.util_graphviz.dump_nx_ondisk(graph3t, 'crall_pkgs_dependencies_full.png')
xdev.startfile('crall_pkgs_dependencies_full.png')


graph3_opt = graph3.copy()
graph3_opt.remove_edges_from([(u, v) for u, v, d in graph3_opt.edges(data=True) if d['type'] == 'test'])
graph3t = nx.transitive_reduction(graph3_opt.reverse())
util.util_graphviz.dump_nx_ondisk(graph3t, 'crall_pkgs_dependencies_opt.png')
xdev.startfile('crall_pkgs_dependencies_opt.png')


graph3_opt = graph3.copy()
graph3_opt.remove_edges_from([(u, v) for u, v, d in graph3.edges(data=True) if d['type'] != 'runtime'])
graph3t = nx.transitive_reduction(graph3_opt.reverse())
util.util_graphviz.dump_nx_ondisk(graph3t, 'crall_pkgs_dependencies_min.png')
xdev.startfile('crall_pkgs_dependencies_min.png')


with_extern_real_edges = list(ub.flatten([list(find_real_dependency_edges(pkgname, None)) for pkgname in nodes]))
graph4 = nx.DiGraph()
graph4.add_nodes_from(nodes)
graph4.add_edges_from(with_extern_real_edges)

util.util_graphviz.dump_nx_ondisk(graph4.reverse(), 'crall_extern_pkgs_dependencies_fulll.png')
xdev.startfile('crall_extern_pkgs_dependencies_fulll.png')


with_extern_real_edges = list(ub.flatten([list(find_real_dependency_edges(pkgname, None)) for pkgname in nodes]))
contrib = {
    'torch',
    'mmdet',
    'networkx',
    'cibuildwheel',
    'dvc',
    'pandas',
    'scikit-build',
    'scikit-learn',
    'scikit-image',
    'distinctipy',
    'MONAI',
    'openskill',
}
extended_nodes = set(nodes) | contrib
with_extern_contrib_real_edges = [(u, v, d) for u, v, d in with_extern_real_edges if v in extended_nodes]
graph4 = nx.DiGraph()
graph4.add_nodes_from(extended_nodes)
graph4.add_edges_from(with_extern_contrib_real_edges)

util.util_graphviz.dump_nx_ondisk(graph4.reverse(), 'crall_extern_contrib_pkgs_dependencies_full.png')
xdev.startfile('crall_extern_contrib_pkgs_dependencies_full.png')
