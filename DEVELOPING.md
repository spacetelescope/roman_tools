# Developing the WFIRST Tools

## Generating a WFIRST Pandeia data package

To use Pandeia 1.1.1 with the WFIRST Pandeia GUI, you must make a patched data package containing an updated configuration file. The provided code also subsets the Pandeia reference data to contain only the WFIRST-specific and mission-independent data.

Minimum Python version: Python 3.4.

```
$ curl -OL http://ssb.stsci.edu/pandeia/engine/1.1.1/pandeia_data-1.1.1.tar.gz
$ tar xvzf ./pandeia_data-1.1.1.tar.gz
$ export pandeia_refdata=./pandeia_data-1.1.1/
$ python3 -m toolbox.etc.make_data_package
New data package in /Users/jlong/software/wfirst-tools/pandeia_refdata_wfirst
Successfully performed the default calculation for wfirstimager
Compressed WFIRST Pandeia data into /Users/jlong/software/wfirst-tools/pandeia_data_wfirst.tar.gz
```

Hopefully the next point release of Pandeia corrects this, and you can delete `./notebooks/toolbox/etc/make_data_package.py`, `./notebooks/toolbox/etc/data_patch/`, and `./pandeia_wfirst_data.tar.gz`. You'll need to change the corresponding section of the `Dockerfile` to fetch an archive from some URL instead of using a file in the repository as well. (See the section that installs the WebbPSF data for inspiration.)

## Updating software versions

For new releases of WebbPSF or Pandeia, you will need to edit both the installation instructions in `README.md` and the installation script in the `Dockerfile`.

The Dockerfile uses environment variables to define the versions of software used (and minimize the number of lines you have to update). Here's a list of them:

  * `TMV_VERSION`
  * `WEBBPSF_DATA_VERSION`
  * `PYTHON_VERSION`
  * `GALSIM_RELEASE` (Note: this is actually the git branch name for the release, e.g. `releases/1.4`.)
  * `PANDEIA_VERSION`
  * `WEBBPSF_VERSION`

The variables are defined close to where they are used, as updating them busts the cache for all the following `Dockerfile` commands.

To verify that the `Dockerfile` updates worked, run `./run.sh` before committing and pushing.
Outdated: Once you have pushed your commits, visit https://beta.mybinder.org/v2/gh/spacetelescope/wfirst-tools/master to run a build of the Binder container image. (Otherwise, the first person to try and follow the Binder link will have to wait through an entire build!)
