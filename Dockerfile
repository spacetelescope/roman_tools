FROM jupyter/scipy-notebook

MAINTAINER Joseph Long <help@stsci.edu>

WORKDIR $HOME
COPY . $HOME
RUN conda config --system --add channels http://ssb.stsci.edu/astroconda
ENV EXTRA_PACKAGES astropy pyfftw pysynphot photutils

RUN conda install --quiet --yes $EXTRA_PACKAGES
RUN conda install --quiet --yes -n python2 $EXTRA_PACKAGES
# RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --no-cache-dir notebook==5.0.0 jupyterhub==0.7.2

# RUN wget -qO- http://www.stsci.edu/~mperrin/software/webbpsf/webbpsf-data-0.5.0.tar.gz  | tar xvz
# ENV WEBBPSF_PATH=$HOME/webbpsf-data/