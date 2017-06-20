FROM jupyter/scipy-notebook

MAINTAINER Joseph Long <help@stsci.edu>

WORKDIR $HOME
USER $NB_USER

# Extract PySynphot reference data into $HOME/grp/hst/cdbs
RUN wget -qO- ftp://ftp.stsci.edu/cdbs/tarfiles/synphot2.tar.gz | tar xvz
RUN wget -qO- ftp://ftp.stsci.edu/cdbs/tarfiles/synphot5.tar.gz | tar xvz
# Configure environment variables for reference data
ENV PYSYN_CDBS $HOME/grp/hst/cdbs

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

### Pandeia
# Extract Pandeia reference data into $HOME/pandeia_data-1.0
RUN wget -qO- http://ssb.stsci.edu/pandeia/engine/1.0/pandeia_data-1.0.tar.gz | tar xvz
ENV pandeia_refdata $HOME/pandeia_data-1.0

# Install Pandeia
RUN pip2 install --no-cache-dir pandeia.engine==1.0
RUN pip3 install --no-cache-dir pandeia.engine==1.0

### WebbPSF
ENV WEBBPSF_VERSION 0.5.1
ENV WEBBPSF_DATA_VERSION 0.5.0

# Extract WebbPSF reference data into $HOME/webbpsf-data
RUN wget -qO- http://www.stsci.edu/~mperrin/software/webbpsf/webbpsf-data-$WEBBPSF_DATA_VERSION.tar.gz | tar xvz
ENV WEBBPSF_PATH $HOME/webbpsf-data

# Install WebbPSF
RUN pip2 install --no-cache-dir webbpsf==$WEBBPSF_VERSION
RUN pip3 install --no-cache-dir webbpsf==$WEBBPSF_VERSION

### Copy notebooks into place
COPY . $HOME

# As root, adjust permissions on notebooks and other files
USER root
RUN chown -R $NB_USER:users $HOME/*
RUN chmod -R u+rwX $HOME/*

# ... and switch back to RUNing as jovyan
USER $NB_USER
