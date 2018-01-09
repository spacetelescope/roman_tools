FROM jupyter/scipy-notebook:db3ee82ad08a
MAINTAINER Space Telescope Science Institute <help@stsci.edu>

# Note: this is ordered roughly by how often things are expected
# to change (ascending). That way, only the last few changed steps
# are rebuilt on push.

WORKDIR $HOME

#
# Install reference data under /opt
#
USER root
RUN mkdir -p /opt
RUN chown $NB_USER /opt

USER $NB_USER
WORKDIR /opt
# Extract PySynphot reference data
RUN wget -qO- ftp://ftp.stsci.edu/cdbs/tarfiles/synphot1.tar.gz | tar xvz
RUN wget -qO- ftp://ftp.stsci.edu/cdbs/tarfiles/synphot2.tar.gz | tar xvz
RUN wget -qO- ftp://ftp.stsci.edu/cdbs/tarfiles/synphot5.tar.gz | tar xvz
ENV PYSYN_CDBS /opt/grp/hst/cdbs

# Extract Pandeia reference data
RUN wget -qO- http://ssb.stsci.edu/pandeia/engine/1.2.1/pandeia_wfirst_data-1.2.1.tar.gz | tar xvz
ENV pandeia_refdata /opt/pandeia_data-1.2.1_wfirst

# Extract WebbPSF reference data
# (note: version number env vars are declared close to where they are used
# to prevent unnecessary rebuilds of the Docker image)
ENV WEBBPSF_DATA_VERSION 0.6.0
RUN wget -qO- http://www.stsci.edu/~mperrin/software/webbpsf/webbpsf-data-$WEBBPSF_DATA_VERSION.tar.gz | tar xvz
ENV WEBBPSF_PATH /opt/webbpsf-data

WORKDIR $HOME

# Prepare environment variables
ENV PYHOME /opt/conda
ENV PYTHON_VERSION 3.6
ENV PATH $HOME/bin:$PATH
ENV LD_LIBRARY_PATH $HOME/lib:$LD_LIBRARY_PATH

# Enable conda-forge package list
RUN conda config --add channels conda-forge
# Configure AstroConda
RUN conda config --system --add channels http://ssb.stsci.edu/astroconda

# Install WFIRST Simulation Tools dependencies for python2 and python3
# from conda:
ENV EXTRA_PACKAGES astropy pyfftw pysynphot photutils future pyyaml pandas
RUN conda install --quiet --yes $EXTRA_PACKAGES && \
    conda clean -tipsy

RUN pip install ipywidgets==7.0.0

# Install Pandeia
ENV PANDEIA_VERSION 1.2.1
RUN pip install --no-cache-dir pandeia.engine==$PANDEIA_VERSION

# Install WebbPSF
ENV WEBBPSF_VERSION 0.6.0
RUN pip install --no-cache-dir webbpsf==$WEBBPSF_VERSION

#
# Prepare files and permissions
#

# Copy notebooks into place
# (n.b. This must be last because otherwise Dockerfile edits
# invalidate the build cache)
COPY ./notebooks/* $HOME/
USER root
RUN chown -R $NB_USER $HOME/
