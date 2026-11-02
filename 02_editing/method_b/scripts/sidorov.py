"""Sidorov (2019) photo-editing tools, translated from MATLAB to Python.

Source: Sidorov, "Changing the Image Memorability: From Basic Photo Editing
to GANs":
https://github.com/acecreamu/changing-the-memorability (PHOTO_EDITING.m).

Each tool takes a photograph and returns the edited photograph, with the same
settings as Sidorov's code. Two differences from the original Sidorov's code:
  - clarity: MATLAB's built-in function for it (localcontrast) is not
    public, so a similar effect of the same strength is used instead.
  - background blurring / darkening: these need a map that separates the
    subject from the background. PHOTO_EDITING.m says "any third-party
    algorithm can be used for their creation" (Sidorov used maps extracted
    from AttGAN); for food we use the dish mask.
"""

from __future__ import annotations

import math

import cv2
import numpy as np

# --------------------------------------------------------- colour conversions
# Math formulas for color conversion to mimic MATLAB's built-in logic.
# Some editing functions below rely on these formulas.
_RGB2XYZ = np.array([[0.412453, 0.357580, 0.180423],
                     [0.212671, 0.715160, 0.072169],
                     [0.019334, 0.119193, 0.950227]])
_XYZ2RGB = np.linalg.inv(_RGB2XYZ)
_D65 = np.array([0.95047, 1.0, 1.08883])


def rgb2xyz(rgb):
    """rgb in [0, 1], shape (..., 3)."""
    rgb = np.asarray(rgb, dtype=np.float64)
    lin = np.where(rgb > 0.04045, ((rgb + 0.055) / 1.055) ** 2.4, rgb / 12.92)
    return lin @ _RGB2XYZ.T


def xyz2rgb(xyz):
    """Returns rgb clipped to [0, 1]."""
    lin = np.asarray(xyz, dtype=np.float64) @ _XYZ2RGB.T
    rgb = np.where(lin > 0.0031308, 1.055 * np.abs(lin) ** (1 / 2.4) - 0.055, 12.92 * lin)
    return np.clip(rgb, 0, 1)


def rgb2lab(rgb):
    t = rgb2xyz(rgb) / _D65
    f = np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16 / 116)
    return np.stack([116 * f[..., 1] - 16,
                     500 * (f[..., 0] - f[..., 1]),
                     200 * (f[..., 1] - f[..., 2])], axis=-1)


def lab2rgb(lab):
    lab = np.asarray(lab, dtype=np.float64)
    fy = (lab[..., 0] + 16) / 116
    f = np.stack([fy + lab[..., 1] / 500, fy, fy - lab[..., 2] / 200], axis=-1)
    t = np.where(f > 0.2068966, f ** 3, (f - 16 / 116) / 7.787)
    return xyz2rgb(t * _D65)


def _uint8(x: np.ndarray) -> np.ndarray:
    """MATLAB uint8(): round half away from zero, then saturate."""
    x = np.asarray(x, dtype=np.float64)
    return np.clip(np.sign(x) * np.floor(np.abs(x) + 0.5), 0, 255).astype(np.uint8)


def imgaussfilt(im: np.ndarray, sigma: float) -> np.ndarray:
    """MATLAB imgaussfilt on uint8 input: replicate padding, rounded uint8 out."""
    k = 2 * math.ceil(2 * sigma) + 1
    out = cv2.GaussianBlur(im.astype(np.float64), (k, k), sigma,
                           borderType=cv2.BORDER_REPLICATE)
    return _uint8(out)


# --------------------------------------------------------------- the nine tools
def sharp(im):
    """Unsharp mask, sigma 1.5, amount 2.0."""
    filtered = imgaussfilt(im, 1.5).astype(np.float64)
    return _uint8(im + 2.0 * (im.astype(np.float64) - filtered))


def contrast(im):
    """threashold: 127."""
    x = im.astype(np.float64)
    return _uint8(x + 1.5 * (x - 127) * np.exp(-(x - 127) ** 2 * 0.0004))


def gray(im):
    """rgb2gray, returned as three identical channels so later it can be scored by ResMem Model.
    """
    x = im.astype(np.float64)
    g = _uint8(0.298936021293775 * x[..., 0] + 0.587043074451121 * x[..., 1]
               + 0.114020904255103 * x[..., 2])
    return np.repeat(g[..., None], 3, axis=2)


