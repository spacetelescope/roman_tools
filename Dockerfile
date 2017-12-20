FROM jupyter/scipy-notebook
MAINTAINER Joseph Long <help@stsci.edu>

# Note: this is ordered roughly by how often things are expected
# to change (ascending). That way, only the last few changed steps
# are rebuilt on push.

WORKDIR $HOME

# As root:
USER root

# Install distro packages for dependencies
ENV APT_EXTRA_PACKAGES libfftw3-dev scons libblas-dev liblapack-dev gfortran
RUN apt-get update \
 && apt-get install -yq --no-install-recommends $APT_EXTRA_PACKAGES \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Install TMV (custom linear algebra library) from source
ENV TMV_VERSION 0.73
RUN wget -qO- https://github.com/rmjarvis/tmv/archive/v$TMV_VERSION.tar.gz | tar xvz
RUN cd tmv-$TMV_VERSION && sudo scons install

#
# Install reference data under /opt
#

WORKDIR /opt

# Extract PySynphot reference data
RUN wget -qO- ftp://ftp.stsci.edu/cdbs/tarfiles/synphot1.tar.gz | tar xvz
RUN wget -qO- ftp://ftp.stsci.edu/cdbs/tarfiles/synphot2.tar.gz | tar xvz
RUN wget -qO- ftp://ftp.stsci.edu/cdbs/tarfiles/synphot5.tar.gz | tar xvz
ENV PYSYN_CDBS /opt/grp/hst/cdbs

# Extract Pandeia reference data
COPY pandeia_wfirst_data.tar.gz /opt
RUN tar xvzf pandeia_wfirst_data.tar.gz
ENV pandeia_refdata /opt/pandeia_wfirst_data

# Extract WebbPSF reference data
# (note: version number env vars are declared close to where they are used
# to prevent unnecessary rebuilds of the Docker image)
ENV WEBBPSF_DATA_VERSION 0.5.0
RUN wget -qO- http://www.stsci.edu/~mperrin/software/webbpsf/webbpsf-data-$WEBBPSF_DATA_VERSION.tar.gz | tar xvz
ENV WEBBPSF_PATH /opt/webbpsf-data

WORKDIR $HOME

USER $NB_USER
# Prepare environment variables
ENV PYHOME /opt/conda
ENV PY2HOME $PYHOME/envs/python2
ENV PYTHON_VERSION 3.6
ENV PATH $HOME/bin:$PATH
ENV LD_LIBRARY_PATH $HOME/lib:$LD_LIBRARY_PATH

# Enable conda-forge package list
RUN conda config --add channels conda-forge
# Configure AstroConda
RUN conda config --system --add channels http://ssb.stsci.edu/astroconda

# Install WFIRST Simulation Tools dependencies for python2 and python3
# from conda:
ENV EXTRA_PACKAGES astropy pyfftw pysynphot photutils future pyyaml pandas boost
RUN conda install --quiet --yes $EXTRA_PACKAGES && \
    conda clean -tipsy
RUN conda install --quiet --yes -n python2 $EXTRA_PACKAGES && \
    conda clean -tipsy
# from pip:
RUN pip3 install --no-cache-dir starlink-pyast
RUN pip2 install --no-cache-dir starlink-pyast

# Install GalSim
ENV GALSIM_RELEASE releases/1.4
RUN git clone -b $GALSIM_RELEASE --depth=1 https://github.com/GalSim-developers/GalSim.git $HOME/galsim-repo
WORKDIR $HOME/galsim-repo
# Build GalSim
# for Python 3
RUN scons \
    PREFIX=$PYHOME \
    PYTHON=$PYHOME/bin/python \
    PYPREFIX=$PYHOME/lib/python$PYTHON_VERSION/site-packages \
    BOOST_DIR=$PYHOME && \
    scons install
# for Python 2
RUN scons \
    PREFIX=$PY2HOME \
    PYTHON=$PY2HOME/bin/python \
    PYPREFIX=$PY2HOME/lib/python2.7/site-packages \
    BOOST_DIR=$PY2HOME && \
    scons install
WORKDIR $HOME

# Install Pandeia
ENV PANDEIA_VERSION 1.2
RUN pip2 install --no-cache-dir pandeia.engine==$PANDEIA_VERSION
RUN pip3 install --no-cache-dir pandeia.engine==$PANDEIA_VERSION

# Install WebbPSF
ENV WEBBPSF_VERSION 0.5.1
RUN pip2 install --no-cache-dir webbpsf==$WEBBPSF_VERSION
RUN pip3 install --no-cache-dir webbpsf==$WEBBPSF_VERSION

#
# Prepare files and permissions
#
USER root
# Clean up build files
RUN rm -rf $HOME/tmv-$TMV_VERSION
RUN mv $HOME/galsim-repo/examples $HOME/galsim-examples
RUN rm -rf $HOME/galsim-repo

# Copy notebooks into place
# (n.b. This must be last because otherwise Dockerfile edits
# invalidate the build cache)
COPY . $HOME
RUN chown -R jovyan $HOME/
