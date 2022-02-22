# Developing the Roman Tools (Outdated: now using Pandeia 1.7)

## Generating a Roman Pandeia data package

To use Pandeia 1.7 with the Roman Pandeia GUI, you need to download the Pandeia engine (the same code is used for JWST and Roman) and the appropriate Pandeia reference data that describe the Roman instruments.

The latest version of the Pandeia Engine is here: https://pypi.org/project/pandeia.engine/ and can also be installed with `pip install pandeia.engine`

The data files for Pandeia v1.7 are here: 
https://stsci.box.com/v/pandeia-refdata-v1p7-roman
Or by direct download here:
https://stsci.box.com/shared/static/ycbm34uxhzafgb7te74vyl2emnr1mdty.gz

Minimum Python version: Python 3.6. (Development has been done on Python 3.9)


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

- Outdated: Once you have pushed your commits, visit https://beta.mybinder.org/v2/gh/spacetelescope/roman-tools/master to run a build of the Binder container image. (Otherwise, the first person to try and follow the Binder link will have to wait through an entire build!)
