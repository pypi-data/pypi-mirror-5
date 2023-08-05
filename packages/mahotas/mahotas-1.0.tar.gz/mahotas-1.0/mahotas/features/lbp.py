# -*- coding: utf-8 -*-
# Copyright (C) 2008-2009 Robert Webb and Luis Pedro Coelho <luis@luispedro.org>
# Copyright (C) 2011-2013 Luis Pedro Coelho <luis@luispedro.org>
#
# License: MIT (see COPYING file)

import numpy as np
from ..histogram import fullhistogram

__all__ = [
    'lbp',
    ]
def lbp(image, radius, points, ignore_zeros=False):
    '''
    features = lbp(image, radius, points, ignore_zeros=False)

    Compute Linear Binary Patterns

    The return value is a **histogram** of feature counts, where position ``i``
    corresponds to the number of pixels that had code ``i``. The codes are
    compressed so that impossible codes are not used. Therefore, this is the
    ``i``th feature, not just the feature with binary code ``i``.

    Parameters
    ----------
    image : ndarray
        input image (2-D numpy ndarray)
    radius : number (integer or floating point)
        radius (in pixels)
    points : integer
        nr of points to consider
    ignore_zeros : boolean, optional
        whether to ignore zeros (default: False)

    Returns
    -------
    features : 1-D numpy ndarray
        histogram of features. See above for a caveat on the interpretation of
        these.

    Reference
    ---------
    Gray Scale and Rotation Invariant Texture Classification with Local Binary Patterns
        Ojala, T. Pietikainen, M. Maenpaa, T. Lecture Notes in Computer Science (Springer)
        2000, ISSU 1842, pages 404-420
    '''
    from ..interpolate import shift
    from mahotas.features import _lbp
    if ignore_zeros:
        Y,X = np.nonzero(image)
        def select(im):
            return im[Y,X].ravel()
        pixels = image[Y,X].ravel()
    else:
        select = np.ravel
        pixels = image.ravel()
    image = image.astype(np.float64)
    angles = np.linspace(0, 2*np.pi, points+1)[:-1]
    data = []
    for dy,dx in zip(np.sin(angles), np.cos(angles)):
        data.append(
            select(shift(image, [radius*dy,radius*dx], order=1)))
    data = np.array(data)
    codes = (data > pixels).astype(np.int32)
    codes *= (2**np.arange(points)[:,np.newaxis])
    codes = codes.sum(0)
    codes = _lbp.map(codes.astype(np.uint32), points)
    final = fullhistogram(codes.astype(np.uint32))

    codes = np.arange(2**points, dtype=np.uint32)
    iters = codes.copy()
    codes = _lbp.map(codes.astype(np.uint32), points)
    pivots = (codes == iters)
    npivots = np.sum(pivots)
    compressed = final[pivots[:len(final)]]
    compressed = np.concatenate((compressed, [0]*(npivots - len(compressed))))
    return compressed