def vignetting(im):
    """Gaussian fall-off, std 200 on a 500x500 grid, resized to the image.
    """
    X, Y = np.meshgrid(np.arange(1, 501), np.arange(1, 501))
    n = np.exp(-((X - 250.0) ** 2 + (Y - 250.0) ** 2) / (2 * 40000.0))
    n /= n.max()
    v = cv2.resize(n, (im.shape[1], im.shape[0]), interpolation=cv2.INTER_CUBIC)
    return _uint8(im.astype(np.float64) * v[..., None])


def vibrance(im):
    """Designed to peak chroma boost at C = 50; same as in the author's Matlab code """
    lab = rgb2lab(im.astype(np.float64) / 255.0)
    C = np.hypot(lab[..., 1], lab[..., 2])
    h = np.arctan2(lab[..., 2], lab[..., 1])
    C = C + 30 * np.exp(-0.5 * ((C - 50) / 20) ** 2)
    lab = np.stack([lab[..., 0], C * np.cos(h), C * np.sin(h)], axis=2)
    return _uint8(lab2rgb(lab) * 255)


_M_CAT02 = np.array([[0.7328, 0.4296, -0.1624],
                     [-0.7036, 1.6975, 0.0061],
                     [0.0030, 0.0136, 0.9834]])
_T5000K = np.array([1.0000, 0.7792, 0.6180])


def temperature(im, white=_T5000K):
    """Standardizes image color temperature to neutral daylight (5000K) to remove lighting bias across the dataset."""
    xyz = rgb2xyz(im.astype(np.float64) / 255.0).reshape(-1, 3).T
    lms = _M_CAT02 @ xyz
    wh2_lms = _M_CAT02 @ rgb2xyz(white.reshape(1, 1, 3)).reshape(3)
    g = float(np.array([0.2989, 0.5870, 0.1140]) @ white)
    wh1_lms = _M_CAT02 @ rgb2xyz(np.full((1, 1, 3), g)).reshape(3)
    lms = lms * (wh2_lms / wh1_lms)[:, None]
    xyz = np.linalg.solve(_M_CAT02, lms).T.reshape(im.shape)
    return _uint8(xyz2rgb(xyz) * 255)


def clarity(im, edge_threshold=0.8, amount=0.2, levels=5):
    """APPROXIMATION of MATLAB localcontrast(I, 0.8, 0.2).
    Enhances image clarity by boosting local texture contrast by 20%. It strictly targets pixel lightness and ignores harsh edges, 
    without artificially distorting the image's original color balance or general structures.
    """
    lab = rgb2lab(im.astype(np.float64) / 255.0)
    L = lab[..., 0] / 100.0
    pyr, cur = [], L
    for _ in range(levels):
        down = cv2.pyrDown(cur)
        up = cv2.pyrUp(down, dstsize=(cur.shape[1], cur.shape[0]))
        d = cur - up
        # detail above the edge threshold is kept as is
        pyr.append(np.where(np.abs(d) < edge_threshold, d * (1 + amount), d))
        cur = down
    out = cur
    for d in reversed(pyr):
        out = cv2.pyrUp(out, dstsize=(d.shape[1], d.shape[0])) + d
    lab[..., 0] = np.clip(out, 0, 1) * 100.0
    return _uint8(lab2rgb(lab) * 255)


def bg_blur(im, attention):
    """Background blur, sigma 10, mixed by a dish mask.
    """
    m = attention[..., None].astype(np.float64)
    return _uint8(im * m + imgaussfilt(im, 10).astype(np.float64) * (1 - m))


def bg_blur_darken(im, attention):
    """'increasing volume': background blurred and darkened.
    blur first, then dark. we code based on author's paper: background blurring with darkening.
    """
    m = attention[..., None].astype(np.float64)
    blurred = im * m + imgaussfilt(im, 10).astype(np.float64) * (1 - m)
    return _uint8(blurred * (0.5 * m + 0.5))


# Table 3:Change of memorability score (estimated from AMNet) by image editing operations. 
TOOLS = {
    "sharpening":        (sharp,          False, +0.023),
    "bg_blurring":       (bg_blur,        True,  -0.008),
    "bg_blur_darkening": (bg_blur_darken, True,  -0.049),
    "grayscaling":       (gray,           False, -0.023),
    "contrast":          (contrast,       False, -0.007),
    "temperature_5000k": (temperature,    False, -0.002),
    "vibrance":          (vibrance,       False, +0.005),
    "clarity_approx":    (clarity,        False, -0.002),
    "vignetting":        (vignetting,     False, -0.024),
}
