"""ImageMagick operators used by the editing grid, reimplemented in numpy.

Each function reproduces the ImageMagick 6.9 / 7 code path of one command-line
operator.

Source (ImageMagick 6, https://github.com/ImageMagick/ImageMagick6):
    _rgb2hsb, _hsb2rgb      magick/gem.c        ConvertRGBToHSB, ConvertHSBToRGB
    modulate_hsb_f          magick/enhance.c    ModulateImage, ModulateHSB
    brightness_contrast_f   magick/enhance.c    BrightnessContrastImage
    _kernel                 magick/gem.c        GetOptimalKernelWidth1D;
                            magick/morphology.c "Blur" kernel
    blur_f, unsharp_f       magick/effect.c     BlurImage, UnsharpMaskImage


    modulate(im, b, s)              -modulate b,s        (HSL colourspace, IM default)
    modulate_hsb(im, b, s)          -define modulate:colorspace=HSB -modulate b,s
    brightness_contrast(im, b, c)   -brightness-contrast b,c
    blur(im, sigma)                 -blur 0xsigma
    unsharp(im, sigma, gain, thr)   -unsharp 0xsigma+gain+thr

All take and return RGB uint8 arrays. ImageMagick holds pixels at 16 bits
between operators (Q16). These functions work in float and round once, when
the 8-bit result is written, so they can differ from ImageMagick by one level
on some pixels.
"""

from __future__ import annotations

import numpy as np

Q = 65535.0                       # QuantumRange at Q16
EPS = 1.0e-12                     # MagickEpsilon


def _f(im):
    """uint8 -> float in [0, 1], as ImageMagick scales 8-bit input to Q16."""
    return np.asarray(im, dtype=np.float64) / 255.0


def _u8(x):
    """float in [0, 1] -> uint8, as ImageMagick writes an 8-bit PNG."""
    return np.floor(np.clip(x, 0.0, 1.0) * 255.0 + 1e-9).astype(np.uint8)


# ----------------------------------------------------------------- -modulate
def _rgb2hsl(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1)
    c = mx - mn
    L = (mx + mn) / 2.0
    safe = np.where(c > 0, c, 1.0)
    h = np.where(np.abs(mx - r) < EPS, (g - b) / safe + np.where(g < b, 6.0, 0.0),
                 np.where(np.abs(mx - g) < EPS, 2.0 + (b - r) / safe, 4.0 + (r - g) / safe))
    h = np.where(c > 0, h * 60.0 / 360.0, 0.0)
    den = np.where(L <= 0.5, 2.0 * L, 2.0 - 2.0 * L)
    s = np.where(c > 0, c / np.where(den > EPS, den, EPS), 0.0)   
    return h, s, L


def _hsl2rgb(h, s, L):
    c = np.where(L <= 0.5, 2.0 * L * s, (2.0 - 2.0 * L) * s)
    mn = L - 0.5 * c
    hh = h * 360.0
    hh = hh - 360.0 * np.floor(hh / 360.0)
    hh = hh / 60.0
    x = c * (1.0 - np.abs(hh - 2.0 * np.floor(hh / 2.0) - 1.0))
    k = np.floor(hh).astype(int)
    r = np.select([k == 0, k == 1, k == 2, k == 3, k == 4], [mn + c, mn + x, mn, mn, mn + x], mn + c)
    g = np.select([k == 0, k == 1, k == 2, k == 3, k == 4], [mn + x, mn + c, mn + c, mn + x, mn], mn)
    b = np.select([k == 0, k == 1, k == 2, k == 3, k == 4], [mn, mn, mn + x, mn + c, mn + c], mn + x)
    return np.stack([r, g, b], -1)


def modulate_f(x, brightness=100.0, saturation=100.0):
    if brightness == 100 and saturation == 100:
        return x
    h, s, L = _rgb2hsl(x)
    return np.clip(_hsl2rgb(h, s * 0.01 * saturation, L * 0.01 * brightness), 0, 1)


