StochPy Stochastic modeling in Python
=====================================

Copyright (c) 2010-2013, Timo R. Maarleveld, Brett G. Olivier, and Frank J. Bruggeman
All rights reserved.

StochPy is distributed under a BSD style licence.

Author information
------------------

Timo R. Maarleveld, Brett G. Olivier, and Frank J. Bruggeman
Centrum Wiskunde en Informatica, Amsterdam, Netherlands
VU University, Amsterdam, Netherlands

e-mail: tmd200@users.sourceforge.net
web: http://sourceforge.net/projects/stochpy/

Documentation can be found in the user guide (see Documentation directory or http://stochpy.sourceforge.net/html/userguide.html) 

Installation
------------
The following software is required before installling StochPy:

- Python 2.x+
- NumPy 1.x+
- Matplotlib (optional)
- libsbml (optional)
- libxml2 (optional)
- mpmath (optional)

Linux/MAC OS/Cygwin
~~~~~~~~~~~~~~~~~~~

1) cd to directory StochPy-1.1.0
2) sudo python setup install

Windows
~~~~~~~
Use the available windows installer or the setup file

Usage
-----
>>> import stochpy
>>> help(stochpy)
>>> smod = stochpy.SSA()
>>> help(smod)
>>> smod.DoStochSim(IsTrackPropensities=1) # Do a stochastic time simulation
>>> smod.PlotSpeciesTimeCourses()  
>>> smod.PlotSpeciesDistributions()
>>> smod.PlotPropensityTimeCourses()
>>> smod.GetEventWaitingtimes()
>>> smod.PlotEventWaitingtimes()
>>> smod.DoStochSim(trajectories = 10,method = 'Direct',end = 1000, mode = 'steps')
>>> smod.data_stochsim              # data object that stores the data of a simulation trajectory (See user guide)
>>> smod.data_stochsim.trajectory   # trajectory
>>> smod.GetTrajectoryData(3)       # Get data from the third trajectory
>>> smod.PrintSpeciesMeans()        # shows the means of every species in the model for the selected trajectory (3)
>>> smod.PrintSpeciesDeviations()
>>> smod.GetRegularGrid(npoints)
>>> smod.data_stochsim_grid # data object that stores the interpolated data
>>> smod.data_stochsim_grid.species_means # species means for every time point
