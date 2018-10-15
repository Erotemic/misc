import numpy as np
import ubelt as ub
import scipy
import scipy.ndimage
import netharn as nh
import scipy


def g(f, σ, **kw):
    truncate = kw.get('truncate', 6.0)  # overkill
    if len(f.shape) == 1:
        sigma = σ
    elif len(f.shape) == 3:
        sigma = (σ, σ, 0)
    else:
        sigma = (σ, σ)
    return scipy.ndimage.gaussian_filter(f, sigma=sigma,
                                         truncate=truncate)


def L(f, t, **kw):
    return g(f, σ=np.sqrt(t), **kw)


def down(f):
    if len(f.shape) == 1:
        return f[0:None:2]
    else:
        return f[0:None:2, 0:None:2]


def close_enough(a, b):
    diff = np.abs(a - b)
    return (diff.mean(), diff.max())


class Signal(ub.NiceRepr):
    """
    Notes:
        The spatial frequency of the digital sampling. The reciprocal of
        the center-to-center distance between adjacent pixels.
    """
    def __init__(self, f_in, s_in, level=0, history=None):
        self.f_in = f_in
        self.s_in = s_in
        self.level = level
        if history is None:
            history = [s_in]
        self.history = history

    def __nice__(self):
        return '{}, s={:.4f}, t={:.4f}'.format(self.f.shape, self.s, self.t)

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
        a = self.f_in
        b = other.f_in
        diff = np.abs(a - b)
        return (diff.mean(), diff.max())

    def find_s(self, s_out):
        # Find the s to achieve s_out
        s = np.sqrt((s_out ** 2) - (self.s_in ** 2))
        return s

    def freq(self):
        # Compute frequency magnitudes
        fourier_mag = np.abs(np.fft.fftshift(np.fft.fft2(self.f_in))) ** 2
        return fourier_mag
        # nh.util.imshow(fourier_mag, norm='log')

    def plot(self):
        if len(self.f.shape) == 1:
            from matplotlib import pyplot as plt
            plt.plot(self.f)
        else:
            nh.util.imshow(self.f)

    def foo(self):
        N = max(self.f_in.shape)
        t = np.arange(0, N)  # pixels
        signal = self.f_in
        dt = np.diff(t)[0]
        # N =
        # df=1/(N*dt);    % the frequency resolution (df=1/max_T)

        pass


def scale_space_v2():
    nh.util.autompl()

    img = nh.util.grab_test_image(space='gray') / 255.0
    nyquist_freq = max(img.shape) // 2

    # TODO: What is the frequency cutoff of a Gaussian Filter?

    f_in = img.mean(axis=0)
    f = Signal(f_in, 0)

    f0 = f.L(1.0)

    base = f0.L(3.0)

    # Downsample then blur
    a = base.down().L(1.0)
    # Blur then downsample
    b = base.L(1.0).down()


    f1 = Signal(f_in, 1.0)
    f1.plot()
    f1.g(np.sqrt(3.0)).down()

    f.g(0.3)

    from matplotlib import pyplot as plt
    plt.plot(f.f)

    nh.util.imshow(f.g(0.0).freq(), norm='log')
    nh.util.imshow(f.g(0.5).freq(), norm='log')
    nh.util.imshow(f.g(1 / np.sqrt(2)).freq(), norm='log')
    nh.util.imshow(f.g(2.0).freq(), norm='log')

    f1 = f.g(.5)
    f2 = f1.g(f1.find_s(1.0))
    f.g(f2.s).similarity(f2)

    f.g(f2.s)



