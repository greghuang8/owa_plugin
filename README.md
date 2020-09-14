# owa_plugin

OWA/WLC Plugin on QGIS. 

This plugin calculates the Weighted Linear Combination (WLC) or Ordered Weighted Average (OWA) scores for Multi-Criteria Decision Analysis (MCDA). 
Note that the procedure for OWA calculation is as follows:

1. Specified criterion weights are applied to values in their respective fields
2. At each location, the different weighted criteria values are sorted from max to min
3. Specified order weights are applied to the sorted list in that order, i.e. what you enter at row 1 of the order weights column will be applied to the max value of the sorted list of max to min weighted criteria values at each location
4. At each location, each ordered weighted criteria value for each criterion selected is summed, and the OWA score is calculated. 

In some other use cases, order weights were applied before criterion weights are applied. Do note that this plugin does _**not**_ calculate OWA scores this way. 

To use this plugin by downloading from GitHub, zip the wlc_owa_tool directory in this repo containing the code and install it via the QGIS plugins interface.

The criteria used can be standardized using the "Field Standardizer" plugin also found on this Github page. 

&copy; Gregory Huang 2020
