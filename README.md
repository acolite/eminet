# About EMINET
EMINET is the EMIssivity neural NET to derive thermal emissivity from multispectral VSWIR surface reflectance developed at RBINS. The network is trained on resampled ECOSTRESS data and can at present derive emissivity for Landsat 8/TIRS bands (B10 and B11) from the multispectral Landsat 8/OLI data (B1-7). The method and validation is presented in Vanhellemont, 2020 (https://doi.org/10.1016/j.isprsjprs.2020.06.007).

EMINET development was funded by the Belgian Science Policy Office BRAIN-be program under contract BR/165/A1/MICROBIAN.

**EMINET is provided by RBINS as an experimental tool, without explicit or implied warranty. Use of the program is at your own discretion and risk.**

## Dependencies
EMINET is coded in Python 3, and requires the following Python packages to run with all functionality:`numpy keras gdal netcdf4`

## Installation & Configuration
* Install dependencies in your Python environment, or create a new environment with e.g. conda: `conda create -n eminet -c conda-forge python=3 numpy keras gdal netcdf4`
and activate the environment: `conda activate eminet`
* cd into a suitable directory and clone the git repository: `git clone https://github.com/acolite/eminet`
* cd into the new tact directory `cd eminet`
* run `python eminet.py --input $in --output $out` where $in is the full path to an L2 surface reflectance Landsat 8 image, either the extracted bundle from LaSRC as processed by EarthExplorer Collection 1 Level 2 on demand processing (https://earthexplorer.usgs.gov) or an L2R.nc output from ACOLITE (https://github.com/acolite/acolite) and $out the full path to the target output directory (which will be generated).

## Options
* --use_water_defaults True/False Option to replace the emissivity for liquid water with the defaults
* --water_threshold float Threshold on the top-of-atmosphere reflectance at 1.6 micron to separate water/non-water
* --em_water_b10 float Set default water B10 emissivity
* --em_water_b11 float Set default water B11 emissivity

## Alternative use
EMINET can be imported in your Python code, if it is in your $PATH. For example:

            import sys, os
            user_home = os.path.expanduser("~")
            sys.path.append(user_home+'/git/eminet')
            import eminet as em

You can then process a single spectrum or a list of spectra, e.g.:

            inp = [[0.15588132,0.18297164,0.26016742,0.31183824,0.36371586,0.45715618,0.45273715],
                  [0.035160758,0.040426794,0.07381269,0.057351366,0.41716343,0.23558201,0.124089],
                  [0.03215484,0.040045694,0.052055236,0.02672039,0.008589883,0.0022362447,0.0017197328]]
            out1 = em.eminet_models(inp, netname='Net1', use_water_defaults=True)
            print('Net1 result', out1)
            out2 = em.eminet_models(inp, netname='Net2', use_water_defaults=True)
            print('Net2 result', out2)

Or a LaSRC or ACOLITE output file:

            inp = '/path/to/L8_OLI_2020_04_01_10_39_43_199024_L2R.nc' ## ACOLITE L2R NetCDF file
            output = '/path/to/output/ACOLITE'
            em.eminet_models(inp, output=output, netname='Net2', use_water_defaults=True)

            inp = '/path/to/LC081990242020051901T1-SC20201012094514' ## LaSRC L2 bundle directory
            output = '/path/to/output/LaSRC'
            em.eminet_models(inp, output=output, netname='Net2', use_water_defaults=True)
