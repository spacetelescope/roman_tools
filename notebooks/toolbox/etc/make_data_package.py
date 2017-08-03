from __future__ import division, absolute_import, print_function
import sys
import os
from os.path import abspath, isdir, join, dirname, basename
import shutil
import glob

from ..utils import ensure_dir


def _noop(*args, **kwargs):
    pass


def make_data_package(pandeia_refdata=None, destination=None, log=_noop, overwrite=False):
    if pandeia_refdata is None:
        if os.environ.get('pandeia_refdata'):
            pandeia_refdata = os.environ.get('pandeia_refdata')
        else:
            raise RuntimeError("Supply pandeia_refdata path or set $pandeia_refdata")
    if destination is None:
        destination = abspath('./pandeia_wfirst_data')
    if isdir(destination) or len(glob.glob(join(destination, '*'))) != 0:
        if not overwrite:
            raise RuntimeError("Remove existing folder ({}) "
                               "or pass overwrite=True".format(destination))
        shutil.rmtree(destination)
    destination = ensure_dir(destination)

    # Populate only WFIRST and mission-independent data files
    for folder_name in ('wfirst', 'source', 'normalization', 'sed', 'strategy',
                        'background', 'extinction'):
        shutil.copytree(join(pandeia_refdata, folder_name), join(destination, folder_name))

    # Patch the data package's config file for WFIRST WFI
    shutil.copy(join(dirname(__file__), 'data_patch', 'wfirstimager_config.json'),
                join(destination, 'wfirst', 'wfirstimager', 'config.json'))

    log("New data package in", destination)
    return destination

if __name__ == "__main__":
    # Make package
    data_dir = make_data_package(log=print, overwrite=True)

    # Test package
    os.environ['pandeia_refdata'] = data_dir
    from pandeia.engine.perform_calculation import perform_calculation
    from pandeia.engine.calc_utils import build_default_calc
    calc = build_default_calc("wfirst", "wfirstimager", "imaging")
    result = perform_calculation(calc, dict_report=True)
    print("Successfully performed the default calculation for wfirstimager")
    if sys.version_info > (3, 2):
        archive_name = shutil.make_archive('pandeia_wfirst_data', 'gztar',
                                           root_dir=dirname(data_dir),
                                           base_dir=basename(data_dir))
        print("Compressed WFIRST Pandeia data into {}".format(archive_name))
