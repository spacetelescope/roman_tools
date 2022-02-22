# Nancy Grace Roman Space Telescope (Roman) Simulation Tools

The Roman team at STScI has developed an exposure time calculator, a PSF model, and an image simulator for the science community to plan how they will use Roman. These tools are available separately as the Pandeia Exposure Time Calculator engine, the WebbPSF point spread function modeling package, and the Space Telescope Image Product Simulator (STIPS).   Comprehensive setup documentation for local installation as well as tutorials for Pandeia and WebbPSF are provided here.  STIPS is available at https://github.com/spacetelescope/STScI-STIPS.  High level overviews of the functionality of the tools are available on [STScI's Roman website](https://www.stsci.edu/roman/science-planning-toolbox).

Would you like to [launch the tools in a temporary environment in the cloud](#Play-with-the-tools-in-a-temporary-environment-in-the-cloud) or [install the simulation tools locally](#install-the-simulation-tools-locally)?

**To stay abreast of changes and make sure you always have the latest Roman simulation tools, you may wish to [subscribe to our mailing list](https://maillist.stsci.edu/scripts/wa.exe?SUBED1=WFIRST-TOOLS&A=1).** This list is low-traffic and only for announcements.

To cite our tools, we ask that you reference [Pontoppidan et al. 2016, "Pandeia: a multi-mission exposure time calculator for JWST and WFIRST", Proc. SPIE. 9910.](http://dx.doi.org/10.1117/12.2231768) and/or [Perrin et al. 2014, "Updated point spread function simulations for JWST with WebbPSF", Proc. SPIE. 9143.](http://adsabs.harvard.edu/abs/2014SPIE.9143E..3XP).

## Tutorial notebooks

The tutorials are stored as Jupyter Notebooks--documents which interleave code, figures, and prose explanations--and can be run locally once you have followed the setup instructions below. They can also be viewed in a browser.

  * [WebbPSF-Roman Tutorial](https://github.com/spacetelescope/roman_tools/blob/develop/notebooks/WebbPSF-Roman_Tutorial.ipynb) — Simulate a PSF for the Roman Wide-Field Instrument by selecting a detector position. Evaluate PSF differences between two detector positions. Shows both the WebbPSF notebook GUI and a brief example of performing calculations with the API.
  * [Pandeia-Roman Tutorial](https://github.com/spacetelescope/roman_tools/blob/develop/notebooks/Pandeia-Roman.ipynb) — Calculate exposure times and simulate detector "postage stamps" for scenes made up of point sources and extended sources.

## Play with the tools in a temporary environment in the cloud

We have automated the setup of a temporary evaluation environment for community users to evaluate the Roman Simulation Tools from STScI. This depends on a free third-party service called Binder, currently available in beta (without guarantees of uptime).

To launch in Binder *(beta)*, follow this URL: https://mybinder.org/v2/gh/spacetelescope/roman_tools.git/stable (**Note:** If you see an error involving redirects in Safari, try Chrome or Firefox. This should be fixed soon by the Binder project.)

It may take a few minutes to start up. Feel free to explore and run example calculations. Launching an environment through Binder will always use the most recent supported versions of our tools.

Simulation products can be saved and retrieved through the file browser, but the environment is **temporary**. After a certain time period, the entire environment will be shut down and the resources returned to the cloud whence it came.

If you wish to save code or output products, you **must** download them from the Jupyter interface. (Or, better yet, switch to a local installation of the tools!)

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

Sometimes you will see `Successfully tagged roman_tools:latest` in your terminal, but still get an error like this:

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
e4cb3f9a0cb1        roman_tools         "tini -- start-not..."   3 minutes ago       Up 3 minutes        127.0.0.1:8888->8888/tcp   priceless_mirzakhani
```

You can use the name or container ID to stop it with `docker stop`:

```
$ docker stop e4cb3f9a0cb1
e4cb3f9a0cb1
```

And then run `./run.sh` again.

## Install the simulation tools locally

The WebbPSF point-spread function model and Pandeia exposure time calculator engine are currently available for local installation by members of the science community. The required packages are distributed as part of Astroconda, a suite of astronomy-focused software packages for use with the [conda](https://conda.io/docs/) package manager for macOS and Linux.

### Before we begin

Astroconda depends on [conda](https://conda.io/docs/), a system that can manage multiple environments without letting packages in one clobber those in another. To accomplish this, it uses features of bash, the default shell on new Mac and Linux systems. Verify that you are running bash by running `ps` in a new terminal window and verifying that `bash` appears in the `CMD` column.

If you are using another shell, bear in mind that you **must** start a bash login shell (`bash -l`) to follow this guide and to run the simulation tools in a `conda` environment.

Commands for you to execute will be prefixed with a `$`. (You only need to type the part following the `$`.)

### Installing Astroconda

If you have already installed Astroconda, skip ahead to "Creating a Roman Tools environment".

The [Getting Started](http://astroconda.readthedocs.io/en/latest/getting_started.html) instructions for Astroconda cover setting up the conda package manager and certain environment variables. Enable the Astroconda channel with the command `conda config --add channels http://ssb.stsci.edu/astroconda` (as explained in the [Selecting a Software Stack](http://astroconda.readthedocs.io/en/latest/installation.html#configure-conda-to-use-the-astroconda-channel) document).

The Roman Simulation Tools suite includes the Pandeia engine, an exposure time and signal-to-noise calculator. To create a Python environment for Roman Simulation Tools, use the following command:

```
$ conda create -n roman_tools --yes python=3.7 astropy \
                                    synphot stsynphot photutils \
                                    future pyyaml pandas \
                                    webbpsf==1.0 webbpsf-data==1.0


```

This will create an environment called `roman_tools` containing the essential packages for Roman simulations. To use it, you must activate it every time you open a new terminal window. Go ahead and do that now:

```
$ source activate roman_tools
```

You should see a new prefix on your shell prompt. (If the prompt was `$` before, it should now look like `(roman_tools) $`.)

Next, create a new directory somewhere with plenty of space to hold the reference files and navigate there in your terminal (with `cd /path/to/reference/file/space` or similar).

### Installing synthetic photometry reference information

To obtain the [reference data](https://stsynphot.readthedocs.io/en/latest/#installation-and-setup) used for synthetic photometry, you will need to retrieve them via FTP. The `curl` command line tool can be used as follows to retrieve the archives:

```
(roman_tools) $ curl -OL https://archive.stsci.edu/hlsps/reference-atlases/hlsp_reference-atlases_hst_multi_everything_multi_v5_sed.tar    # 85 MB
(roman_tools) $ curl -OL https://archive.stsci.edu/hlsps/reference-atlases/hlsp_reference-atlases_hst_multi_star-galaxy-models_multi_v3_synphot2.tar    # 34 MB
(roman_tools) $ curl -OL https://archive.stsci.edu/hlsps/reference-atlases/hlsp_reference-atlases_hst_multi_pheonix-models_multi_v2_synphot5.tar    # 505 MB
(roman_tools) $ curl -OL https://archive.stsci.edu/hlsps/reference-atlases/hlsp_reference-atlases_jwst_multi_etc-models_multi_v1_synphot7.tar # 9 MB
```

This retrieves interstellar extinction curves, several spectral atlases, and a grid of stellar spectra derived from [PHOENIX](http://www.hs.uni-hamburg.de/index.php?option=com_content&view=article&id=14&Itemid=294&lang=en) models. Extract them into the current directory:

```
(roman_tools) $ tar xvzf ./hlsp_reference-atlases_hst_multi_everything_multi_v5_sed.tar
(roman_tools) $ tar xvzf ./hlsp_reference-atlases_hst_multi_star-galaxy-models_multi_v3_synphot2.tar
(roman_tools) $ tar xvzf ./hlsp_reference-atlases_hst_multi_pheonix-models_multi_v2_synphot5.tar 
(roman_tools) $ tar xvzf ./hlsp_reference-atlases_jwst_multi_etc-models_multi_v1_synphot7.tar
```

This will create a tree of files rooted at `grp/redcat/trds/` in the current directory.

(Instructions for installing the full set of Synphot reference data, including things like HST instrument throughput reference files, can be found [in the PySynphot documentation](http://pysynphot.readthedocs.io/en/latest/index.html#installation-and-setup).)

### Installing the Pandeia Engine

The Pandeia Engine is available through PyPI (the Python Package Index), rather than Astroconda. Fortunately, we can install it into our `roman_tools` environment with the following command:

```
(roman_tools) $ pip install pandeia.engine==1.7
```

Note that the `==1.7` on the package name explicitly requests version 1.7, which is the version that is compatible with the bundled reference data.

Pandeia also depends on a collection of reference data to define the characteristics of the Roman instruments. Download it (45 MB) as follows and extract:

```
(roman_tools) $ curl -OL https://stsci.box.com/shared/static/ycbm34uxhzafgb7te74vyl2emnr1mdty.gz
(roman_tools) $ tar xvzf ./ycbm34uxhzafgb7te74vyl2emnr1mdty.gz
```

This creates a folder called `pandeia_data-1.7_roman` in the current directory.

## Running the simulation tools locally

WebbPSF, Pandeia, and Synphot all depend on certain environment variables to determine the paths to reference data.

You may wish to save these variables in your `~/.bash_profile` file, or [a new conda/activate.d/ script](https://conda.io/docs/using/envs.html#saved-environment-variables) so they are always set when you go to run the Roman simulation tools.

### Configuring environment variables

Where you see `$(pwd)` in the following commands, substitute in the directory where you have chosen to store the reference data (e.g. `echo "$(pwd)"` becomes `echo "/path/to/reference/file/space"`).

Configure the Synphot CDBS path:

```
(roman_tools) $ export PYSYN_CDBS="$(pwd)/grp/redcat/trds"
```

To test that synphot can find its reference files, use the following command:

```
(roman_tools) $ python -c "import warnings; warnings.simplefilter('ignore'); import stsynphot; print(stsynphot.catalog.grid_to_spec('phoenix', 5750, 0.0, 4.5))"
```

If you see output for a SourceSpectrum detailing the Model, Inputs, Outputs, and Components, synphot, stsynphot, and their reference data files have been installed correctly.

Next, configure the Pandeia path:

```
(roman_tools) $ export pandeia_refdata="$(pwd)/pandeia_data-1.7_roman"
```

To test that Pandeia can find its reference files, use the following command:

```
(roman_tools) $ python -c 'import pandeia.engine; pandeia.engine.pandeia_version()'
```

If your data is set up correctly, it will output the version numbers for the Engine and RefData.

### Viewing and running these example notebooks

In a terminal where you have run `source activate roman_tools` and set the above environment variables, navigate to the directory where you would like to keep the example notebooks and clone this repository from GitHub:

```
(roman_tools) $ git clone https://github.com/spacetelescope/roman_tools.git
```

This will create a new folder called `roman_tools` containing this README and all of the example notebooks. From this directory, simply run `jupyter notebook`. Choose `Getting Started.ipynb` from the file list, and explore the available examples of WebbPSF and Pandeia calculations.

## Resources

Pandeia users are encouraged to address questions, suggestions, and bug reports to help@stsci.edu with "Pandeia-Roman question" in the subject line. The message will be directed to the appropriate members of the Pandeia-Roman team at STScI.  For issues with WebbPSF, we prefer that you report your issues in the GitHub issue tracker for the speediest response: https://github.com/spacetelescope/webbpsf/issues (choose the green "New Issue" button after logging in).


  * [WebbPSF documentation](https://pythonhosted.org/webbpsf/)
  * [WebbPSF JWST quickstart notebook](http://nbviewer.jupyter.org/github/spacetelescope/webbpsf/blob/master/notebooks/WebbPSF_tutorial.ipynb)
  * [Perrin et al. 2014, "Updated point spread function simulations for JWST with WebbPSF", Proc. SPIE. 9143.](http://adsabs.harvard.edu/abs/2014SPIE.9143E..3XP)
  * How to use the ETC python code interface: [JWST ETC Pandeia Engine Tutorial](http:///jwst-docs.stsci.edu/display/JPP/JWST+ETC+Pandeia+Engine+Tutorial "JWST ETC Pandeia Engine Tutorial")
  * [Pandeia tutorials on Space Telescope's GitHub](https://github.com/spacetelescope/pandeia-tutorials)
  * [Pontoppidan et al. 2016, "Pandeia: a multi-mission exposure time calculator for JWST and WFIRST", Proc. SPIE. 9910.](http://dx.doi.org/10.1117/12.2231768)
