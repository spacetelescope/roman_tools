# WFIRST Simulation Tools

The WFIRST team at STScI has developed an [exposure time calculator](http://www.stsci.edu/wfirst/software/Pandeia) and [a PSF model](http://www.stsci.edu/wfirst/software/webbpsf) for the science community to plan how they will use WFIRST. These tools are available separately as the [Pandeia exposure time calculator engine](http://www.stsci.edu/wfirst/software/Pandeia) and [WebbPSF point spread function modeling package](http://www.stsci.edu/wfirst/software/webbpsf), but are provided here with comprehensive setup documentation for local installation as well as tutorials on their use.

**To stay abreast of changes and make sure you always have the latest WFIRST simulation tools, you may wish to [subscribe to our mailing list](https://maillist.stsci.edu/scripts/wa.exe?SUBED1=WFIRST-TOOLS&A=1).** This list is low-traffic and only for announcements.

Would you like to view the [tutorial notebooks](#tutorial-notebooks) or [install the simulation tools locally](#install-the-simulation-tools-locally)?

To cite our tools, we ask that you reference [Pontoppidan et al. 2016, "Pandeia: a multi-mission exposure time calculator for JWST and WFIRST", Proc. SPIE. 9910.](http://dx.doi.org/10.1117/12.2231768) and/or [Perrin et al. 2014, "Updated point spread function simulations for JWST with WebbPSF", Proc. SPIE. 9143.](http://adsabs.harvard.edu/abs/2014SPIE.9143E..3XP).

## Tutorial notebooks

The tutorials are stored as Jupyter Notebooks--documents which interleave code, figures, and prose explanations--and can be run locally once you have followed the setup instructions below. They can also be viewed in a browser.

  * [WebbPSF-WFIRST Tutorial](./blob/master/notebooks/WebbPSF-WFIRST_Tutorial.ipynb) — Simulate a PSF for the WFIRST Wide-Field Instrument by selecting a detector position. Evaluate PSF differences between two detector positions. Shows both the WebbPSF notebook GUI and a brief example of performing calculations with the API.
  * [Pandeia-WFIRST Tutorial](./blob/master/notebooks/Pandeia-WFIRST.ipynb) — Calculate exposure times and simulate detector "postage stamps" for scenes made up of point sources and extended sources.

## Run locally in a container with Docker

1. Start by installing the free [Docker Community Edition](https://www.docker.com/community-edition) locally. This will make the `docker` command available in your terminal. Note that after installing docker, you must open the application once for docker to be available from the command line.
2. Clone this repository to a folder on your computer and `cd` into it.
3. Execute `./run.sh` to build and start a Docker container. (The first time you build the container, you will have to download a lot of data files, but subsequent builds will be quick.) You should see a lot of output, ending with something like:

   ```
   [C 12:34:56.000 NotebookApp]

       Copy/paste this URL into your browser when you connect for the first time,
       to login with a token:
           http://localhost:8888/?token=aabbccddeeff00112233445566778899
   ```

  Open that URL in a browser, and you'll see a Jupyter notebook interface to an environment with the tools available. (The `run.sh` script forwards `localhost:8888` to the same port in the container, so you can copy the URL as-is.)

**To stay abreast of changes and make sure you always have the latest WFIRST simulation tools, you may wish to [subscribe to our mailing list](https://maillist.stsci.edu/scripts/wa.exe?SUBED1=WFIRST-TOOLS&A=1).** This list is low-traffic and only for announcements.

### Keeping your environment up to date

From time to time, we will release new versions of the tools or new notebooks. You can clone a fresh copy by following the instructions again, or use `git pull` from a terminal in the repository folder. (If you've run or modified your copies of the notebooks, you may want to make copies so your changes aren't clobbered. Use `git checkout .` to discard changes or `git stash` to temporarily stash them before `git pull`-ing.)

### Troubleshooting

#### When I run `./run.sh` I get `-bash: docker: command not found`

1. Make sure you have Docker Community Edition installed correctly.
2. Make sure to include the path to Docker in your `PATH` environment variable. For example include the following line in your bashrc file:

If Docker is located in `/usr/local/bin`
```
export PATH=/usr/local/bin:$PATH
```

3. Consult the [Docker manual](https://docs.docker.com/manuals/) section on troubleshooting.

#### When I run `./run.sh`, I get an error saying "context canceled"

Sometimes you will see `Successfully tagged wfirst-tools:latest` in your terminal, but still get an error like this:

```
docker: Error response from daemon: driver failed programming external
connectivity on endpoint eloquent_lewin
(549b43e32ae795c446f14fd6408c72fe9ddf08dbb8bde1122c28299696eda064): Bind for
127.0.0.1:8888 failed: port is already allocated.
ERRO[0000] error waiting for container: context canceled
```

This means that port 8888 is already in use, either by a notebook server running on your computer, or by another Docker container. If you're pretty sure you aren't running anything on port 8888, you can use `docker ps` to see if the container is running:

```
$ docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                      NAMES
e4cb3f9a0cb1        wfirst-tools        "tini -- start-not..."   3 minutes ago       Up 3 minutes        127.0.0.1:8888->8888/tcp   priceless_mirzakhani
```

You can use the name or container ID to stop it with `docker stop`:

```
$ docker stop e4cb3f9a0cb1
e4cb3f9a0cb1
```

And then run `./run.sh` again.

## Install the simulation tools locally

The WebbPSF point-spread function model and Pandeia exposure time calculator engine are currently available for local installation by members of the science community. The required packages are distributed as part of Astroconda, a suite of astronomy-focused software packages for use with the [conda](https://conda.io/docs/) package manager for macOS and Linux.

*STIPS, the Space Telescope Image Product Simulator, is not currently available for local installation. See the page at http://www.stsci.edu/wfirst/software/STIPS for information on obtaining access to STIPS.*

### Before we begin

Astroconda depends on [conda](https://conda.io/docs/), a system that can manage multiple environments without letting packages in one clobber those in another. To accomplish this, it uses features of bash, the default shell on new Mac and Linux systems. Verify that you are running bash by running `ps` in a new terminal window and verifying that `bash` appears in the `CMD` column.

If you are using another shell, bear in mind that you **must** start a bash login shell (`bash -l`) to follow this guide and to run the simulation tools in a `conda` environment.

Commands for you to execute will be prefixed with a `$`. (You only need to type the part following the `$`.)

### Installing Astroconda

If you have already installed Astroconda, skip ahead to "Creating a WFIRST Tools environment".

The [Getting Started](http://astroconda.readthedocs.io/en/latest/getting_started.html) instructions for Astroconda cover setting up the conda package manager and certain environment variables. Enable the Astroconda channel with the command `conda config --add channels http://ssb.stsci.edu/astroconda` (as explained in the [Selecting a Software Stack](http://astroconda.readthedocs.io/en/latest/installation.html#configure-conda-to-use-the-astroconda-channel) document).

The WFIRST Simulation Tools suite includes Pandeia, an exposure time and signal-to-noise calculator that (for now) depends on Python 2.7. To create a Python 2.7 environment for WFIRST Simulation Tools, use the following command:

```
$ conda create -n wfirst-tools --yes python=2.7 numpy scipy astropy \
                                     ipython-notebook ipykernel \
                                     pyfftw pysynphot photutils \
                                     webbpsf webbpsf-data
```

This will create an environment called `wfirst-tools` containing the essential packages for WFIRST simulations. To use it, you must activate it every time you open a new terminal window. Go ahead and do that now:

```
$ source activate wfirst-tools
```

You should see a new prefix on your shell prompt. (If the prompt was `$` before, it should now look like `(wfirst-tools) $`.)

Next, create a new directory somewhere with plenty of space to hold the reference files and navigate there in your terminal (with `cd /path/to/reference/file/space` or similar).

### Installing synthetic photometry reference information

To obtain the [reference data](http://pysynphot.readthedocs.io/en/latest/#installation-and-setup) used for synthetic photometry, you will need to retrieve them via FTP. The `curl` command line tool can be used as follows to retrieve the archives:

```
(wfirst-tools) $ curl -OL ftp://ftp.stsci.edu/cdbs/tarfiles/synphot1.tar.gz    # 85 MB
(wfirst-tools) $ curl -OL ftp://ftp.stsci.edu/cdbs/tarfiles/synphot2.tar.gz    # 34 MB
(wfirst-tools) $ curl -OL ftp://ftp.stsci.edu/cdbs/tarfiles/synphot5.tar.gz    # 505 MB
```

This retrieves interstellar extinction curves, several spectral atlases, and a grid of stellar spectra derived from [PHOENIX](http://www.hs.uni-hamburg.de/index.php?option=com_content&view=article&id=14&Itemid=294&lang=en) models. Extract them into the current directory:

```
(wfirst-tools) $ tar xvzf ./synphot1.tar.gz
(wfirst-tools) $ tar xvzf ./synphot2.tar.gz
(wfirst-tools) $ tar xvzf ./synphot5.tar.gz
```

This will create a tree of files rooted at `grp/hst/cdbs/` in the current directory.

(Instructions for installing the full set of PySynphot reference data, including things like HST instrument throughput reference files, can be found [in the PySynphot documentation](http://pysynphot.readthedocs.io/en/latest/index.html#installation-and-setup).)

### Installing the Pandeia engine

Pandeia is available through PyPI (the Python Package Index), rather than Astroconda. Fortunately, we can install it into our `wfirst-tools` environment with the following command:

```
(wfirst-tools) $ pip install pandeia.engine==1.2.1
```

Note that the `==1.2.1` on the package name explicitly requests version 1.2.1, which is the version that is compatible with the bundled reference data.

Pandeia also depends on a collection of reference data to define the characteristics of the WFIRST instruments. Download it (54 MB) as follows and extract:

```
(wfirst-tools) $ curl -OL https://github.com/spacetelescope/wfirst-tools/raw/master/pandeia_wfirst_data-1.2.1.tar.gz
(wfirst-tools) $ tar xvzf ./pandeia_wfirst_data-1.2.1.tar.gz
```

This creates a folder called `pandeia_wfirst_data` in the current directory.

## Running the simulation tools locally

WebbPSF, Pandeia, and pysynphot all depend on certain environment variables to determine the paths to reference data.

You may wish to save these variables in your `~/.bash_profile` file, or [a new conda/activate.d/ script](https://conda.io/docs/using/envs.html#saved-environment-variables) so they are always set when you go to run the WFIRST simulation tools.

### Configuring environment variables

Where you see `$(pwd)` in the following commands, substitute in the directory where you have chosen to store the reference data (e.g. `echo "$(pwd)"` becomes `echo "/path/to/reference/file/space"`).

Configure the PySynphot CDBS path:

```
(wfirst-tools) $ export PYSYN_CDBS="$(pwd)/grp/hst/cdbs"
```

To test that pysynphot can find its reference files, use the following command:

```
(wfirst-tools) $ python -c "import warnings; warnings.simplefilter('ignore'); import pysynphot; print pysynphot.Icat('phoenix', 5750, 0.0, 4.5).name"
```

If you see "phoenix(Teff=5750,z=0,logG=4.5)" appear in your terminal, pysynphot and its reference data files have been installed correctly.

Next, configure the Pandeia path:

```
(wfirst-tools) $ export pandeia_refdata="$(pwd)/pandeia_wfirst_data"
```

To test that Pandeia can find its reference files, use the following command:

```
(wfirst-tools) $ python -c 'from pandeia.engine.wfirst import WFIRSTImager; WFIRSTImager(mode="imaging")'
```

If you do not see any errors, Pandeia was able to instantiate a WFIRST WFI model successfully.

### Viewing and running these example notebooks

In a terminal where you have run `source activate wfirst-tools` and set the above environment variables, navigate to the directory where you would like to keep the example notebooks and clone this repository from GitHub:

```
(wfirst-tools) $ git clone https://github.com/spacetelescope/wfirst-tools.git
```

This will create a new folder called `wfirst-tools` containing this README and all of the example notebooks. From this directory, simply run `jupyter notebook`. Choose `Getting Started.ipynb` from the file list, and explore the available examples of WebbPSF and Pandeia calculations.

## Resources

The STScI helpdesk at help@stsci.edu is available for members of the WFIRST scientific community. For issues with WebbPSF, we prefer that you report your issues in the GitHub issue tracker for the speediest response: https://github.com/mperrin/webbpsf/issues (choose the green "New Issue" button after logging in).

  * [WebbPSF documentation](https://pythonhosted.org/webbpsf/)
  * [WebbPSF JWST quickstart notebook](http://nbviewer.jupyter.org/github/mperrin/webbpsf/blob/master/notebooks/WebbPSF_tutorial.ipynb)
  * [Perrin et al. 2014, "Updated point spread function simulations for JWST with WebbPSF", Proc. SPIE. 9143.](http://adsabs.harvard.edu/abs/2014SPIE.9143E..3XP)
  * [Pandeia tutorials on Space Telescope's GitHub](https://github.com/spacetelescope/pandeia-tutorials)
  * [Pontoppidan et al. 2016, "Pandeia: a multi-mission exposure time calculator for JWST and WFIRST", Proc. SPIE. 9910.](http://dx.doi.org/10.1117/12.2231768)
