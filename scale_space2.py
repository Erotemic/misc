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
