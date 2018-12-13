"""
Notes:
    This is related to a [previous question][1], but is perhaps a more concise phrasing.

    I have an `N x N` image and I want to know what the minimum `σ` is that I need before I can downsample my image by a factor of two without losing any information (w.r.t the information in the blurred image).

    Here is my own attempt to think through this problem:

    Setup:

     * I have a 1D discrete signal `F`
     * I measure `F` to obtain a discrete signal `f` with N uniformly spaced samples. Lets call the distance between each sample `1u` for one unit (e.g. seconds, millimeters, pixels with a known intrinsic camera calibration).
     * The Nyquist Sampling Theorem states that the highest frequency signal that can be accurately represented in these `N` samples is `N / 2`.


    Thus,

    FREQ: cycles per u=1
    RATE: u=1 per cycle

    * Because the samples are spaced `u` units apart, this means the measurement's sampling rate is `u` and the sampling frequency is `1 / u`.
    * From the Nyquist Sampling Theorum, this means that the highest frequency accurately represented in the discrete signal is `N * u / 2`.

    WIP:

    * If we blur with a `σ`, then this attenuates higher frequencies, effectively cutting off frequencies over `something that depends on σ / u`.
    * Therefore if we choose `σ=?`, then the highset frequency that remains in the image will be `1 / (u * 4)`, which means we can capture that signal using `N / 2` samples, thus making it safe to downsample.


Example:
    if N = 512u
    Then the higest frequency representable is 512/2 = 256 cycles/u


      [1]: https://dsp.stackexchange.com/questions/52607/question-about-down-sampling-a-scale-space-representation
"""
import scipy
import scipy.ndimage
import numpy as np
import ubelt as ub


def g(f, s, **kw):
    """
    Apply a gaussian filter to an input signal

    Args:
        f (ndarray): a discretized signal in 1 or 2 dimensions
        s (float): standard deviation of the gaussian kernel.
    """
    truncate = kw.get('truncate', 6.0)  # overkill in practical cases
    if len(f.shape) == 1:
        sigma = s
    elif len(f.shape) == 3:
        sigma = (s, s, 0)
    else:
        sigma = (s, s)
    return scipy.ndimage.gaussian_filter(f, sigma=sigma,
                                         truncate=truncate)


def down(f):
    """
    Downsample a signal `f`.

    Args:
        f (ndarray): a discretized signal in 1 or 2 dimensions
    """
    if len(f.shape) == 1:
        return f[0:None:2]
    else:
        return f[0:None:2, 0:None:2]


