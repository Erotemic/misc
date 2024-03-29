import kwplot
import numpy as np
import matplotlib as mpl


def plot_searchsorted_visualization(array, values, side='left', ax=None):
    array_yloc = 1
    value_yloc = 0

    colors = {
        'array': 'darkblue',
        'values': 'orange',
        'association': 'purple',
    }

    array_segment = [(x, array_yloc) for x in array]
    value_segment = [(x, value_yloc) for x in values]

    array_next_pos = [array[-1] + 1, array_yloc]

    found_idxs = np.searchsorted(array, values, side=side)

    found_association_segments = []
    for value_idx, array_idx in enumerate(found_idxs):
        if array_idx == len(array_segment):
            array_pt = array_next_pos
        else:
            array_pt = array_segment[array_idx]
        found_association_segments.append([
            array_pt,
            value_segment[value_idx],
        ])

    circles = [mpl.patches.Circle(xy, radius=0.1) for xy in array_segment]
    data_points = mpl.collections.PatchCollection(circles, color=colors['array'], alpha=0.7)
    data_lines = mpl.collections.LineCollection([array_segment], color=colors['array'], alpha=0.5)
    ax.add_collection(data_lines)
    ax.add_collection(data_points)

    circles = [mpl.patches.Circle(xy, radius=0.1) for xy in value_segment]
    data_points = mpl.collections.PatchCollection(circles, color=colors['values'], alpha=0.7)
    data_lines = mpl.collections.LineCollection([value_segment], color=colors['values'], alpha=0.5)
    ax.add_collection(data_lines)
    ax.add_collection(data_points)

    found_association_lines = mpl.collections.LineCollection(found_association_segments, color=colors['association'], alpha=0.5)
    ax.add_collection(found_association_lines)

    ax.autoscale_view()
    ax.set_aspect('equal')

    kwplot.phantom_legend(colors)

    ax.set_ylim(-1, 2)


def main():
    sns = kwplot.autosns()  # NOQA
    plt = kwplot.autoplt()  # NOQA

    if 1:
        array = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        values = [-1, 0, 1, 4, 6, 6.1, 6.5, 7, 10.3, 10.5, 10.7, 15, 16]

    if 0:
        array = np.linspace(0, 30)
        values = np.linspace(0, 30)

    if 0:
        xscale = 20
        num = 20
        array = np.array(sorted(np.random.rand(num) * xscale)).round()
        values = np.hstack([np.unique(np.random.choice(array, 3)), np.random.rand(num // 2) * xscale])

    fig = kwplot.figure(fnum=1, doclf=1, pnum=(2, 1, 1))
    ax = fig.gca()
    plot_searchsorted_visualization(array, values, side='left', ax=ax)
    ax.set_title('association = searchsorted(array, values, side=left)')

    fig = kwplot.figure(fnum=1, doclf=0, pnum=(2, 1, 2))
    ax = fig.gca()
    plot_searchsorted_visualization(array, values, side='right', ax=ax)
    ax.set_title('association = searchsorted(array, values, side=right)')

    import ubelt as ub
    fig.suptitle(ub.codeblock(
        '''
        Notice:
        side=left and side=right have the same result
        except when the value is already in the array.
        '''))

    if 1:
        pnum_ = kwplot.PlotNums(nRows=3, nCols=2)
        fig = kwplot.figure(fnum=2, doclf=1, pnum=pnum_[0])
        fig.suptitle(ub.codeblock('''Cases:'''))

        array = [0, 1, 2]
        values = [2]
        fig = kwplot.figure(fnum=2, doclf=0, pnum=pnum_())
        plot_searchsorted_visualization(array, values, side='left', ax=fig.gca())
        fig.gca().set_title('left')
        fig = kwplot.figure(fnum=2, doclf=0, pnum=pnum_())
        plot_searchsorted_visualization(array, values, side='right', ax=fig.gca())
        fig.gca().set_title('right')

        array = [0, 1, 2]
        values = [2.5]
        fig = kwplot.figure(fnum=2, doclf=0, pnum=pnum_())
        plot_searchsorted_visualization(array, values, side='left', ax=fig.gca())
        fig.gca().set_title('left')
        fig = kwplot.figure(fnum=2, doclf=0, pnum=pnum_())
        plot_searchsorted_visualization(array, values, side='right', ax=fig.gca())
        fig.gca().set_title('right')

        array = [1, 2]
        values = [0.5]
        fig = kwplot.figure(fnum=2, doclf=0, pnum=pnum_())
        plot_searchsorted_visualization(array, values, side='left', ax=fig.gca())
        fig.gca().set_title('left')
        fig = kwplot.figure(fnum=2, doclf=0, pnum=pnum_())
        plot_searchsorted_visualization(array, values, side='right', ax=fig.gca())
        fig.gca().set_title('right')

    plt.show()

if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/learn/viz_searchsorted.py
    """
    main()
