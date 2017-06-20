FROM jupyter/scipy-notebook

MAINTAINER Joseph Long <help@stsci.edu>

WORKDIR $HOME
COPY . $HOME

# Download WebbPSF reference data into $HOME
RUN wget -qO- http://www.stsci.edu/~mperrin/software/webbpsf/webbpsf-data-0.5.0.tar.gz | tar xvz

# As root, adjust permissions on notebooks and other files
USER root
RUN chown -R $NB_USER:users $HOME/*
RUN chmod -R u+rwX $HOME/*

# ... and back to RUNing as jovyan
USER $NB_USER

# Configure AstroConda
RUN conda config --system --add channels http://ssb.stsci.edu/astroconda
ENV EXTRA_PACKAGES astropy pyfftw pysynphot photutils

# Install WFIRST Simulation Tools dependencies for python2 and python3
RUN conda install --quiet --yes $EXTRA_PACKAGES && \
    conda remove  --quiet --yes --force qt pyqt && \
    conda clean -tipsy
RUN conda install --quiet --yes -n python2 $EXTRA_PACKAGES && \
    conda remove  --quiet --yes -n python2 --force qt pyqt && \
    conda clean -tipsy

# Install Pandeia 1.0
RUN pip install --no-cache-dir pandeia.engine==1.0

# Configure environment variables for reference data
ENV PYSYN_CDBS $HOME/grp/hst/cdbs
ENV WEBBPSF_PATH $HOME/webbpsf-data
ENV pandeia_refdata $HOME/pandeia-data-1.0
