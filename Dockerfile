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
RUN wget -qO- https://archive.stsci.edu/hlsps/reference-atlases/hlsp_reference-atlases_hst_multi_everything_multi_v5_sed.tar | tar xvz
RUN wget -qO- https://archive.stsci.edu/hlsps/reference-atlases/hlsp_reference-atlases_hst_multi_star-galaxy-models_multi_v3_synphot2.tar | tar xvz
RUN wget -qO- https://archive.stsci.edu/hlsps/reference-atlases/hlsp_reference-atlases_hst_multi_pheonix-models_multi_v2_synphot5.tar | tar xvz
RUN wget -qO- https://archive.stsci.edu/hlsps/reference-atlases/hlsp_reference-atlases_jwst_multi_etc-models_multi_v1_synphot7.tar | tar xvz
ENV PYSYN_CDBS /opt/grp/redcat/trds

# Extract Pandeia reference data
RUN wget -qO- https://stsci.box.com/shared/static/ycbm34uxhzafgb7te74vyl2emnr1mdty.gz | tar xvz
ENV pandeia_refdata /opt/pandeia_data-1.7_roman

# Extract WebbPSF reference data
# (note: version number env vars are declared close to where they are used
# to prevent unnecessary rebuilds of the Docker image)
ENV WEBBPSF_DATA_VERSION 1.0.0
RUN wget -qO- https://stsci.box.com/shared/static/34o0keicz2iujyilg4uz617va46ks6u9.gz | tar xvz
ENV WEBBPSF_PATH /opt/webbpsf-data

WORKDIR $HOME

# Prepare environment variables
ENV PYHOME /opt/conda
ENV PYTHON_VERSION 3.7
ENV PATH $HOME/bin:$PATH
ENV LD_LIBRARY_PATH $HOME/lib:$LD_LIBRARY_PATH

# Enable conda-forge package list
RUN conda config --add channels conda-forge
# Configure AstroConda
RUN conda config --system --add channels http://ssb.stsci.edu/astroconda

# Install Roman Simulation Tools dependencies for python3 from conda:
ENV EXTRA_PACKAGES astropy synphot stsynphot photutils future pyyaml pandas
RUN conda install --quiet --yes $EXTRA_PACKAGES && \
    conda clean -tipsy

RUN pip install ipywidgets==7.0.0

# Install Pandeia
ENV PANDEIA_VERSION 1.7
RUN pip install --no-cache-dir pandeia.engine==$PANDEIA_VERSION

# Install WebbPSF
ENV WEBBPSF_VERSION 1.0.0
#RUN pip install --no-cache-dir webbpsf==$WEBBPSF_VERSION
RUN pip install git+git://github.com/spacetelescope/webbpsf.git@develop
RUN pip install git+git://github.com/spacetelescope/poppy.git
#
# Prepare files and permissions
#

# Copy notebooks into place
# (n.b. This must be last because otherwise Dockerfile edits
# invalidate the build cache)
COPY ./notebooks/* $HOME/
USER root
RUN chown -R $NB_USER $HOME/