def _rgb2hsb(rgb):
    """ImageMagick ConvertRGBToHSB (= HSV)."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = mx - mn
    s = np.where(mx > EPS, d / np.where(mx > EPS, mx, 1.0), 0.0)
    sd = np.where(d > 0, d, 1.0)
    h = np.where(np.abs(r - mx) < EPS, (g - b) / sd,
                 np.where(np.abs(g - mx) < EPS, 2.0 + (b - r) / sd, 4.0 + (r - g) / sd)) / 6.0
    h = np.where(s > EPS, np.where(h < 0, h + 1.0, h), 0.0)
    return h, s, mx


def _hsb2rgb(h, s, v):
    """ImageMagick ConvertHSBToRGB (= HSV)."""
    hh = 6.0 * (h - np.floor(h))
    f = hh - np.floor(hh)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    k = np.floor(hh).astype(int)
    conds = [k == 0, k == 1, k == 2, k == 3, k == 4]
    r = np.select(conds, [v, q, p, p, t], v)
    g = np.select(conds, [t, v, v, q, p], p)
    b = np.select(conds, [p, p, t, v, v], q)
    out = np.stack([r, g, b], -1)
    grey = (s < EPS)[..., None]
    return np.where(grey, v[..., None], out)


def modulate_hsb_f(x, brightness=100.0, saturation=100.0):
    """-define modulate:colorspace=HSB -modulate B,S. Scales HSV value and
    saturation, the quantities Study 1 measures. Brightening multiplies the
    RGB channels, so colours keep their hue and are not washed with white."""
    if brightness == 100 and saturation == 100:
        return x
    h, s, v = _rgb2hsb(x)
    return np.clip(_hsb2rgb(h, s * 0.01 * saturation, v * 0.01 * brightness), 0, 1)


# ------------------------------------------------------ -brightness-contrast
def brightness_contrast_f(x, brightness=0.0, contrast=0.0):
    """Linear in each channel. Slope and intercept as in ImageMagick 6.9.10+ / 7."""
    if brightness == 0 and contrast == 0:
        return x
    slope = 100.0 / (100.0 - contrast) if contrast >= 0 else 0.01 * contrast + 1.0
    intercept = (0.01 * brightness - 0.5) * slope + 0.5
    return np.clip(slope * x + intercept, 0, 1)


# --------------------------------------------------------- -blur / -unsharp
def _kernel(sigma):
    """Kernel width from GetOptimalKernelWidth1D(0, sigma); values from
    morphology.c's "Blur" kernel, which samples the Gaussian at three points
    per pixel (KernelRank 3) and sums them into each tap."""
    a, beta = 1.0 / (2 * sigma * sigma), 1.0 / (np.sqrt(2 * np.pi) * sigma)
    width = 5
    while True:
        j = (width - 1) // 2
        i = np.arange(-j, j + 1)
        if np.exp(-(j * j) * a) * beta / (np.exp(-(i * i) * a) * beta).sum() < 1.0 / Q:
            break
        width += 2
    width -= 2
    rank = 3
    v = (width * rank - 1) // 2
    u = np.arange(-v, v + 1)
    s3 = sigma * rank
    k = np.zeros(width)
    np.add.at(k, (u + v) // rank, np.exp(-(u * u) / (2 * s3 * s3)))
    return k / k.sum()


def _conv1d(x, k, axis):
    j = len(k) // 2
    pad = [(0, 0)] * x.ndim
    pad[axis] = (j, j)
    xp = np.pad(x, pad, mode="edge")            # virtual-pixel "edge", IM default
    out = np.zeros_like(x)
    n = x.shape[axis]
    for t, w in enumerate(k):
        out += w * np.take(xp, np.arange(t, t + n), axis=axis)
    return out

def blur_f(x, sigma):
    """Gaussian blur (ImageMagick -blur 0x{sigma}). Each pixel becomes a
    weighted average of its neighbours, weights following a Gaussian with
    standard deviation sigma (in pixels). Larger sigma = blurrier."""
    k = _kernel(sigma)
    return np.clip(_conv1d(_conv1d(x, k, 1), k, 0), 0, 1)

def unsharp_f(x, sigma, gain, threshold):
    """Unsharp mask, the standard sharpening method (ImageMagick
    -unsharp 0x{sigma}+{gain}+{threshold}). The name comes from darkroom
    practice: a blurred ("unsharp") copy is subtracted from the image, which
    leaves the edges (d); the edges are then added back, amplified.
      sigma      size of the edges detected (Gaussian sigma, pixels)
      gain       strength: how much of the edges is added back (the
                 "amount" in Photoshop, GIMP and scikit-image)
      threshold  pixels whose edge signal is below this are left unchanged,
                 so flat areas and noise are not sharpened (ImageMagick
                 compares 2 * |d| with it)"""
    d = x - blur_f(x, sigma)
    return np.clip(np.where(np.abs(2.0 * d) < threshold, x, x + d * gain), 0, 1)


# ------------------------------------------------- uint8 wrappers, one operator
def modulate(im, b=100, s=100):
    return _u8(modulate_f(_f(im), b, s))


def modulate_hsb(im, b=100, s=100):
    return _u8(modulate_hsb_f(_f(im), b, s))


def brightness_contrast(im, b=0, c=0):
    return _u8(brightness_contrast_f(_f(im), b, c))


def blur(im, sigma):
    return _u8(blur_f(_f(im), sigma))


def unsharp(im, sigma, gain, threshold):
    return _u8(unsharp_f(_f(im), sigma, gain, threshold))
