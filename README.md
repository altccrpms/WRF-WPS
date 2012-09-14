Overview
========

This package currently compiles WRF and WPS in DM parallel mode with simple
nesting with openmpi.

Running
=======

To run WRF you generally create a run directory to hold the input in and
output data.  After creating this directory and putting in the necessary
input data and namelist.input file, run:

> module load wrf/openmpi-%compiler%
> setupwrf
> mpirun -np %processes% wrf.exe

The setupwrf command will link in the standard input files into the current
directory.  This only needs to be done one per run directory.

The module load command will load the needed environment modules to run WRF.
Change %compiler% to the name of the compiler you want to use (e.g. intel).
This need to be run once per login session.
