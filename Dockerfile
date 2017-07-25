FROM jupyter/scipy-notebook

MAINTAINER Joseph Long <help@stsci.edu>

WORKDIR $HOME
USER $NB_USER

# Copy notebooks into place
COPY . $HOME

# Note: this Dockerfile is ordered roughly by how often things are expected
# to change (ascending). That way, only the last few changed steps are
# rebuilt on push.

# Configure AstroConda
RUN conda config --system --add channels http://ssb.stsci.edu/astroconda

# Extract PySynphot reference data into $HOME/grp/hst/cdbs
RUN wget -qO- ftp://ftp.stsci.edu/cdbs/tarfiles/synphot2.tar.gz | tar xvz
RUN wget -qO- ftp://ftp.stsci.edu/cdbs/tarfiles/synphot5.tar.gz | tar xvz
ENV PYSYN_CDBS $HOME/grp/hst/cdbs

# Install WFIRST Simulation Tools dependencies for python2 and python3
ENV EXTRA_PACKAGES astropy pyfftw pysynphot photutils
RUN conda install --quiet --yes $EXTRA_PACKAGES && \
    conda remove  --quiet --yes --force qt pyqt && \
    conda clean -tipsy
RUN conda install --quiet --yes -n python2 $EXTRA_PACKAGES && \
    conda remove  --quiet --yes -n python2 --force qt pyqt && \
    conda clean -tipsy

# Install Pandeia
ENV PANDEIA_VERSION 1.1.1
RUN pip2 install --no-cache-dir pandeia.engine==$PANDEIA_VERSION
RUN pip3 install --no-cache-dir pandeia.engine==$PANDEIA_VERSION

# Extract Pandeia reference data into $HOME/pandeia_wfirst_data
RUN tar xvzf $HOME/pandeia_wfirst_data.tar.gz
ENV pandeia_refdata $HOME/pandeia_wfirst_data

# Extract WebbPSF reference data into $HOME/webbpsf-data
# (note: version number env vars are declared close to where they are used
# to prevent unnecessary rebuilds of the Docker image)
ENV WEBBPSF_DATA_VERSION 0.5.0
RUN wget -qO- http://www.stsci.edu/~mperrin/software/webbpsf/webbpsf-data-$WEBBPSF_DATA_VERSION.tar.gz | tar xvz
ENV WEBBPSF_PATH $HOME/webbpsf-data

# Install WebbPSF
ENV WEBBPSF_VERSION 0.5.1
RUN pip2 install --no-cache-dir webbpsf==$WEBBPSF_VERSION
RUN pip3 install --no-cache-dir webbpsf==$WEBBPSF_VERSION

#
# Prepare files and permissions
#

# As root, adjust permissions on notebooks
USER root
RUN chown -Rv $NB_USER:users $HOME/*.ipynb
RUN chmod -Rv u+rwX $HOME/*.ipynb

# ... and switch back to RUNing as jovyan
USER $NB_USER
