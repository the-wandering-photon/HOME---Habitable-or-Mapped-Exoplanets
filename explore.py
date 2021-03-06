import numpy as np
import pandas as pd
import sys
import matplotlib.pyplot as plt
from pathlib import Path

# below 4 scripts written by me which are used by the main function below 
# and can be found in the /deps/ folder
from deps import data_cleansing as dc
from deps import plot_logic as pl
from deps import phys_and_math as pam
from deps import consts as consts


def main():

	# This dataset has a gaps of imbalanced missing data and duplicates. ~ 32 000 rows of data in the imbalanced dataset.
	# This script is designed to work with the dataset from: 
	# https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=PS, I have included a copy of the csv.

	'''
	A few fun things to consider in the future below! My project is now complete, in that i have taken 32 000 rows of data and 
	selected planets for scientific focus which would / could support life.

	A nice to do list that is not 'mission critical' to the purposes of my project:

		* Graph out the black body spectrum of a system's star - from the black body work out its temperature
		# Histograms:
			* Histogram distance to exo from earth vs number of exo
			* Histogram radius of planet against earth, and jupiter
			* Histogram temperature of planet (if observed)
			* Histogram eccentricity
		# Scatter for mass vs luminosity vs distance of orbit
		# Balance gaps - is there data missing which is in another row that has been discounted?
		# Can i look at any spectra re the planets?
		# Look at solar data
		# Scrape web / other resources to find additional data such as mass, radius for a more complete dataset.
		# It would be interesting to see if planets are iron / rocky close to the star, and the further out do they go to gas giants?

	'''

	LENGTH_OF_LIST = consts.get_len_list() # raw data
	CLEAN_DATA_FILE_PATH = consts.get_clean_data_file_path()
	INPUT_DATA_PATH = consts.get_input_data_path()

	# set some rules for debug output - I dont want rows, but columns in full:
	pd.set_option('display.max_columns', None)
	pd.options.mode.chained_assignment = None  # turn off warnings as they are used in a safe way

	# Check if there is the santisised xl, if not it is first run (or changes to code) so import large dataset, otherwise import sanitised 
	# dataset to save load times..
	# Just remember to delete this file if you make changes to clean_data_exoplanets or similar.
	if Path(CLEAN_DATA_FILE_PATH).is_file():
		print("Importing sanitised data..")
		exoplanets = pd.read_excel(CLEAN_DATA_FILE_PATH)
	
	else:
		print("Importing un-sanitised data.. This could take a while depending on the size of the input data.")

		# create sqlite database for the master data
		dc.convert_xl_to_sql()

		# first create data frame with CSV in, ~ 30 000 rows.
		master_data = pd.read_excel(INPUT_DATA_PATH)

		# Examine the shape
		print("Shape of the import: {}".format(master_data.shape))

		# Clean & format the data
		exoplanets = dc.data_cleansing_methods(master_data, LENGTH_OF_LIST, CLEAN_DATA_FILE_PATH)


	# produce a scatter plot for planet mass against the temperature (K) of its host star, is there a correlation? 
	# TODO - this should also take into account the distance from the host star - probably use 'orbital_period_widest_radius_in_AU' for this.
	pl.scatter_plot_for_planet_mass_vs_solar_temp(exoplanets, 
		'./output/scatter_plot_mass_vs_temp.png', 
		'A graph to show the mass (1e29) (kg) of known exoplanets orbiting stars of a \ncertain temperature (K), with earth denoted as an orange dot.')

	# A histogram to show the frequency of host stars with different numbers of exoplanets.
	# TODO - it would be interesting to add additional data to this histogram, size of star, temperature, habitability etc.
	# Could I analyse the data to show those in habitabiltiy zone AND multiple planets? Would they look similar to our solar system in terms
	# of their composition?
	pl.histogram_exoplanets_per_star(exoplanets, './output/histogram_exoplanets_per_star.png', 
		'A histogram to show the frequency of exoplanets orbiting a host star.')

	# plot habitable exos
	habitable = pl.graph_habitable_exoplanets(exoplanets)

	# graph the gravitational forces for both habitable planets and non-habitable.
	pl.graph_gravity(exoplanets, habitable, './output/g_force_all_exoplanets.png', './output/g_force_habitable_exoplanets.png')

	pam.compute_planet_state_from_temperature(exoplanets)

	# graph the density's and thus planet state of each planet
	# 0 flag just for formatting logic
	pl.graph_density(exoplanets, './output/density_all_planets.png', './output/density_all_planets-histogram.png', 0)
	pl.graph_density(habitable, './output/density_hab_planets.png', './output/density_hab_planets-histogram.png')

	pl.print_optimal_planets_for_life(exoplanets)



if __name__ == '__main__':
	main()