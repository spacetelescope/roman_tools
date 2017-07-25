FROM jupyter/scipy-notebook

MAINTAINER Joseph Long <help@stsci.edu>

WORKDIR $HOME
USER $NB_USER

# Define versions of interest
ENV WEBBPSF_DATA_VERSION 0.5.0
ENV WEBBPSF_VERSION 0.5.1

#
# Retrieve/extract reference data files
#

# Extract PySynphot reference data into $HOME/grp/hst/cdbs
RUN wget -qO- ftp://ftp.stsci.edu/cdbs/tarfiles/synphot2.tar.gz | tar xvz
RUN wget -qO- ftp://ftp.stsci.edu/cdbs/tarfiles/synphot5.tar.gz | tar xvz

# Extract WebbPSF reference data into $HOME/webbpsf-data
RUN wget -qO- http://www.stsci.edu/~mperrin/software/webbpsf/webbpsf-data-$WEBBPSF_DATA_VERSION.tar.gz | tar xvz

# Extract Pandeia reference data into $HOME/pandeia_wfirst_data
RUN wget -qO- http://www.stsci.edu/~jlong/pandeia_wfirst_data-1.1.1.tar.gz | tar xvz

# Configure environment variables for reference data
ENV PYSYN_CDBS $HOME/grp/hst/cdbs
ENV pandeia_refdata $HOME/pandeia_wfirst_data
ENV WEBBPSF_PATH $HOME/webbpsf-data

#
# Install software
#

# Configure AstroConda
RUN conda config --system --add channels http://ssb.stsci.edu/astroconda

# Install WFIRST Simulation Tools dependencies for python2 and python3
ENV EXTRA_PACKAGES astropy pyfftw pysynphot photutils
RUN conda install --quiet --yes $EXTRA_PACKAGES && \
    conda remove  --quiet --yes --force qt pyqt && \
    conda clean -tipsy
RUN conda install --quiet --yes -n python2 $EXTRA_PACKAGES && \
    conda remove  --quiet --yes -n python2 --force qt pyqt && \
    conda clean -tipsy

# Install Pandeia
RUN pip2 install --no-cache-dir pandeia.engine==1.1.1
RUN pip3 install --no-cache-dir pandeia.engine==1.1.1

# Install WebbPSF
RUN pip2 install --no-cache-dir webbpsf==$WEBBPSF_VERSION
RUN pip3 install --no-cache-dir webbpsf==$WEBBPSF_VERSION

#
# Prepare files and permissions
#

# Copy notebooks into place
COPY . $HOME

# As root, adjust permissions on notebooks
USER root
RUN chown -Rv $NB_USER:users $HOME/*.ipynb
RUN chmod -Rv u+rwX $HOME/*.ipynb

# ... and switch back to RUNing as jovyan
USER $NB_USER
