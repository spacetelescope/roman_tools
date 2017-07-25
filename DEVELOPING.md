# Developing the WFIRST Tools

## Generating a WFIRST Pandeia data package

To use Pandeia 1.1.1 with the WFIRST Pandeia GUI, you must make a patched data package containing an updated configuration file. The provided code also subsets the pandeia reference data to contain only the WFIRST-specific and mission-independent data. 

Minimum version: Python 3.2.

```
$ curl -OL http://ssb.stsci.edu/pandeia/engine/1.1.1/pandeia_data-1.1.1.tar.gz
$ tar xvzf ./pandeia_data-1.1.1.tar.gz
$ export pandeia_refdata=./pandeia_data-1.1.1/
$ python3 -m toolbox.etc.make_data_package
New data package in /Users/jlong/software/wfirst-tools/pandeia_refdata_wfirst
Successfully performed the default calculation for wfirstimager
Compressed WFIRST Pandeia data into /Users/jlong/software/wfirst-tools/pandeia_data_wfirst.tar.gz
```