class Signal(ub.NiceRepr):
    """
    Notes:
        The spatial frequency of the digital sampling is the reciprocal of the
        center-to-center distance between adjacent pixels.

    Notes:
        The scale parameter $t=\sigma^2$ is the variance of the Gaussian
        filter.

        The scale-space representation at scale level t=0 is the image f
        itself.

        Subsampling is a bad idea unless you have previously blurred/smoothed
        the image! (because it leads to aliasing)

        When an image is halved, applying a gaussian kernel of σ will apply as
        2σ.

        Gaussians of variance σ^2_1 and σ^2_2 results in a Gaussian of variance
        σ^2_3 = σ^2_1 + σ^2_2.

        An important detail is that the algorithm computing the scale space
        assumes that the input image ℓ(x,y) is pre-smoothed, roughly capturing
        the effect of the finite pixel size in a CCD (charge-coupled device?).
        This is modelled by assuming that the input is not ℓ(x,y), but
        ℓ(x,y,σn), where σn is a nominal smoothing, usually taken to be 0.5
        (half a pixel standard deviation). This also means that σ=σn=0.5 is the
        finest scale that can actually be computed


        According to Shannon's sampling theorem, in order to preserve the spatial
        resolution of the original image, the digitizing device must utilize a sampling
        interval that is no greater than one-half the size of the smallest resolvable
        feature of the optical image. This is equivalent to acquiring samples at twice
        the highest spatial frequency contained in the image, a reference point
        commonly referred to as the Nyquist criterion. If the Abbe limit of resolution
        in the optical image is approximately 0.22 micrometers, the digitizer must
        sample at intervals that correspond in the specimen space to 0.11 micrometers
        or less. A digitizer that samples 512 points per horizontal scan line would
        then have a maximum horizontal field of view of approximately 56 micrometers
        (512 × 0.11 micrometers). An increased number of digital samples per scan line
        or unit specimen area, which could be brought about by too great an optical
        magnification, would not yield more spatial information and the image would be
        said to be oversampled. Note that oversampling is often done intentionally to
        examine or display diffraction patterns or point spread functions, to produce a
        reduced field of view, or to acquire redundant values to ensure fidelity of the
        displayed image. In most cases, to ensure adequate sampling for high-resolution
        imaging, an interval of 2.5 to 3 samples for the smallest resolvable feature is
        desirable.
        [source](https://www.olympus-lifescience.com/en/microscope-resource/primer/java/digitalimaging/processing/samplefrequency/)


    References:
        https://en.wikipedia.org/wiki/Scale_space
        https://en.wikipedia.org/wiki/Scale_space_implementation
        https://dsp.stackexchange.com/questions/10275/creating-a-gaussian-pyramid
        http://www.montefiore.ulg.ac.be/~piater/papers/Crowley-2002-CogVis.pdf
        http://www.vlfeat.org/api/scalespace-fundamentals.html

        https://dsp.stackexchange.com/questions/31013/gaussian-pyramid-how-is-subsampling-rate-related-to-sigma

        https://www.scipy-lectures.org/intro/scipy/auto_examples/solutions/plot_image_blur.html

        https://dsp.stackexchange.com/questions/24329/downsampling-and-gaussian-filtering-in-the-context-of-scale-space-pyramids

        https://stackoverflow.com/questions/12334551/low-pass-gaussian-filter-with-a-specified-cut-off-frequency
    """
    def __init__(self, f_in, s_in, level=0, history=None):
        self.f_in = f_in
        self.s_in = s_in
        self.level = level
        if history is None:
            history = [s_in]
        # Keep track of
        self.history = history

    def __nice__(self):
        return '{}, s={:.4f}, t={:.4f}'.format(self.f.shape, self.s, self.t)

    @classmethod
    def demo(cls, N=512, C=100):
        """
        Make a dummy 1D signal
        """
        x = np.linspace(0, 1.0, N)
        f = np.zeros(N)
        # Add random frequency sin waves together to make a signal
        for i in range(C):
            w = np.random.rand() * N / 8
            f += np.sin(w * x)
        # Normalize between 0 and 1
        f = (f - f.min()) / (f.max() - f.min())
        return cls(f, 0.0)

    @property
    def f(self):
        return self.f_in

    @property
    def s(self):
        return self.s_in

    @property
    def t(self):
        return self.s_in ** 2

    def g(self, s):
        """
        Apply a Gaussian filter with a `sigma` (std-dev) of s.
        """
        s_out = np.sqrt((self.s_in ** 2) + (s ** 2))

        # Compute s_out relative to the current output level
        # NOTE: if level is 0, this is the same as s_rel = s_out
        s_rel = s_out / (2 ** self.level)

        # Blur the signal to compute the signal at a coarser scale
        f_out = g(self.f_in, s_rel)

        history = self.history + [s_rel]

        return Signal(f_out, s_out, self.level, history)

    def L(self, t):
        """
        Same as `g` but parameterized by the `t` scale space parameter.
        """
        s = np.sqrt(t)
        return self.g(s)

    def down(self):
        """
        Downsample the signal
        """
        # The current scale must be high enough where adding a level does not
        # reduce the sample frequency under the Nyquist limit (otherwise
        # aliasing would happen).

        # TODO: Is this correct? When exactly is it ok to downsample?
        scale_thresh = 2 ** (self.level)
        if self.s < scale_thresh:
            raise Exception(
                'Cannot downsample while details finer '
                'than 2 pixels still remain')

        # Downsample does not change the current scale, but it does impact
        # future smoothing operations
        f_out = down(self.f_in)
        s_out = self.s

        history = self.history + ['down']
        return Signal(f_out, s_out, self.level + 1, history)

    def similarity(self, other):
        """
        due to floating point errors, quantization errors, and border effects
        two theoretically equivalent scale space representations might not be
        have small differences. Ideally both numbers returned here will be
        reasonably small.
        """
        # NOTE: We are never going to get the pixels to be exactly the same
        # what we are looking for is agreement between extrema.

        # Consider downsampling an image.  Even after appropriate smoothing
        # sampling with [1::2] and [0::2] will result in slightly different
        # pixel values. The key thing that lets downsampling be OK is that you
        # don't introduce any new extreme points (maxima or minima).

        a = self.f_in
        b = other.f_in
        diff = np.abs(a - b)
        return (diff.mean(), diff.max())

    def find_s(self, s_out):
        # Find the s_apply to achieve s_out (when level == 0)
        s_apply = np.sqrt((s_out ** 2) - (self.s_in ** 2))
        return s_apply

    def freq(self):
        # Compute frequency magnitudes
        fourier_mag = np.abs(np.fft.fftshift(np.fft.fft2(self.f_in))) ** 2
        return fourier_mag

    def plot(self):
        # Compute frequency magnitudes
        if len(self.f_in.shape) == 1:
            ft = np.fft.fft(self.f_in)
            ft_mag = np.abs(ft) ** 2
        else:
            ft = np.fft.fft2(self.f_in)
            ft_shift = np.fft.fftshift(ft)
            ft_mag = np.abs(ft_shift) ** 2
        fourier_mag = ft_mag
        return fourier_mag


def demo_addative_property():
    """
    Demonstrate adative property of Gaussian filtering
    L(f, t1 + t2) == L(L(f, t1), t2)
    """

    f = Signal.demo()

    t1 = 2.3
    t2 = 3.5

    a = f.L(t1 + t2)
    b = f.L(t1).L(t2)

    print(a.similarity(b))


def demo_downsample_property():
    """
    Demonstrate adative property of Gaussian filtering
    L(f, t1 + t2) == L(L(f, t1), t2)
    """
    f = Signal.demo()

    # Blur to an initial scale such that downsampling is OK
    base = f.L(3.0)

    # Downsample then blur
    a = base.down().L(1.0)
    # Blur then downsample
    b = base.L(1.0).down()

    print(a.similarity(b))
