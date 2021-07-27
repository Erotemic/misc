from os.path import exists
import ubelt as ub
import geopandas as gpd
import kwarray
import kwimage


def main():
    # https://gis.stackexchange.com/questions/254330/python-gdal-grid-correct-use
    # https://gdal.org/programs/gdal_grid.html

    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    xyz = []

    rng = kwarray.ensure_rng(432432)

    for shape in world[world['continent'] == 'Africa'].geometry:
        mpoly = kwimage.MultiPolygon.from_shapely(shape)
        for poly in mpoly.data:
            exterior = poly.data['exterior']

            for x, y in exterior.data:
                z = rng.rand()
                xyz.append((x, y, z))

    import numpy as np
    xyz = np.array(xyz)

    lines = ['x;y;d']
    for x, y, z in xyz:
        lines.append(f'{x};{y};{z}')
    text = '\n'.join(lines)

    with open('tmp.csv', 'w') as file:
        file.write(text)

    with open('tmp.vrt', 'w') as file:
        file.write(ub.codeblock(
            '''
            <OGRVRTDataSource>
                <OGRVRTLayer name="tmp">
                    <SrcDataSource>tmp.csv</SrcDataSource>
                    <SrcLayer>tmp</SrcLayer>
                    <LayerSRS>EPSG:4326</LayerSRS>
                    <GeometryType>wkbPoint</GeometryType>
                    <GeometryField encoding="PointFromColumns" x="x" y="y" z="d"/>
                </OGRVRTLayer>
            </OGRVRTDataSource>
            '''))

    minx, miny = xyz.T[0:2].min(axis=1)
    maxx, maxy = xyz.T[0:2].max(axis=1)

    lonext = maxx - minx
    latext = maxy - miny

    ar = latext / lonext
    xres = int(512)
    yres = int(xres * ar)

    command = (
        'gdal_grid '
        # '-ot Float32 -of GTiff '
        # '-zfield d '
        # '-a_srs EPSG:4326 '
        # f'-txe {minx - 1} {maxy + 1} '
        # f'-tye {miny - 1} {maxx + 1} '
        # f'-outsize {xres} {yres} '
        # '-a invdist:power=2.0:smoothing=1.0 '
        # '-a nearest:radius1=1.0:radius2=1.0 '
        # '-a linear:radius=1.0 '
        'tmp.vrt tmp.tif')

    ub.delete('tmp.tif')
    print(command)
    info = ub.cmd(command, verbose=3)

    assert info['ret'] == 0

    if exists('tmp.tif'):
        data = kwimage.imread('tmp.tif')
        print('data.shape = {!r}'.format(data.shape))
        import kwplot
        kwplot.autompl()
        kwplot.imshow(data)


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/learn/learn_gdal_grid.py
    """
    main()
