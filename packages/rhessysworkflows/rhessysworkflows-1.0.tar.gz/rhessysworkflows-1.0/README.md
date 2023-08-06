RHESSysWorkflows			{#index}
=======================

This software is provided free of charge under the New BSD License. Please see
the following license information:

Copyright (c) 2013, University of North Carolina at Chapel Hill
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    - Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    - Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    - Neither the name of the University of North Carolina at Chapel Hill nor 
      the names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE UNIVERSITY OF NORTH CAROLINA AT CHAPEL HILL
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT 
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


Authors
-------
Brian Miles <brian_miles@unc.edu>

Lawrence E. Band <lband@email.unc.edu>

For questions or support contact [Brian Miles](brian_miles@unc.edu)


Funding
-------
This work was supported by the following NSF grants

- Award no. 1239678 EAGER: Collaborative Research: Interoperability
   Testbed-Assessing a Layered Architecture for Integration of
   Existing Capabilities

- Award no. 0940841 DataNet Federation Consortium.

- Award no. 1148090 Collaborative Research: SI2-SSI: An Interactive Software
   Infrastructure for Sustaining Collaborative Innovation in the
   Hydrologic Sciences


Introduction
------------
RHESSysWorkflows provides a series of Python scripts for performing
[RHESSys](http://fiesta.bren.ucsb.edu/~rhessys/) data preparation
workflows.  These scripts build on the workflow system defined by
[EcohydroLib](https://github.com/selimnairb/EcohydroLib).


Source code
-----------
Source code can be found at: https://github.com/selimnairb/RHESSysWorkflows

Documentation can be found at: http://pythonhosted.org/rhessysworkflows


Configuration files
-------------------
Many scripts in both RHESSysWorkflows and EcohydroLib
require a configuration file to specify locations to executables and
datasets required by the ecohydrology workflow libraries.  The
configuration file can be specified via the environmental variable
ECOHYDROLIB_CFG or via command line option. Here is an example
configuration file:

		[GDAL/OGR]
		PATH_OF_OGR2OGR = /Library/Frameworks/GDAL.framework/Versions/Current/Programs/ogr2ogr
		PATH_OF_GDAL_RASTERIZE = /Library/Frameworks/GDAL.framework/Versions/Current/Programs/gdal_rasterize
		PATH_OF_GDAL_WARP = /Library/Frameworks/GDAL.framework/Versions/Current/Programs/gdalwarp
		PATH_OF_GDAL_TRANSLATE = /Library/Frameworks/GDAL.framework/Versions/Current/Programs/gdal_translate
		
		[NHDPLUS2]
		PATH_OF_NHDPLUS2_DB = /Users/<myusername>/data/NHDPlusDB.sqlite
		PATH_OF_NHDPLUS2_CATCHMENT = /Users/<myusername>/data/Catchment.sqlite
		PATH_OF_NHDPLUS2_GAGELOC = /Users/<myusername>/data/GageLoc.sqlite
		
		[NLCD]
		PATH_OF_NLCD2006 = /Users/<myusername>/data/nlcd2006_landcover_4-20-11_se5.img
		
		[UTIL]
		PATH_OF_FIND = /usr/bin/find
		#PATH_OF_SEVEN_ZIP = /opt/local/bin/7z
		PATH_OF_SQLITE = /usr/bin/sqlite3
		
		[SCRIPT]
		ETC = /System/Library/Frameworks/Python.framework/Versions/2.7/rhessysworkflows/etc
		
		[GRASS]
		GISBASE = /Applications/GRASS-6.4.app/Contents/MacOS
		MODULE_PATH = /Library/GRASS/6.4/Modules/bin
		MODULE_ETC = /Library/GRASS/6.4/Modules/etc
		
		[RHESSYS]
		PATH_OF_GIT = /usr/bin/git
		PATH_OF_MAKE = /usr/bin/make

Prototype configuration files for OS X are available here: https://github.com/selimnairb/RHESSysWorkflows/tree/master/docs/config
We'll cover how to setup your configuration file during the installation process.
		

Installation instructions
-------------------------
These instructions are tailored to OS X users, however installation
under Linux is also possible.  Linux instructions will be provided in
the future.  In the mean time, Linux users should be able to follow
along to install the necessary dependencies and Python modules to use
RHESSysWorkflows; this is relatively easy to do via your distributions
package manager.  Note that if you are installing dependencies such as
GDAL under Linux, you will also need to install the 'devel' version of
these packages so that the header files necessary for compiling
against the libraries are available.  RHESSysWorkflows may in theory
work under Windows, but this has never been tested.  Windows users are
encouraged to run a Linux distribution under a virtual machine.

RHESSysWorkflows is compatible with OS X 10.6, 10.7, and 10.8.  To
find out what version of OS X you are currently running, click on the
apple in the upper left corner of the screen and select *About this
Mac*.  To find out the latest version of OS X you computer can run,
visit
http://www.everymac.com/systems/by_capability/maximum-macos-supported.html.

Due to its age, there are a few more installation steps needed under
OS X 10.6.  Also, once Apple stops support this version of the OS,
support for OS X 10.6 will also be dropped from subsequent releases of
RHESSysWorkflows.  If you were thinking of upgrading from OS X 10.6 to
10.7 or 10.8 for other reasons, this may add another.

### OS X 10.6 only: Install Python 2.7

#### Download and install Python 2.7 (for Mac OS 10.6 and later) from: http://www.python.org/download/

Once installation has completed, make sure that Python 2.7 is the
default Python version by doing the following from the Terminal:
    python
This will load the Python interpreter.  The first line of output will
display the Python version number.  Type *exit()* to exit the
interpreter.

#### Download setuptools from: https://pypi.python.org/pypi/setuptools/0.8
Install setuptools as follows:
1. Unpack the archive by double-clicking on it in Finder
2. From Terminal:
    cd setuptools-0.8
    sudo python ez_setup.py

### Install non-Python dependencies

#### OS X 10.6: Install Xcode (OS X developer tools)
1. Download and install Xcode 3.2.6 and iOS SDK 4.3 for Snow Leopard from https://developer.apple.com/downloads/index.action (This requires you to register for a free developer account)
2. Download and install Git from http://git-scm.com/download/mac

RHESSysWorkflows uses Git to download RHESSys source code so you don't have to.

#### OS X 10.7 and 10.8: Install Xcode (OS X developer tools):
1. Install Xcode via the App Store
2. Launch Xcode
3. Install 'Command Line Tools' from menu Xcode > Preferences... > Downloads

#### Install GIS tools: GRASS QGIS
Note, GRASS version 6.4.2 is required for RHESSysWorkflows.  GRASS is
used internally to carry out workflow steps (leading to the creation
of RHESSys world files and flow tables).  You will also find it useful
to use GRASS to visualize the results from some workflow steps.

To install GRASS on OS X, visit http://www.kyngchaos.com/software/grass

Here you will need to download and install the following:
1. GDAL Complete 1.9 framework
2. FreeType framework
3. cairo framework
4. GRASS.app

While you are there, I recommend you also install QGIS (Quantum GIS) from http://www.kyngchaos.com/software/qgis

In addition to GRASS and components installed above, install:
1. GSL framework
2. QGIS

QGIS is useful for visualizing output for earlier workflow steps that precede the importing data into GRASS. 

#### Install GRASS Addons for RHESSysWorkflows
Download and install GRASS addons from: http://ecohydrology.web.unc.edu/files/2013/07/GRASSAddons-RHESSysworkflows.dmg_.zip

For non-OS X users, these addons (r.soils.texture and r.findtheriver)
are also available for installation from the GRASS addons repository
via g.extension.  You can download r.findtheriver
[here](http://grasswiki.osgeo.org/wiki/AddOns/GRASS_6#r.findtheriver)
and r.soils.texture
[here](http://grasswiki.osgeo.org/wiki/AddOns/GRASS_6#r.soils.texture)

### Install Python modules
#### Install PIP, a tool for installing Python modules
Pip is the recommended way to install Python modules (i.e. rather than
using easy_install). For example, Pip allows you to easily uninstall
modules.  To install pip, enter the following in a Terminal window:

    sudo easy_install pip

#### OS X 10.6: Install GDAL Python modules
Even though we installed the GDAL complete framework above, we still
need to install the GDAL Python modules for the copy of Python 2.7 we
installed above; the GDAL framework only installs the Python modules
for Python 2.6, which RHESSysWorkflows is not compatible with. These
installation steps are a little ugly, but bear with me (or upgrade
from OS X 10.6). From a Terminal window type the following:

    export PATH=${PATH}:/Library/Frameworks/GDAL.framework/unix/bin
    sudo pip install --no-install GDAL
    cd /tmp/pip-build-root/GDAL
    sudo python setup.py build_ext --include-dirs=/Library/Frameworks/GDAL.framework/Headers --library-dirs=/Library/Frameworks/GDAL.framework/Versions/Current/unix/lib
    sudo pip install --no-download GDAL

#### Install RHESSysWorkflows Python modules (including EcohydroLib) 
To install RHESSysWorkflows and its dependencies (including EcohydroLib), enter the following from your Terminal:

    sudo pip install rhessysworkflows

This may take a while as several of the modules rely on non-Python code that has to be compiled.
    
> Why are GDAL Python libraries not included as a dependency of
> RHESSysWorkflows? This is to make life easier for users of OS X 10.7
> and 10.8.  For these OSes, the GDAL complete installer that
> accompanies GRASS will install GDAL Python modules in the copy of
> Python 2.7 that ships with the OS, and the GDAL Python module does
> not successfully build by itself under OS X, which would make the
> rhessysworkflows install fail.  Linux users will have to make sure
> they install GDAL Python modules in addition to GDAL itself
> (e.g. via a companion package, or by 'sudo pip install GDAL').

### Install local data
RHESSysWorkflows allows you to use the National Hydrography Dataset
Plus (NHD Plus) to locate USGS streamflow gages, or use the National
Landcover Dataset (NLCD 2006). Unfortunately, these are large datasets
and this are currently no way to query subsets of these data over the
web.  If you want to use NHDPlus or NLCD2006 in your workflows, you
will have to download local copies of these datasets.
 
#### Setup NLCD2006 data [optional]
If you want to use NLCD2006 land cover data, do the following:
- Download NLCD2006 data [here](https://docs.google.com/file/d/0B7aK-9pTSLS-MHRrRTVVRV9zdVk/edit?usp=sharing)

    It is important that you download this version of the dataset, and not the official data from 
    http://www.mrlc.gov/nlcd06_data.php.  The offical data are packaged using a version of PkZip that
    is not compatible with OS X's GUI or commandline unzip utilities.

- Copy NLCD2006 archive to the parent folder where you would like to store it

    For example, under OS X, create a folder called 'data' in your home directory

- Unpack NLCD2006 data by double-clicking on the archive

#### Setup pre-packaged NHDPlusV2 data [optional]
If you want to determine your study area based on an NHD catchment
drained by a USGS streamflow gage, you will need a local copy of the
NHDPlusV2 data.  You can obtain these data by downloading all or a
subset of the NHDPlusV2 data and building the database as described in
the [EcohydroLib documentation](https://github.com/selimnairb/EcohydroLib).
Alternatively, you can download a pre-built copy of the NHDPlusV2
database needed by RHESSysWorkflows
[here](https://docs.google.com/file/d/0B7aK-9pTSLS-dGVzWGRCd1NwNzQ/edit?usp=sharing).
To download and unpack the pre-built data, do the following:

- Download pre-packaged NHDPlusV2 database [here](https://docs.google.com/file/d/0B7aK-9pTSLS-dGVzWGRCd1NwNzQ/edit?usp=sharing)

    Note, the compressed data are nearly 7 GB, nearly 11 GB uncompressed, the download may take a while

- Copy the pre-packaged NHDPlusV2 database archive to the parent folder where you would like to store it
    
    For example, under OS X, create a folder called 'data' in your home directory

- Unpack NHDPlusV2 database archive
    
    For example, under OS X, double-click on the NHDPlusV2 archive. Note, this may take a while to unpack

### Setup EcohydroLib and RHESSysWorkflows configuration file
- Choose the appropriate prototype configuration file from https://github.com/selimnairb/RHESSysWorkflows/tree/master/docs/config
- Copy and paste the prototype configuration into a text file named '.ecohydro.cfg'
- Save '.ecohydro.cfg' in your home directory
- Modify the example configuration to point to your NHDPlusV2 and NLCD2006 data:

    If you are using OS X, and if you placed the data in a directory called 'data' in your
    home directory, the only changes you need to make is to substitute '<myusername>' with your user name.
    To find out your OS X user name, use the *whoami* command in Terminal
    
- Set ECOHYDROLIB_CFG environment variable so that RHESSysWorkflows can find your configuration file
    For example, under OS X, from Terminal, do the following:
	+ Open your bash profile in an editor:
		nano ~/.bash_profile
	+ Add the following at the end of the file:
		export ECOHYDROLIB_CFG=${HOME}/.ecohydro.cfg
	+ Save the file
	+ Re-load bash profile (or close and open a new Terminal window):
		source ~/.bash_profile


Using RHESSysWorkflows - Introduction
-------------------------------------
All EcohydroLib and RHESSysWorkflows scripts are executed from the
command line.  Each script stores the data and metadata associated
with a single workflow in a directory, called a *project directory*.
Metadata are stored in a file in the project directory called
*metadata.txt*.  There can only be one metadata.txt in a project
directory, so it is essential that each workflow have its own project
directory.

In addition to automatically recording provenance information for data
and the processing steps of a workflow, the metadata store allows for
loose coupling between the scripts that are used to carry out a
particular workflow. By design, each workflow script performs roughly
one discrete function.  This allows for flexible workflows. Each
workflow script writes a series of entries to the metadata to reflect
the work done by the script.  Most workflow scripts require certain
entries to be present in the metadata store to perform the work they
will do.  For example, before DEM data for the study are can be
downloaded from DEMExplorer, the bounding box for the study area must
be known. The script that queries DEMExplorer need not know how the
bounding box was generated, it only cares that the bounding box is
present in the metadata store.  Lastly, the metadata store helps users
to orchestrate workflows by requiring that only new information
required at each step be entered to run a particular command, other
information required can be queried from the metadata.

Each workflow script will print usage information when run on its own
for example running:
    GetNHDStreamflowGageIdentifiersAndLocation.py 
Will yield:
    usage: GetNHDStreamflowGageIdentifiersAndLocation.py [-h] [-i CONFIGFILE] -p
    PROJECTDIR -g GAGEID
    GetNHDStreamflowGageIdentifiersAndLocation.py: error: argument -p/--projectDir is required

This indicates that the -p (a.k.a. --projectDir) argument is required;
that is, you must specify the project directory associated with
workflow for which you are running the script.  For many
EcohydroLib/RHESSyWorkflows scripts, this is the only required command
line parameter.  

It's good practice when running a command to first execute the command
with no command line arguments.  This will show you the required and
optional parameters.  To get detailed help for a given command, run
the command with the -h (a.k.a. --help) argument, for example:

    GetNHDStreamflowGageIdentifiersAndLocation.py -h
 
Note that while this particular script, and RHESSysWorkflows scripts
in general, have long names, they are long to be descriptive so as to
be easier to use.  To avoid having to type these long names out, you
are encouraged to make use of *tab* completion in Terminal.  To use
tab completion, simply type the first few characters of a command and
then hit the 'tab' key on your keyboard; the entire command name will
be 'completed' for you on the command line.  If the entire name is not
'completed' for you, hit tab again to see that list of commands that
match what you've typed so far.  Once you type enough characters to
uniquely identify the command, hitting tab once more will complete the
command name.


Using RHESSysWorkflows - Typical workflows
------------------------------------------
A typical workflow will consist of running data
processing/registration scripts from EcohydroLib.  Once the required
datasets are in place (e.g. DEM, soils, landcover, etc.)
RHESSysWorkflows scripts can be run to create the world file and flow
table associated with a RHESSys model.

In the following sections two example workflows are described: (1)
using data from national spatial data infrastructure (USGS, NHD, NLCD,
SSURGO, SRTM); and (2) using custom local data.  These combination of
scripts executed in these workflows represent two of the many unique
workflows possible.

### National spatial data workflow

Start by creating a directory called 'standard'.  This will be your
project directory for this example workflow.  You can create this
directory anywhere on your computer where you have write access
(e.g. in your home directory).

#### Specify a USGS streamflow data to locate on the NHD network

First, choose the USGS streamflow gage, identified by the USGS site
number, you wish to build a RHESSys model for.  Note that while you
can select gages that drain large basins, if you are planning to use
SSRUGO soils data acquired using the RHESSysWorkflows script
GetSSURGOFeaturesForBoundingbox.py the study area must be less than
10,000 sq. km.

To locate the USGS gage of interest on the NHD flow line network run
the following script:

    GetNHDStreamflowGageIdentifiersAndLocation.py -p standard -g 01589312

This will create the metadata store for your project in a file named
metadata.txt in the project directory 'standard'.  The metadata store
will be populated with the gage ID (the site number you specified on
the command line), and the NHD reachcode and reach measure associated
with this gage.

#### Extract NHD catchments that drain through the streamflow gage

The NHD database relates stream flowlines to the catchments that drain
into them.  RHESSysWorkflows can use these catchments, stored in a
shapefile in your project directory, to determine the geographic
bounding box for your study area (see below).  This bounding box can
then beused extract spatial data for your study area from datasets
stored locally as well as those available via web services interfaces.

To extract a shapefile of the NHD catchments that drain through your
streamflow gage, run the following script:

    GetCatchmentShapefileForNHDStreamflowGage.py -p standard

You should now see the study area shapefile in your project directory.
You can visualize the study area, along with the streamflow gage, in
QGIS.  Note that the study area shapefile does not represent the
delineation of your watershed, but should instead be a superset of the
watershed.  We will delineate your watershed using GRASS GIS.

#### Get bounding box for study area

Now that RHESSysWorkflows has a GIS representation of your study area,
it can determine the extent or bounding box (also sometimes called the
'minimum bounding rectangle') of the study area.  Do so by running the
following script:

    GetBoundingboxFromStudyareaShapefile.py -p standard

As with many EcohydroLib/RHESSysWorkflows commands, you won't see much
in the way of output printed to the screen; don't fear.  The commands
are writing what's needed for future workflow steps to the metadata
store associated with your project directory.  If you open the
metadata store, the file called *metadata.txt* in the project
directory *standard*, you can see the bounding box coordinates stored
in the *study_area* section; look for the attribute named
*bbox_wgs84*.

#### Acquire terrain data from DEM Explorer

[DEM Explorer](http://geobrain.laits.gmu.edu), developed and
maintained by the Center for Spatial Information Science and Systems
at George Mason University in partnership with NASA EOS, provides
web-based access to USA and global DEM data from a number of data
sources (currently SRTM, GLS, ASTER, and GTOPO).  In addition to a
browser-based interface, DEM Explorer provides an HTTP query service
to allow applications such as EcohydroLib to programmatically query
and download DEM data.  Now that we've defined the bounding box for
our study area, its very easy to download DEM data from DEM Explorer,
as follows:

    GetDEMExplorerDEMForBoundingbox.py -p standard

By default, this script will download an extract for your study area
from the SRTM 30-meter (27.58-meter actual) USA DEM.  The DEM will be
stored in a UTM project (WGS84 datum) with the appropriate UTM zone
chosen for you.  You can override both the DEM coverage type and
target spatial reference system by specifying the appropriate command
line parameters; spatial reference systems must be refered to by their
EPSG code (see http://www.spatialreference.org/ref/epsg/ for more
information).  Additionally, you can choose to resample the DEM
extract to another spatial resolution.  To learn how to specify these
options, issue the help command line argument as follows:

    GetDEMExplorerDEMForBoundingbox.py -h

Note that EcohydroLib/RHESSysWorkflows uses the DEM resolution,
extent, and sptial reference the reference for all other rasters
imported into or generated by subsequent workflow scripts.

Lastly, you are not required to use a DEM from DEM Explorer.  See the
*Custom local data workflow* example below for more information.

#### Extract landcover data from local NLCD 2006 data

At the time of writing there was not a web service interface to the
NLCD 2006 data, thus it is necessary to download the entire dataset
and store it locally if you wish to use these data in EcohydroLib
workflows.  Fortunately, once downloaded and listed in the
ecohydro.cfg file (see installation instructions above), EcohyodroLib
makes it easy to import custom NLCD2006 tiles for your study area into
your project, for example

    GetNLCDForDEMExtent.py -p standard

Will extract a tile matching the extent, resolution, and spatial
reference of your DEM and store the tile in your project directory.
If you wish to give your NLCD tile a particular name, use the
*outfile* command line option.

#### Download soils data from SSURGO

The USDA NRCS provides the [Soil Data
Mart](http://soildatamart.nrcs.usda.gov), a sophisticated web
services-based interface for querying and downloading high-resolution
SSURGO soils data.  SSURGO data are structured as a complex database
consisting of both spatial and tabular data.  For more information on
this database format and the soil survey data exposed through the
SSRUGO database please see the [SSURGO
metadata](http://soildatamart.nrcs.usda.gov/SSURGOMetadata.aspx).

EcohydroLib provides two scripts that make it easy to generate soil
hydraulic properties commonly needed for ecohydrology modeling (namely
the numeric properties Ksat, porosity, percent sand, percent silt, and
percent clay).  The first script downloads spatial mapunit features
for your study area as well as tabular soil hydraulic property data.
These spatial and tabular data are joined, and written to your project
directory as an ESRI Shapefile.  For more information on what
attributes are queried and how non-spatial mapunit commponents are
aggregated by the code, please see the EcohydroLib source code
[here](https://github.com/selimnairb/EcohydroLib/blob/master/ecohydrolib/ssurgo/featurequery.py)
and
[here](https://github.com/selimnairb/EcohydroLib/blob/master/ecohydrolib/ssurgo/attributequery.py).

To download SSURGO features and attributes into your project, run the
following command:

    GetSSURGOFeaturesForBoundingbox.py -p standard

Note that for server performance and network bandwidth issues, Soil
Data Mart limits SSURGO spatial queries to areas of less than roughly
10,000 sq. km.  If your study area is larger than this, you may wish
to obtain a copy of the SURRGO data and extract your own soils data.
In the future we hope to address this limitation by hosting a copy of
SSURGO at UNC, however this work is still underway.

You can visualize the downloaded SSURGO features and joined tabular
data by opening the shapfile in QGIS.  The SSURGO shapefile has a
long, though descriptive, name that includes the bounding box
coordinates for your study area.  If you are unsure what shapefile in
your project directory to open, the *soil_features* attribute of the
*manifest* section of your metadata store lists the filename.  

> While you're looking at the metadata store, scroll down to the
> *provenance* section.  While the attribute names are a bit messy,
> you can see that for each manifest entry, there EcohydroLib has
> recorded detailed provenance information.  For the SSURGO soil
> features, the Soil Data Mart web services URL is listed as the
> datasource; for the DEM data downloaded from DEM Explorer,
> EcohydroLib records the exact URL used to download your DEM.
> Lastly, if you scroll down a bit farther, you can see that the
> *history* section of the metadata store records the order of every
> EcohydroLib/RHESSysWorkflow command you've run in this workflow,
> including all of the command line parameters.

EcohydroLib provides a second script for detailing with SSURGO soils
data.  This script allows you to create raster maps of SSURGO mapunit
polygons using the following numeric soil properties as raster values:
Ksat, porosity, percent clay, percent silt, and percent sand).  Use
the following command to generate all of these rasters in your project
directory:

    GenerateSoilPropertyRastersFromSSURGO.py -p standard

Later on in this example workflow, we'll use the percent sand and
percent clay rasters to generate a USDA soil texture map, which we'll
use to define RHESSys soil parameters for our study watershed.

#### Registering custom local data: LAI data 

EcohydroLib does not current provide direct access to vegetation leaf
area index data from remote sensing sources, though we are working to
make available Landsat LAI data generated from the Landsat archive on
[NASA NEX](https://c3.nasa.gov/nex/).  LAI data are needed by RHESSys
to initialize vegetation carbon and nitrogen stores.  RHESSysWorkflows
relies can use a user-supplied LAI rasters to supply these initial LAI
data to RHESSys.  For this example workflow, you can download an LAI
image
(here)[https://docs.google.com/file/d/0B7aK-9pTSLS-eEJaZXctaEtkb2s/edit?usp=sharing].
Use the following command to register this user-supplied raster into
your project:

    RegisterRaster.py -p standard -t lai -r /path/to/static_lai-01589312.tif -b "Brian Miles <brian_miles@unc.edu>"

To make this command work, you'll have to change the path to the file
name passed to the *-r* argument to reflect the location on your
computer to which you downloaded the example LAI image.  

> Note that EcohydroLib/RHESSysWorkflows do not work with files or
> directories whose names contain spaces.  This will be addressed in a
> future release.

Also, the extent of the LAI image doesn't quite match that of our DEM.
By default, RegisterRaster will not import a raster that does not
match the extent of the DEM.  Use the *--force* option to force
RegisterRaster to import the raster:
    
    RegisterRaster.py -p standard -t lai -r /path/to/static_lai-01589312.tif -b "Brian Miles <brian_miles@unc.edu>" --force

When using the *force* option, it is even more important that you
check the results of the command to ensure the data registered with
the workflow are appropriate for the modeling you plan to perform.  Go
ahead and browse to your project directory, find the DEM and LAI
rasters and open them in QGIS (you will likely have to set a color map
for each, otherwise all values will render in grey).

Note the *-b* (a.k.a. *--publisher*) argument given to the above
command.  When specified, this optional parameter will be stored in
the provenance matadata store entry of the raster.

RegisterRaster is a generic EcohydroLib script that knows how to
import several types of raster into your workflow; the *-t lai*
argument indicates that we are importing an LAI raster (see the
*Custom local data workflow* for to learn how to import other raster
types).  RegisterRaster will copy the raster being imported into your
project directory; the raster will be resampled and reprojected to
match the resolution and spatial reference of the DEM already present
in the workflow.  You can choose the resampling method to use, or turn
off resampling, though the raster will be resampled if the spatial
reference system does not match that of the DEM; see the help message
for more information.

At this point, we have enough spatial data in a generic format
(e.g. GeoTIFF) to build RHESSys-specific datasets using RHESSysWorkflows.

#### Create a new GRASS location 

RHESSys requires that all spatial data used to create a world file and
flow table for a RHESSys model be stored in a GRASS GIS mapset.  We'll
start building these data in RHESSysWorkflows by creating a new GRASS
location and mapset within our project directory, and importing our
DEM into this mapset:

    CreateGRASSLocationFromDEM.py -p standard -d "RHESSys model for Dead Run 5 watershed near Catonsville, MD"

The *-d* (a.k.a. *--description") parameter is a textual description
of this GRASS location; always wrap this parameter in quotes.  If you
choose, you can specify custome names of the following GRASS
parameters:

1. dbase, the directory within the project directory where your GRASS
location will be stored (defaults to 'GRASSData') 
2. location (defaults to 'default')
3. mapset (defaults to 'PERMANENT')

> Use the *--overwrite* option to CreateGRASSLocationfromDEM to
> overwrite the GRASS location created by a previous invocation of
> CreateGRASSLocationFromDEM.  Note that most RHESSysWorkflows
> commands provide the same option.  The ability to overwrite GRASS
> datasets accomodates the often exploratory nature of ecohydrology
> data preparation workflows.  While the data will be overwritten, the
> command history stored in the metadata store will retain a listing
> of the order in which you ran all workflow steps.  This can help you
> to retrace the steps you took to arrive at the current workflow
> state.

Go ahead and open GRASS, pointing it to the dbase in your project
directory, and then opening the mapset *PERMANENT* in the location
*default*.  You should be able to load the DEM raster into the map
view.  We'll use GRASS to visualize the results of the next few
workflow steps, so keep GRASS open in the background.

#### Import RHESSys source code into your project

To create worldfiles and flow tables RHESSysWorkflows needs a copy of
RHESSys source code.  RHESSysWorkflows also uses the new RHESSys
[ParamDB](https://github.com/RHESSys/ParamDB) database and Python
libraries to generate vegetation, soil, land use and other parameters
needed by RHESSys.  RHESSysWorkflows is only compatible with the
pre-release version of RHESSys 5.16 and later versions of the code.
At present, and for first-time users, the most reliable way to import
ParamDB and RHESSys source code into your project is to download the
code from GitHub using the ImportRHESSysSource script.  However, this
script is also capable of importing RHESSys source code stored on your
computer.  This alows you to import the code from a previous
RHESSysWorkflows project; ParamDB is always downloaded from GitHub,
even when RHESSys source code is imported from a local source.

To download ParamDB and the RHESSys source code and store them in your
project directory issue the following command:

    ImportRHESSysSource.py -p standard -b develop

The *-b* options specifies the Git branch of RHESSys to use, in this
case the *develop* branch.  By default, ImportRHESSysSource will use
the *master* branch, which will be the appropriate branch to use once
RHESSys 5.16 is officially released (ca. August 2013).
	
Once ImportRHESSysSource finishes importing RHESSys source code into
the project directory, it will compile all the tools necessary to
create world files and flow tables, while also compiling the RHESSys
binary.  Once the command finishes, open the *rhessys* directory in
your project directory.  Here you can see the familiar RHESSys
directory structure for storing model parameters, templates,
worldfiles, flow tables, temporal event files, and model output; the
RHESSys tools compiled by ImportRHESSysSource will be copied into the
*bin* directory of the *rhessys* directory.  Also note that all the
source code for RHESSys is stored in the *src* directory.

#### Import RHESSys climate data 

Because of the greater variability of climate data formats, and the
complexity of time-series workflows, we have chosen to focus
development effort on RHESSysWorkflows toward making it easier to
acquire and manipulate geospatial data required for building RHESSys
work files and flow tables.  This means that the modeler is
responsible for building the climate data necessary for building
RHESSys world files and performing model runs.  

RHESSysWorkflows provides the ImportClimateData script to import
RHESSys climate data into your project.  To run this example workflow,
download example climate data
[here](https://docs.google.com/file/d/0B7aK-9pTSLS-Q1NQbUJzVXZKeUE/edit?usp=sharing).
Unzip the file to a location on your computer (e.g. in your home
directory), this will result in a directory named *clim* in the
location.  Issue the following command to import these data:

    ImportClimateData.py -p standard -s /path/to/clim

You will have to replace */path/to/clim* with the path of the clim
folder unpacked from the zip file downloaded above.  

For your own climate data to work with ImportClimateData the data must
be stored in their own directory, with each base station having file
name that ends in *.base*.  See the help for ImportClimateData for
more information.

#### Delineate watershed and generate derived data products

RHESSysWorkflows automates the process of delineating your study
watershed based on the location of the streamflow gage registered in
the workflow.  As part of this process, many datasets needed by
RHESSys will be derived from the DEM.  To delineate the watershed:

    DelineateWatershed.py -p standard -t 500 -a 1.5

Here the *-t* (a.k.a. *--threshold*) parameter specifies the minimum
size (in DEM cells) for subwatersheds generated by the GRASS command
[r.watershed](http://grass.osgeo.org/grass64/manuals/r.watershed.html).

The *-a* (a.k.a. *--areaEstimate*) parameter allows you to provide a
guess of the area (in sq. km) of the delineated watershed.
DelineateWatershed will report whether the watershed is within 20% of
the area.  You can view the delinated watershed in GRASS by displaying
the raster map named *basin*.  If the area or the shape of the
delineated watershed differs greatly from what you expect, you may
need to vary how DelineateWatershed snaps your streamflow gage onto
the stream network.  This is accomplished by changing the *-s*
(a.k.a. *--streamThreshold*) or stream threshold parameter passed to
[r.findtheriver](https://svn.osgeo.org/grass/grass-addons/grass6/raster/r.findtheriver/description.html).

To debug watershed delineation problems, it is also helpful to view
the original streamflow gage and the snapped streamflow gage overlaid
on the upslope accumulated area map (UAA). DelineateWatershed will
create vector layers for each of the streamflow gage coordinants
(named *gage* and *gage_snapped*) as well as a UAA raster map (named
*uaa*).

> Though we do not recommend that you make changes to the metadata
> store by hand, as a last resort, you can snap the gage location by
> hand using GRASS and update the *gage_easting_raw* and
> *gage_northing_raw* attributes in the *rhessys* section of the
> metadata store.  Then re-run DelineateWatershed as before with the
> addition of the *--overwrite* option.

For a listing of the derived datasets generated by DelineateWatershed,
use the GRASS command *g.list rast* or check the DelineateWatershed
[source
code](https://github.com/selimnairb/RHESSysWorkflows/blob/master/bin/DelineateWatershed.py).

#### Generating a patch map

RHESSysWorkflows provides GeneratePatchMap, an automated script for
creating gridded and clumped patch maps.  Gridded patch maps consist
of a regular grid of the same resolution and extent as the DEM;
clumped maps can be created using elevation or topographic wetness
index rasters.  Modelers can also use custom patch maps registered via
EcohydroLib's RegisterRaster script and imported into GRASS using
ImportRasterMapIntoGRASS (see below for a general description of this
command).

To create a gridded patch map, enter the following into your Terminal:

    GeneratePatchMap.py -p standard -t grid

To create an elevation clumped patch map:

    GeneratePatchMap.py -p standard -t clump -c elevation

... and a topographic wetness index clumped map:

    GeneratePatchMap.py -p standard -t clump -c wetness_index

Clumped patch maps are generated by calling GRASS's r.clump command
with the appropriate source raster as import.

#### Generating soil texture map

Since we used EcohydroLib's SSURGO scripts to generate percent sand
and percent clay raster maps for our watershed, we can use the GRASS
addon r.soils.texture to generate USDA soil texture classes, for which
RHESSys's ParamDB contains parameters.  It is also possible to use
custom soil maps, which we'll explore in the *custom local data
workflow* section below.

To generate our soil texture map in GRASS, as well as the
corresponding RHESSys soil definition files, use the
GenerateSoilTextureMap script as follows:

    GenerateSoilTextureMap.py -p standard

This command will print information about what soil texture classes
were encountered in the soil texture map, and what RHESSys soil
default IDs these classes map onto.  You can view the resulting soil
texture map (named *soil_texture*) in GRASS.  The soil definition
files will be stored in the *defs* directory of th *rhessys* directory
stored in your project directory.

#### Import LAI map into GRASS

We'll use the general command ImportRasterMapIntoGRASS to import our
LAI map from the project directory into GRASS, where RHESSys will be
able to make use of it:

    ImportRasterMapIntoGRASS.py -p standard -t lai -m nearest

The *-m* (a.k.a. *--method*) paramer specifies how GRASS should
resample the raster being imported.  Value resampling methods are
those supported by GRASS's
[r.resamp.interp](http://grass.osgeo.org/grass64/manuals/r.resamp.interp.html)
command, as well as *none*, which will cause ImportRasterMapIntoGRASS
to skip the resampling step.

#### Generate landcover maps in GRASS

RHESSysWorkflows uses a single landcover map to generate the following maps
used by RHESSys:

- Vegetation type (stratum)
- Land use
- Roads
- Impervious surfaces

The first step in generating these maps is to import the landcover
raster from your project directory into GRASS using
ImportRasterMapIntoGRASS:

    ImportRasterMapIntoGRASS.py -p standard -t landcover -m nearest

In our case, the landcover map in our project directory came from our
local copy of NLCD2006.  However, RHESSysWorkflows supports the use of
custom landcover maps regsitered via RegisterRaster.  In either case,
we need to provide raster reclassification rules so that
RHESSysWorkflows will know how to generate vegetation, land use,
roads, and impervious surface maps from the landcover map.  To do
this, we use the RegisterLandcoverReclassRules script:

    RegisterLandcoverReclassRules.py -p standard -k

NLCD2006 is a known landcover type in RHESysWorkflows (the only one),
so all we need do is use the *-k* (a.k.a. *--generateKnownRules*)
option.  For a custom landcover map, we could instead use the *-b*
(a.k.a. *--buildPrototypeRules*) option to generate prototype rules
that we can edit as needed.  It is also possible to specify that
existing reclass rules should be imported from another directory on
your computer using the *-r* (a.k.a. *--ruleDir*) parameter.

Whether using known rules, building prototype rules, or importing
existing rules, RegisterLandcoverReclassRules will result in the
following four rules files being created in the *rules* directory of
your project directory:

- stratum.rule
- landuse.rule
- impervious.rule
- road.rule

There is no need to edit these rules for this NLCD2006 example, but
you should take a moment to look at how these rules work.
RHESSysWorkflows uses GRASS's
[r.reclass](http://grass.osgeo.org/grass64/manuals/r.reclass.html)
command, and so the rules files follow this format.  It's important to
note that your landcover reclass rules must result in raster maps
whose values labels match class names present in the RHESSys ParamDB
database.  Thus, be very carful in editing the righthand side of the
expressions in your reclass rules.

> You can find information on NLCD2006 classes [here](http://www.mrlc.gov/nlcd06_leg.php)

Once the landcover reclass rules are in place, it is very easy to
generate the raster maps derived from the landcover data as well as
the vegetation and land use definition files needed by RHESSys; this
is done using the following command:

    GenerateLandcoverMaps.py -p standard

Like with the soil texture map and definition generation step,
GenerateLandcoverMaps will provide descriptive output of the
vegetation and land use definition types encountered in the raster
data.

#### Creating the worldfile for a watershed

We are finally ready to create the worldfile for our watershed.  Note
that we haven't discussed creating or editing a worldfile template.
In general it should not be necessary for you to edit a template when
using RHESSysWorkflows.  The reason is, at this point in the workflow,
the metadata store contains nearly all the information necessary to
create the worldfile and the template.  The CreateWorldfile script
will generate the template for your, and then call the grass2world
RHESSys program to generate the worldfile.  All you need do is specify
which of the climate base stations you previously imported you with to
associate with the worldfile:

    CreateWorldfile.py -p standard -c bwi -v

Here we're using the climate station named *bwi*.  Note also that
we've specified the the *-v* (a.k.a. *--verbose*) command line option.
This will print details about what CreateWorldfile, and the programs
it runs on your behalf, is doing.  This is recommended as these
programs can fail in complex ways that CreateWorldfile may not be able
to detect, so you'll likely want to know what's going on under the
hood.

When CreateWorldfile finishes, it will create an initial worldfile
named *worldfile_init* in the *worldfiles* directory in the *rhessys*
directory in your project directory.  Additionally, the template used
to create the worldfile will be saved as *template* in the *templates*
folder of the *rhessys* folder.  Currently, this template will be
regenerated each time CreateWorldfile is run.  However the next
release of RHESSysWorkflows will separate the creation of the template
from the creation of the worldfile, allowing you to customize the
generated template before grass2world is called.  In the mean time,
there is nothing to stop you from editing the template and re-running
grass2world by hand.

#### Creating the flow table

As with worldfile creation, at this point in the workflow,
RHESSysWorkflows's metadata store contains nearly all the information
needed to create a flow table using the createflowpaths (CF) RHESSys
program.  The two choices you have are whether CF should create a flow
table that includes roads and/or includes a sufrace flow table to
modeling non-topographic routing of rooftops.  We'll route roads in
this example, leaving rooftops for the *custom local data* workflow
discussed below.

Run CreateFlowtable as follows:

    CreateFlowtable.py -p standard --routeRoads

This will result in the creation of a flow table called *world.flow*
in the *flow* directory of your *rhessys* directory.  Now we have
almost everything we need to run RHESSys simulations.

#### Initializing vegetation carbon stores

RHESSys provides a program called LAIread to initialize vegetation
carbon stores in your worldfile.  Initializing carbon stores is a
multi-step process that involves running LAI read to generate a
redefine worldfile, running a 3-day RHESSys simulation to incorporate
the redefine worldfile, writing out a new worldfile with initialized
vegetation carbon stores.  RHESSysWorkflows automates all of these
processes for you, it can even figure out what date to start the 3-day
RHESSys simulation on based on your climate data.

> In the current version of RHESSysWorkflows, RunLAIRead is only able
> to read simulation start dates from point time-series climate data.
> Users of ASCII or NetCDF gridded climate data must run LAI read by
> hand.  The next release of RHESSysWorkflows will add support for
> gridded climate data to RunLAIRead.

You can run RunLAIRead as follows:

    RunLAIRead.py -p standard -v

Note that we use the verbose command line option here as well.  The
new GRASS-based version of LAIread is relatively new and not as well
tested, so we advise you to keep a close watch on what it is doing.

LAIread relies on allometric relationships to initialize vegetation
carbon stores.  These allometric parameters have not yet been added to
RHESSys ParamDB.  A default version of the parameters for RHESSys base
vegetation classes is stored in the RHESSys source code
[repository](https://github.com/RHESSys/RHESSys/blob/develop/util/templates/allometric.txt).
RHESSysWorkflows stores this file under the name *allometric.txt* in
the *templates* folder of your *rhessys* folder.  You can edit this
file to suit your needs before running RunLAIRead.  Consult the
[RHESSys wiki](http://wiki.icess.ucsb.edu/rhessys/index.php/Main_Page) for more information on allometric relationships used
by LAIread.

When finished, a final worldfile named *world* will be created in the
*worldfiles* directory of your *rhessys* directory.  With this
worldfile, you are ready to perform subsequent model workflow steps
including: spin-up, calibration, scenario runs, and analysis and
visualization.

This concludes this tutorial using RHESSysWorkflows to create a
RHESSys world file and flow table using standard spatial data
infrastructure.

### Custom local data workflow

The following sections outline how one might use RHESSysWorkflows to
build RHESSys input files using custom data already available on your
computer.  Unlike the above standard spatial data tutorial, we won't
provide data for the workflow steps below.  Instead, we'll describe
how your data should be formatted to work with each workflow script.
To avoid duplication, only those concepts specific to using local data
in RHESSysWorkflows will be discussed.  You are encouraged to read the
standard spatial data tutorial above as well.  The workflow sequence
covered below is not the only possible workflow involving local data.
Also, it is possible to combine steps from this example workflow with
steps from the standard spatial data tutorial.

#### Import a DEM into your project

When working in watersheds outside the coverage of the NHD (such as
when working outside of the U.S.) the first workflow step is to import
a digital elevation model data using the RegisterDEM script.  The DEM
to be imported must be in a format readable by
[GDAL](http://www.gdal.org/formats_list.html).  

Run RegisterDEM as follows:

    RegisterDEM.py -p PROJECT_DIR -d /path/to/my/DEM.tif -b "City of Springfield, Custom LIDAR"

To run this command, replace *PROJECT_DIR* with the absolute or
relative path of an empty directory where you would like the data and
metadata for your project to be stored (i.e. your project directory).
It is also possible to reproject or resample the DEM on import.  See
RegisterDEM's help for more information (i.e. run with the *-h*
option).

RegisterDEM will result in the DEM being copied to your project
directory, also the DEM extent will be used to determine the bounding
box for the study area; a polygon of the DEM extent will be generated
and saved as a shapefile in your project directory.

#### Import streamflow gage coordinates 

The coordinates of the streamflow gage associated with your watershed
are registered with the workflow using the RegisterGage script.  The
script takes as input a point shapefile containing one or more points;
the WGS84 lat-lon coordinates for the desired gage will be extracted
from the shapefile.  These coordinates will be written to the metadata
store, and a new point shapefile containing a point only for the
selected gage will be created in the project directory.

A typical way to run RegisterGage is:

    RegisterGage.py -p PROJECT_DIR -g /path/to/gage/shapefile.shp -l DATASET_NAME -a GAGE_ID_ATTRIBUTE -d GAGE_ID

To run this comment, replace *PROJECT_DIR* as above, specify the input
shapefile you'd like to use, the name of the dataset within the
shapefile, the name of the ID gage attribute in the dataset, and the
ID of the desired gage.  The name of the dataset is usually the same
as the filename of the shapefile (minus the .shp).  If you are unsure,
you can use the command line tool
[ogrinfo](http://www.gdal.org/ogrinfo.html), which ships with GDAL.

#### Importing data into GRASS for use with RHESSys

The following workflow steps are identical whether using standard
spatial data or custom local data and will not be covered here:

- Create a new GRASS location
- Import RHESSys source code into your project
- Import RHESSys climate data
- Delineate watershed and generate derived data products
- Generate landcover maps in GRASS

See the above standard spatial data tutorial for detailed information
on these steps.


#### Importing other raster layers

For a list of all of the current raster map types supported by
EcohydroLib, run the RegisterRaster script as follows:

    RegisterRaster.py -h

This will also show all of the resampling and other import options
available.

What follows is a series of examples showing how to input some of
these raster types.  All rasters must be stored in a file format
readable by GDAL (see above).

##### Landcover data

    RegisterRaster.py -p PROJECT_DIR -t landcover -r /path/to/my/landcover_map.tif --noresample -b "Baltimore Ecosystem Study LTER" --force

Here we are importing a landcover raster map obtained from the
Baltimore Ecosystem Study LTER where we've asked RegisterRaster not to
resample the raster (unless its spatial reference system differs from
the DEM; i.e. the resolution of the raster cells won't be changed).
We're also telling RegisterRaster to ignore the fact that the extent
of the landcover raster does not exactly match the extent of the
DEM/study area.  After import, you are strongly encouraged to
visualize the landcover map overlaid on the DEM using QGIS to ensure
that the landcover will cover an adequate portion of your study area.

> For landcover maps, we recommend that you do not resample when
> registering the raster using RegisterRaster, but instead let GRASS
> handle the resampling.

To make the landcover map in the project directory available to
RHESSys, it must be imported into GRASS as follows:

    ImportRasterMapIntoGRASS.py -p PROJECT_DIR -t landcover -m nearest

This will import the landcover raster into GRASS, and then resample
the raster using the nearest neighbor method.  For a list of valid
resampling methods, run ImportRasterMapIntoGRASS with the *-h* option;
you may also specify *none* as the resampling method and the raster
will not be resampled.

##### Rooftop connectivity

Starting with RHESSys 5.16, the createflowpaths (CF) utility is able
to create surface flow tables that can incorporate non-topographic
routing of flow from rooftops to nearby impervious and pervious areas.
RHESSys 5.16 can use separate surface and subsurface flow tables to
simulate the effect of such non-topographic routing on the landscape.
You can find more information on using surface flowtable routing in RHESSys
[here](https://github.com/RHESSys/RHESSys/wiki/Surface-Flowtable-Routing).

To import a rooftop connectivity raster, use RegisterRaster as follows:

    RegisterRaster.py -p PROJECT_DIR -t roof_connectivity -r /path/to/my/roof_map.tif --noresample --force

> As with landcover maps, we recommend do not let RegisterRaster
> resample roof connectivity rasters, instead letting GRASS handle the
> resampling.  RegisterRaster uses GDAL to resample rasters.  GDAL
> ignore null/nodata pixels when resampling, whereas GRASS's
> r.resamp.interp does not.  Thus, when a landcover and a roof top
> connectivity raster, which contains nodata values for all non-roof
> pixels, are resampled in RegisterRaster, they can become
> mis-registered, which will result in an invalid surface routing
> table.

Then make your rooftop connectivity raster available for RHESSys by
importing it into GRASS:

    ImportRasterMapIntoGRASS.py -p PROJECT_DIR -t roof_connectivity -m nearest

##### Vegetation LAI

As described in the standard spatial data tutorial above,
EcohydroLib/RHESSysWorkflows requires that the user provide their own
LAI data, which can be imported into a project using RegisterRaster:

     RegisterRaster.py -p PROJECT_DIR -t lai -r /path/to/my/lai_map.tif --force

Now make your LAI raster available for RHESSys by importing it into
GRASS:

    ImportRasterMapIntoGRASS.py -p PROJECT_DIR -t lai -m none

##### Custom patch map

A custom patch map can be imported into a project as follows:

    RegisterRaster.py -p PROJECT_DIR -t patch -r /path/to/my/patch_map.tif --noresample

Then make your patch raster available for RHESSys by importing it into
GRASS:

    ImportRasterMapIntoGRASS.py -p PROJECT_DIR -t patch -m none

##### Custom soils data

A custom soils map can be imported into a project as follows:

    RegisterRaster.py -p PROJECT_DIR -t soil -r /path/to/my/soils_map.tif -b "Brian Miles <brian_miles@unc.edu>, based on field observations"

Then make your soil raster available for RHESSys by importing it into
GRASS:

    ImportRasterMapIntoGRASS.py -p PROJECT_DIR -t soils -m none

##### Climate station zone map

The DelineateWatershed script will use the hillslope map as the zone
map.  If you wish to use another map for the zone map, do the
following after running DelineateWatershed:

    RegisterRaster.py -p PROJECT_DIR -t zone -r /path/to/my/zone_map.tif -b "Brian Miles <brian_miles@unc.edu>, climate station zones based on isohyet"

Then make your zone raster available for RHESSys by importing it into
GRASS:

    ImportRasterMapIntoGRASS.py -p PROJECT_DIR -t zone -m none

#### Generating RHESSys definitions for custom soil data

When using custom soil data with RHESSysWorkflows you need to create
soil definition files before you can create a worldfile.  To create
soil definitions, you must first create raster reclass rules that map
between your soil type and a soil type known to RHESSys ParamDB.  At
present, ParamDB contains definitions drawn from the literature for
USDA soil textures.  However you may load custom soil parameters into
your own local copy of ParamDB.  For more information, see the ParamDB
[README](https://github.com/RHESSys/ParamDB).

To create prototype soil reclass rules for a project, do the following:

    RegisterCustomSoilReclassRules.py -p PROJECT_DIR -b

Here we're using the *-b* (a.k.a. *--buildPrototypeRules*) command
line option.  This will result in the creation of a file called
*soils.rule* in the *rules* directory of your project directory. You
will need to edit this file as necessary to map your custom soil types
to ParamDB soil types.  

> Make sure that the soil class names on the righthand side of each
> reclass rule correspond to soil class names in ParamDB

You can also import existing soil reclass rules as follows:

    RegisterCustomSoilReclassRules.py -p PROJECT_DIR -r /path/to/my/existing/reclass_rules/

The *-r* (a.k.a. *--ruleDir*) parameter must point to a directory that
contains a file named soils.rule.  This will will be copied into the
*rules* directory of your project directory.

Once you have valid soil reclass rules in place, you can generate
RHESSys soil parameter definition files for your custom soils using
the following command:

    GenerateCustomSoilDefinitions.py -p PROJECT_DIR 

This script will print information to the screen about each soil type
encountered and the RHESSys ParamDB soil parameter classes they map
to.  If you see no such print out, check your soil reclass rule file
to make sure it is correct.  The resulting soil definition files will
be written to the *defs* directory in the *rhessys* directory of your
project directory.

> Remember most RHESSysWorkflows commands support the *--overwrite*
> command line option for overwriting existing data stored in the
> project directory or in GRASS.


#### Creating a surface flow table using a roof connectivity map

If you are using a roof connectivity map in your workflow, you need to
explicitly tell CreateFlowtable to use the roof connectivity map to
generate a surface flow table.  Do so as follows:

    CreateFlowtable.py -p PROJECT_DIR --routeRoofs --routeRoads

Here we're using both the *--routeRoofs* and *--routeRoads* options.
You are not required to use both together, but usually when modeling
rooftop connectivity you will be working in a watershed that also has
roads whose effects on routing you will also want to consider.

#### Creating the worldfile and initializing vegetation carbon stores

The following workflow steps are identical whether using standard
spatial data or custom local data and will not be covered here:

- Creating the worldfile for a watershed
- Initializing vegetation carbon stores

See the above standard spatial data tutorial for detailed information
on these steps.

