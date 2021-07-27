

def main():
    """
    Demo using gdal_grid

    References:
        https://gis.stackexchange.com/questions/254330/python-gdal-grid-correct-use
        https://gdal.org/programs/gdal_grid.html

    """
    from os.path import exists
    import ubelt as ub
    import geopandas as gpd
    import numpy as np

    # Generate Demo Data Ungridded data
    # Generate a random value at points along the African continent
    xyz = []
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    rng = np.random.RandomState(0)
    for shape in world[world['continent'] == 'Africa'].geometry:
        if shape.type == 'MultiPolygon':
            for geom in shape.geoms:
                for x, y in geom.exterior.coords:
                    z = rng.rand()
                    xyz.append((x, y, z))
        elif shape.type == 'Polygon':
            for x, y in shape.exterior.coords:
                z = rng.rand()
                xyz.append((x, y, z))
    xyz = np.array(xyz)

    # Write the demo data to a CSV file
    lines = ['x;y;d']
    for x, y, z in xyz:
        lines.append(f'{x};{y};{z}')
    text = '\n'.join(lines)
    with open('tmp.csv', 'w') as file:
        file.write(text)

    # I was unable to get the command to work with the CSV file alone
    # I needed to create a VRT that pointed at the CVS file.
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

    # Can modify these but they are not needed
    minx, miny = xyz.T[0:2].min(axis=1)
    maxx, maxy = xyz.T[0:2].max(axis=1)
    lonext = maxx - minx
    latext = maxy - miny
    ar = latext / lonext
    xres = int(512)
    yres = int(xres * ar)

    # Call the GDAL Grid command
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
        # Show the result if it worked
        import tifffile
        data = tifffile.imread('tmp.tif')
        from matplotlib import pyplot as plt
        print('data.shape = {!r}'.format(data.shape))
        plt.imshow(data)


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/learn/learn_gdal_grid.py
    """
    main()