def scale_space(signal):
    """
    References:
        https://en.wikipedia.org/wiki/Scale_spacmpe
        https://en.wikipedia.org/wiki/Scale_space_implementation
        https://dsp.stackexchange.com/questions/10275/creating-a-gaussian-pyramid
        http://www.montefiore.ulg.ac.be/~piater/papers/Crowley-2002-CogVis.pdf
        http://www.vlfeat.org/api/scalespace-fundamentals.html

        https://www.scipy-lectures.org/intro/scipy/auto_examples/solutions/plot_image_blur.html

        https://dsp.stackexchange.com/questions/24329/downsampling-and-gaussian-filtering-in-the-context-of-scale-space-pyramids

        https://stackoverflow.com/questions/12334551/low-pass-gaussian-filter-with-a-specified-cut-off-frequency


    Notes:
        The scale parameter {\displaystyle t=\sigma ^{2}} t=\sigma ^{2} is the
        variance of the Gaussian filter.

        The scale-space representation at scale level {\displaystyle t=0} t=0
        is the image {\displaystyle f} f itself.


        Subsampling is a bad idea unless you have previously blurred/smoothed
        the image! (because it leads to aliasing)

        When an image is halved, applying a gaussian kernel of σ will apply as
        2σ.

        downsample(I) * g(s) = I * g(2s)

        When an image is halfed, applying a scale of t will apply as 4*t

        When an image has a scale of σ, and a gaussian kernel of σ is applied,
        then the resulting image will have a scale of sqrt(2)*σ.


        Let x(t) be a signal defined over a continuous variable t.
        A kernel function, k(t), can be scaled to any scale factor, s, by
        dividing the t: `p(t, s) = x(t) ∗ k(t / s)`

        For a scale-invariant representation, the s variable should be sampled
        using an exponential series


        Gaussians of variance σ^2_1 and σ^2_2 results in a Gaussian of variance
        σ^2_3 = σ^2_1 + σ^2_2.

        An important detail is that the algorithm computing the scale space
        assumes that the input image ℓ(x,y) is pre-smoothed, roughly capturing
        the effect of the finite pixel size in a CCD (charge-coupled device?).
        This is modelled by assuming that the input is not ℓ(x,y), but
        ℓ(x,y,σn), where σn is a nominal smoothing, usually taken to be 0.5
        (half a pixel standard deviation). This also means that σ=σn=0.5 is the
        finest scale that can actually be computed

    Example:
        import netharn as nh
        import cv2
        img = nh.util.grab_test_image(space='bgr')

        p0 = img
        p1 = cv2.pyrDown(p0)
        p2 = cv2.pyrDown(p1)
        p3 = cv2.pyrDown(p2)

        nh.util.autompl()

        nh.util.imshow(p0)
        nh.util.imshow(p1)
        nh.util.imshow(p2)
        nh.util.imshow(p3)
    """
    import netharn as nh
    from skimage.transform import pyramid_gaussian
    import scipy
    nh.util.autompl()

    f = nh.util.grab_test_image(space='gray')
    f = nh.util.ensure_float01(f).astype(np.float64)
    f = nh.util.imutil.imscale(f, 1 / 2, interpolation='lanczos')[0]
    f = np.clip(f, 0, 1)

    def window_size(sigma):
        truncate = 6.0
        lw = int(truncate * sigma + 0.5)
        return lw

    def g(f, σ, **kw):
        truncate = kw.get('truncate', 6.0)  # overkill
        if len(f.shape) == 3:
            sigma = (σ, σ, 0)
        else:
            sigma = (σ, σ)
        return scipy.ndimage.gaussian_filter(f, sigma=sigma,
                                             truncate=truncate)

    def L(f, t, **kw):
        return g(f, σ=np.sqrt(t), **kw)

    def down(f):
        return f[0:None:2, 0:None:2]

    def close_enough(a, b):
        diff = np.abs(a - b)
        return (diff.mean(), diff.max())

    def apply_g(f_in, s_in, s=None, s_out=None):
        assert bool(s) ^ bool(s_out)
        if s_out is not None:
            # If we are given the desired output scale, compute what the
            # additional smoothing required is.
            s = np.sqrt((s_out ** 2) - (s_in ** 2))
        s_out = np.sqrt((s_in ** 2) + (s ** 2))
        f_out = g(f_in, s)
        return f_out, s_out, s

    def apply_down(f_in, s_in, s=None, s_out=None):
        assert bool(s) ^ bool(s_out)
        if s_out is not None:
            # If we are given the desired output scale, compute what the
            # additional smoothing required is.
            s = np.sqrt((s_out ** 2) - (s_in ** 2))
        s_out = np.sqrt((s_in ** 2) + (s ** 2))
        f_out = g(f_in, s)
        return f_out, s_out, s

    #  THIS WORKS
    a = g(g(f, 1.0), 1.0)
    b = g(f, np.sqrt(2))
    print(np.abs(a - b).max())

    # Also works
    a = g(g(g(g(f, 1.0), 1.0), 1.0), 1.0)
    b = g(f, 2)
    print(np.abs(a - b).max())

    # Demonstrate adative property of Gaussian filtering
    # L(f, t1 + t2) == L(L(f, t1), t2)
    # I'm pretty sure I did this right.
    # Note: t must be a minimum of 0.5
    # Also this is equivalent to:
    # g(f, sqrt(t1^2 + t2^2)) == g(g(f, t1^2), t2^2)
    rng = np.random.RandomState(0)
    for _ in range(1000):
        t1 = (rng.rand() * 8) + .5
        t2 = (rng.rand() * 8) + .5
        a = L(f, (t1 + t2))
        b = L(L(f, t1), t2)
        # There will be small differences due to floating point errors
        # Also, clip out borders which might be weird

        # make the radius of the filter equal to truncate standard deviations
        sigma = np.sqrt(t1 + t2)
        lw = window_size(sigma)
        sl = (slice(lw, -lw), slice(lw, -lw))
        diff = np.abs(a[sl] - b[sl])
        print(diff.max())
        assert (diff < 1e-1).mean() > .99
        assert (diff < 1e-2).mean() > .98
        assert (diff < 1e-3).mean() > .92

        # Show equivalence in case with just g
        s1 = np.sqrt(t1)
        s2 = np.sqrt(t2)
        a_ = g(f, np.sqrt(s1 ** 2 + s2 ** 2))
        b_ = g(g(f, s1 ** 2), s2 ** 2)

        diff_ = np.abs(a_[sl] - b_[sl])
        print(diff_.max())
        assert (diff < 1e-3).mean() > .92

    f1, s1, _ = apply_g(f, 0, σ_init)
    # apply_g(f1, s1, s_out=2 * σ_init)[-1]
    f2, s2, _ = apply_g(f1, s1, 0.8660254037844387)
    close_enough(apply_g(f, 0, s2)[0], f2)
    apply_g(f2, s2, .5)

    apply_g(f, 0, 2 * σ_init)

    f2 = g(f, 2 * σ_init)
    f2_down = down(f2)
    g(f2_down, .5)

    # Show the downsample -> double sigma effect
    # (This has much more numerical error I think)
    # Also I'm not sure I've done this right

    lw = 64
    sl = (slice(lw, -lw), slice(lw, -lw))
    f0 = L(f, t=1.0)  # initial nominal scaling

    # If you have an image that was filtered at an initial sigma above 0.5 (the Nyquist Limit?)
    s1 = 0.5
    f1 = g(f, s1)
    # If you double sigma, then you can downsample by a factor of 2 without losing information.
    s2 = 1.0
    f2  = g(f1, np.sqrt((s2 ** 2) - (s1 ** 2)))
    f2_ = g(f1, s2)




    f0 = g(f, .5)
    s0 = 0.0
    f1, s1, s = apply_g(f0, s0, .5)
    f2, s2, s = apply_g(f1, s1, s_out=1.0)
    f2_, s2_ = apply_g(f0, 0, s2)
    print(np.abs(f2_ - f2).max())


    f0 = g(f, 0.25)

    f1 = down(L(f0, 4.0))
    f2 = L(down(L(f0, 2)))

    f1 = down(g(f0, 4.0))
    f2 = g(down(g(f0, np.sqrt(2))), np.sqrt(2))


    t = 3.0
    a = down(g(f0, t=2 * t))
    b = g(down(f0), s=s)
    diff = np.abs(a[sl] - b[sl])
    print(diff.max(), diff.mean())

    t = 3.0
    a = down(g(f0, t=2 * t))
    b = g(down(f0), s=s)
    diff = np.abs(a[sl] - b[sl])
    print(diff.max(), diff.mean())

    a = down(L(f0, t=4.0))
    b = L(down(f0), t=2.0)
    diff = np.abs(a[sl] - b[sl])
    print(diff.max(), diff.mean())


