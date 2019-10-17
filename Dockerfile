FROM jupyter/scipy-notebook:db3ee82ad08a
MAINTAINER Space Telescope Science Institute <help@stsci.edu>

# Note: this is ordered roughly by how often things are expected
# to change (ascending). That way, only the last few changed steps
# are rebuilt on push.

WORKDIR $HOME

##############
# Root Setup #
##############

USER root
RUN mkdir -p /opt
RUN chown $NB_USER /opt

COPY ./docker/install_webbpsf_pandeia.sh /opt/.
RUN chmod +x /opt/install_webbpsf_pandeia.sh

USER $NB_USER

# Update pip
RUN pip install -U pip
RUN pip install -U setuptools


###############################
# Install webbpsf and pandeia #
###############################

# Prepare environment variables
ENV PYHOME /opt/conda
ENV PYTHON_VERSION 3.6
ENV PATH $HOME/bin:$PATH
ENV LD_LIBRARY_PATH $HOME/lib:$LD_LIBRARY_PATH

WORKDIR /opt

RUN /opt/install_webbpsf_pandeia.sh

ENV PYSYN_CDBS /opt/grp/hst/cdbs
ENV pandeia_refdata /opt/pandeia_data-1.5_wfirst
ENV WEBBPSF_PATH /opt/webbpsf-data

RUN rm /opt/install_webbpsf_pandeia.sh

WORKDIR $HOME

# Copy notebooks into place
# (n.b. This must be last because otherwise Dockerfile edits
# invalidate the build cache)
COPY ./notebooks/* $HOME/
USER root
RUN chown -R $NB_USER $HOME/
