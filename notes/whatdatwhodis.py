import whatdat
import whodis
import kwcoco
import kwimage


def main():
    image_fpath = 'path/to/image.jpg'
    detector_fpath = 'path/to/detector.zip'

    # Determine the database annotation ids.
    dset = kwcoco.CocoDataset.coerce('path/to/kwcoco-dataset/data.kwcoco.json')
    aids : list[int] = list(dset.annots())

    detector = whodis.Detector.load(detector_fpath)

    imdata: np.ndarray = kwimage.imread(image_fpath)
    detections = detector.detect(imdata)

    database = whodis.ReidDataset.from_kwcoco(dset, aids)
    matches = database.query(detections)

    # Do filtering based on some criterion
    decisions = matches.filter(config={'method': 'name-score', 'threshold': 0.3})

    # not sure of the details here
    # will need to export edge information, and update the state of whatever
    # the managing datastore is.
    decisions.export()
