#!/bin/bash
set -e

# This script downloads data files, requirements and installs Pandeia and WebbPSF
# Please note that this script is intended to be used by Docker files as it will
# set or change environmental variables.


DIR="$( cd "$( dirname "$0" )" && pwd )"

# Extract PySynphot reference data
wget -qO- http://ssb.stsci.edu/cdbs/tarfiles/synphot1.tar.gz | tar xvz
wget -qO- http://ssb.stsci.edu/cdbs/tarfiles/synphot2.tar.gz | tar xvz
wget -qO- http://ssb.stsci.edu/cdbs/tarfiles/synphot5.tar.gz | tar xvz

export PYSYN_CDBS=$DIR/grp/hst/cdbs

# Extract Pandeia reference data
wget -qO- https://stsci.box.com/shared/static/5j506xzg9tem2l7ymaqzwqtxne7ts3sr.gz | tar -xvz
export pandeia_refdata=$DIR/pandeia_data-1.5_wfirst

# Extract WebbPSF reference data
# (note: version number env vars are declared close to where they are used
# to prevent unnecessary rebuilds of the Docker image)
export WEBBPSF_DATA_VERSION=0.8.0
wget -qO- http://www.stsci.edu/~mperrin/software/webbpsf/webbpsf-data-$WEBBPSF_DATA_VERSION.tar.gz | tar xvz
export WEBBPSF_PATH=$DIR/webbpsf-data


# Enable conda-forge package list
conda config --add channels conda-forge
# Configure AstroConda
conda config --system --add channels http://ssb.stsci.edu/astroconda

# Install WFIRST Simulation Tools dependencies for python2 and python3
# from conda:
EXTRA_PACKAGES="astropy=2.0.6 pyfftw pysynphot photutils future pyyaml pandas"
conda install --quiet --yes $EXTRA_PACKAGES && \
     conda clean -tipsy

pip install ipywidgets==7.0.0

# Install Pandeia
export PANDEIA_VERSION=1.5
pip install --no-cache-dir pandeia.engine==$PANDEIA_VERSION

# Install WebbPSF
export WEBBPSF_VERSION=0.8.0
#pip install --no-cache-dir webbpsf==$WEBBPSF_VERSION
pip install git+git://github.com/spacetelescope/webbpsf.git@master
pip install git+git://github.com/spacetelescope/poppy.git

