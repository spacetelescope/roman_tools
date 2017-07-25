from __future__ import division, absolute_import, print_function
import os
from os.path import isdir
from astropy.visualization import LogStretch, ZScaleInterval
from astropy.visualization.mpl_normalize import ImageNormalize

__all__ = (
    'ensure_dir',
    'write_ds9_overlay',
    'quick_mono_norm'
)

def ensure_dir(dirpath):
    try:
        os.makedirs(dirpath)
    except OSError:
        if not isdir(dirpath):
            raise
    return dirpath


def write_ds9_overlay(outpath, ra, dec):
    with open(outpath, 'w') as f:
        f.writelines([
            '# Region file format: DS9 version 4.1\n',
            'global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 '
            'highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n',
            'fk5\n',
        ])
        for point_ra, point_dec in zip(ra, dec):
            f.write('point({},{}) # point=circle\n'.format(point_ra, point_dec))


def quick_mono_norm(image, contrast=0.25):
    interval = ZScaleInterval(contrast=contrast)
    vmin, vmax = interval.get_limits(image)
    norm = ImageNormalize(vmin=vmin, vmax=vmax, stretch=LogStretch(), clip=True)
    return norm