def _decheck_scalespace():
    # The goal in re-investigateing this old code is to remember how Tburg
    # scale space works.
    # We should view each level of the Feature Pyramid as an octave in scale
    # space. Thus the anchor boxes, should correspond to very particular base
    # window sizes. The number of ar=1 boxes should be `num_intervals`, and
    # the size should correspond to those ksizes within the intervals.
    # Putting this here to indicate I thought about it, I probably wont touch
    # this again (but who knows).

    initial_sigma = 1.6
    num_intervals = 4

    def makepyramid_octave(level, num_intervals):
        # Downsample image to take sigma to a power of level
        step = (2 ** (level))
        # Compute interval relative scales
        interval = np.arange(num_intervals)
        relative_scales = (2 ** ((interval / num_intervals)))
        octave_sigmas = initial_sigma * relative_scales
        real_sigmas = octave_sigmas * step
        octave_ksizes = []
        for sigma in octave_sigmas:
            sizex = int(6. * sigma + 1.) + int(1 - (int(6. * sigma + 1.) % 2))
            ksize = (sizex, sizex)
            octave_ksizes.append(ksize)

        real_ksize = []
        for sigma in real_sigmas:
            sizex = int(6. * sigma + 1.) + int(1 - (int(6. * sigma + 1.) % 2))
            real_ksize.append(sizex)
        return (real_sigmas, real_ksize)

    pyramid = []
    num_octaves = 4
    for level in range(num_octaves):
        octave_sigmas, real_ksize = makepyramid_octave(level, num_intervals)
        pyramid.append(real_ksize)
