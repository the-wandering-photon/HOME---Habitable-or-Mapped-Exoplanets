import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from math import log10 , floor

from . import phys_and_math as pam

def print_optimal_planets_for_life(exoplanets):
	'''
	A function to print the optimal planets for supprting life, based on: 
		* Being in the habitable zone
		* Having life supporting gravity

	Also compile interesting information about those planets, that is the result of all the analysis done in my code.
	'''
	combined = {'name_of_planet': np.array(exoplanets['name_of_planet']), 
		'orbital_period' : np.array(exoplanets['orbital_period']), 
		'equilibrium_temperature_K' : np.array(exoplanets['equilibrium_temperature_K']), 
		'stellar_effective_temperature_black_body_radiation' : np.array(exoplanets['stellar_effective_temperature_black_body_radiation']), 
		'stellar_radius' : np.array(exoplanets['stellar_radius']), 
		'distance_to_system_in_light_years' : np.array(exoplanets['distance_to_system_in_light_years']), 
		'planet_actual_radius' : np.array(exoplanets['planet_actual_radius']), 
		'planet_density' : np.array(exoplanets['planet_density']), 
		'is_planet_gas_giant' : np.array(exoplanets['is_planet_gas_giant']), 
		'is_planet_habitable' : np.array(exoplanets['is_planet_habitable']), 
		'accelaration_to_gravity' : np.array(exoplanets['accelaration_to_gravity']), 
		'gravity_compared_to_earth' : np.array(exoplanets['gravity_compared_to_earth'])}

	# Now we have to pass some tests for selection..

	# temp dataframe to remove nans - if there are nan values in the dataframe, remove the row as we need both x and y values to plot.
	t_df = pd.DataFrame(combined)
	#t_df.dropna(inplace = True) # 705 rows

	t_df = t_df.loc[(t_df['is_planet_habitable'] == 1) & ((t_df['is_planet_gas_giant'] == 0)) & ((t_df['gravity_compared_to_earth'] <= 4))]

	for index, row in t_df.iterrows():
		# Manual data fix:
		if t_df.loc[index,'name_of_planet'] == "TRAPPIST-1 e":
			t_df.loc[index,'distance_to_system_in_light_years'] = 39 # Source: https://www.space.com/35796-trappist-1-alien-planets-travel-time.html

		print(f"""Potentially habitable planet found! Planet name: {t_df.loc[index,'name_of_planet']}, it has an orbital period of:
			{round_it(t_df.loc[index,'orbital_period'], 2)} days (2.s.f) (meaning it takes {round_it(t_df.loc[index,'orbital_period'], 2)} (2.s.f) days to orbit its star), 
			it has a possible temperature of: {round_it(t_df.loc[index,'equilibrium_temperature_K'] - 273.15, 3)} degrees celsius (3.s.f), 
			the temperature of its star is {t_df.loc[index,'stellar_effective_temperature_black_body_radiation']} Kelvin, 
			the radius of the star is: {t_df.loc[index,'stellar_radius']} km, 
			the distance to the planet is {t_df.loc[index,'distance_to_system_in_light_years']} light years, 
			the radius of the planet is {t_df.loc[index,'planet_actual_radius']} km,
			the planet lives in the habitable zone of the star and is not a gas planet or an iron planet. Gravity has an acceleration of 
			 {round_it(t_df.loc[index,'accelaration_to_gravity'], 3)} meters per second per second (3.s.f), which is {round_it(t_df.loc[index,'gravity_compared_to_earth'], 3)} (3.s.f) times that of Earth.""")
			


def scatter_plot_for_planet_mass_vs_solar_temp(df, savepath, graph_title):
	'''
	A function to plot planet mass vs the solar temperature, is there any correlation?

	Takes in a dataframe, for example:

	combined = {'stellar_effective_temperature_black_body_radiation': np.array(df['stellar_effective_temperature_black_body_radiation']), 
		'planet_mass_in_kg' : np.array(df['planet_mass_in_kg'])}

	t_df = pd.DataFrame(combined) <------ create a df from combined data before calling function
	new_df = remove_nans_from_df(t_df)

	'''

	# combine two arrays from the dataframe into a dictionary
	combined = {'stellar_effective_temperature_black_body_radiation': np.array(df['stellar_effective_temperature_black_body_radiation']), 
		'planet_mass_in_kg' : np.array(df['planet_mass_in_kg'])}

	# temp dataframe to remove nans - if there are nan values in the dataframe, remove the row as we need both x and y values to plot.
	t_df = pd.DataFrame(combined)
	t_df.dropna(inplace = True)

	# Create our final dataset
	x_solar_temp_array = np.array(t_df['stellar_effective_temperature_black_body_radiation'])
	y_planet_mass_array = np.array(t_df['planet_mass_in_kg'])

	# add some data for earth (orange dot on plot)
	earth_mass = 5.972e24
	sol_temp = 5778

	# plot
	plt.clf()

	plt.suptitle(graph_title, fontsize=10)
	plt.xlabel("Temperature of the host star / K")
	plt.ylabel("Mass of the exo-planet / kg")

	plt.scatter(x_solar_temp_array, y_planet_mass_array, s=5)
	plt.scatter(sol_temp, earth_mass, s=15)

	plt.savefig(savepath)


def graph_habitable_exoplanets(df):
	'''
	A function to graph the habitable planets
	'''
	# create a dataframe for habitable planets
	habitable = df.loc[df['is_planet_habitable'] == 1]

	scatter_plot_for_planet_mass_vs_solar_temp(habitable, 
		'./output/habitable_scatter_plot_mass_vs_temp.png', 
		'A graph to show the mass (1e28) (kg) of known exoplanets in the habitable zone orbiting \nstars of a certain temperature (K), ' + 
		'with earth \ndenoted as an orange dot.')

	# A histogram to show the frequency of host stars with different numbers of exoplanets.
	# TODO - it would be interesting to add additional data to this histogram, size of star, temperature, habitability etc.
	# Could I analyse the data to show those in habitabiltiy zone AND multiple planets? Would they look similar to our solar system in terms
	# of their composition?
	histogram_exoplanets_per_star(habitable, './output/habitable_histogram_exoplanets_per_star.png', 
		'A histogram to show the frequency of exoplanets with at least one \nin the habitable range orbiting a host star.')

	return habitable # return the habitable df


def histogram_exoplanets_per_star(df, savepath, graph_title):

	# provide a dataframe to count the planets around host stars
	solar_system_data = df.groupby(['name_of_host_star']).size().reset_index(name='count')

	# clear previous plot and make new plot
	plt.clf()
	plt.suptitle(graph_title,fontsize=10)
	plt.ylabel("Frequency")
	plt.xlabel("Number of detected exoplanets around star")
	
	num_bins, edges, bars = plt.hist(solar_system_data['count'], bins=range(1,10), rwidth=0.7)

	# add numbers onto plot as low values are unreadable
	plt.bar_label(bars)

	# export
	plt.savefig(savepath)


def graph_density(exo, savepath, savepath_histogram, hab=1):

	'''
	A function to plot the density against mass
	'''

	# clear previous plot and make new plot
	plt.clf()
	combined = {'planet_density': np.array(exo['planet_density']), 
	'planet_mass_in_kg' : np.array(exo['planet_mass_in_kg']),
	'is_planet_gas_giant' : np.array(exo['is_planet_gas_giant'])}

	# temp dataframe to remove nans - if there are nan values in the dataframe, remove the row as we need both x and y values to plot.
	t_df = pd.DataFrame(combined)
	t_df.dropna(inplace = True)

	# Create our final dataset, independant variable on the x
	x_planet_mass = np.array(t_df['planet_mass_in_kg']) 
	y_dens = np.array(t_df['planet_density'])

	# add some data for earth (orange dot on plot)
	earth_mass = 5.972e24
	earth_dens = 5520 # source http://astronomy.nmsu.edu/mchizek/105/LABS/EarthDensity.pdf

	if hab == 1:
		title = "A graph to show the density vs its mass of habitable-zone exoplanets, \nwith Earth plotted as an organge point."
		plt.figure(figsize=(8,8)).suptitle(title,fontsize=10)
	else: 
		plt.suptitle("A graph to show the density vs its mass of all detected exoplanets, \nwith Earth plotted as an organge point.", fontsize=10)

	plt.xlabel("Planet's mass / kg")
	plt.ylabel("Planet's density / kg m^-3")

	plt.scatter(x_planet_mass, y_dens, s=10)
	plt.scatter(earth_mass, earth_dens, s=10)

	plt.savefig(savepath)

	# scatter graph is too busy to provide any decent interpretations, so I'll use a histogram instead:

	plt.clf()

	if hab == 1:
		plt.suptitle("A histogram to show the frequency of different planet types of \nhabitable-zone planets.",fontsize=10)
	else: 
		plt.suptitle("A histogram to show the frequency of different planet types.",fontsize=10)

	plt.ylabel("Frequency")
	plt.xlabel("Planet type")
	plt.xticks([]) # remove numbers off of x axis
	
	num_bins, edges, bars = plt.hist(t_df['is_planet_gas_giant'], bins=range(0,4), rwidth=0.7)

	# some logic for text placement
	if hab == 1:
		plt.text(0.25, 0.1, 'Rocky planet')
		plt.text(1.25, 0.1, 'Gas planet')
		plt.text(2.25, 0.1, 'Iron planet')
	else:
		plt.text(0.25, 7, 'Rocky planet')
		plt.text(1.25, 7, 'Gas planet')
		plt.text(2.25, 7, 'Iron planet')


	# add numbers onto plot as low values are unreadable
	plt.bar_label(bars)

	plt.savefig(savepath_histogram)




def graph_gravity(exo, hab, savepathall, savepathhab):
	''' 

	A function to graph the gravity of exoplanets.

	Produce as a scatter against their mass, it should be a straight line graph.. will be interesting to see
	if the results are different. Doen as g force (compared to earths g-force of 1 g) as apposed to m s^-2

	'''

	# clear previous plot and make new plot
	plt.clf()
	combined = {'gravity_compared_to_earth': np.array(exo['gravity_compared_to_earth']), 
	'planet_mass_in_kg' : np.array(exo['planet_mass_in_kg'])}

	# temp dataframe to remove nans - if there are nan values in the dataframe, remove the row as we need both x and y values to plot.
	t_df = pd.DataFrame(combined)
	t_df.dropna(inplace = True)

	# Create our final dataset, independant variable on the x
	x_planet_mass = np.array(t_df['planet_mass_in_kg']) 
	y_g_force = np.array(t_df['gravity_compared_to_earth'])

	# add some data for earth (orange dot on plot)
	earth_mass = 5.972e24
	earth_g = 1

	# plot
	plt.clf()

	plt.suptitle("A graph to show the G-force as a measure compared to earth (1 G) (vs. its mass) \n of all detected exoplanets with Earth plotted as an organge point.", fontsize=10)
	plt.xlabel("Planet's mass / kg")
	plt.ylabel("G-Force compared to Earth / G's")

	plt.scatter(x_planet_mass, y_g_force, s=5)
	plt.scatter(earth_mass, earth_g, s=15)

	# Humans could build the strength to survive up to 4 G's potentially (though i have seen studies suggeting we can only survive
	# 3 G's for up to 2 minuets, so not sure on the reliability of this.) Add a line to indicate this cut off point. 
	# Source: https://www.discovermagazine.com/the-sciences/whats-the-maximum-gravity-we-could-survive
	plt.axhline(y=4, color='r', linestyle='-') # plot line

	plt.savefig(savepathall)


	# plot habitable planets

	# clear previous plot and make new plot
	plt.clf()
	combined = {'gravity_compared_to_earth': np.array(hab['gravity_compared_to_earth']), 
	'planet_mass_in_kg' : np.array(hab['planet_mass_in_kg'])}

	# temp dataframe to remove nans - if there are nan values in the dataframe, remove the row as we need both x and y values to plot.
	t_df = pd.DataFrame(combined)
	t_df.dropna(inplace = True)

	# Create our final dataset, independant variable on the x
	x_planet_mass = np.array(t_df['planet_mass_in_kg']) 
	y_g_force = np.array(t_df['gravity_compared_to_earth'])

	# clear last plot
	plt.clf()

	plt.suptitle("A graph to show the G-force as a measure compared to earth (1 G) (vs. its mass) of all \ndetected habitable exoplanets with Earth plotted as an organge point.", fontsize=10)
	plt.xlabel("Planet's mass / kg")
	plt.ylabel("G-Force compared to Earth / G's")

	plt.scatter(x_planet_mass, y_g_force, s=5)
	plt.scatter(earth_mass, earth_g, s=15)

	# Humans could build the strength to survive up to 4 G's potentially (though i have seen studies suggeting we can only survive
	# 3 G's for up to 2 minuets, so not sure on the reliability of this.) Add a line to indicate this cut off point. 
	# Source: https://www.discovermagazine.com/the-sciences/whats-the-maximum-gravity-we-could-survive
	plt.axhline(y=4, color='r', linestyle='-') # plot line

	plt.savefig(savepathhab)


	### plot g's vs radius ###

	# clear previous plot and make new plot
	plt.clf()
	combined = {'gravity_compared_to_earth': np.array(exo['gravity_compared_to_earth']), 
	'planet_actual_radius' : np.array(exo['planet_actual_radius'])}

	# temp dataframe to remove nans - if there are nan values in the dataframe, remove the row as we need both x and y values to plot.
	t_df = pd.DataFrame(combined)
	t_df.dropna(inplace = True)

	# Create our final dataset, independant variable on the x
	x_planet_radius = np.array(t_df['planet_actual_radius']) 
	y_g_force = np.array(t_df['gravity_compared_to_earth'])

	# add some data for earth (orange dot on plot)
	earth_mass = 5.972e24
	earth_g = 1

	# plot
	plt.clf()

	plt.suptitle("A graph to show the G-force as a measure compared to earth (1 G) (vs. its radius) \n of all detected exoplanets with Earth plotted as an organge point.", fontsize=10)
	plt.xlabel("Planet's radius / km")
	plt.ylabel("G-Force compared to Earth / G's")

	plt.scatter(x_planet_radius, y_g_force, s=5)
	plt.scatter(6371, earth_g, s=15)

	# Humans could build the strength to survive up to 4 G's potentially (though i have seen studies suggeting we can only survive
	# 3 G's for up to 2 minuets, so not sure on the reliability of this.) Add a line to indicate this cut off point. 
	# Source: https://www.discovermagazine.com/the-sciences/whats-the-maximum-gravity-we-could-survive
	plt.axhline(y=4, color='r', linestyle='-') # plot line

	plt.savefig("./output/g_force_all_exoplanets_radius.png")


	### plot g's vs radius ###

	# clear previous plot and make new plot
	plt.clf()
	combined = {'gravity_compared_to_earth': np.array(hab['gravity_compared_to_earth']), 
	'planet_actual_radius' : np.array(hab['planet_actual_radius'])}

	# temp dataframe to remove nans - if there are nan values in the dataframe, remove the row as we need both x and y values to plot.
	t_df = pd.DataFrame(combined)
	t_df.dropna(inplace = True)

	# Create our final dataset, independant variable on the x
	x_planet_radius = np.array(t_df['planet_actual_radius']) 
	y_g_force = np.array(t_df['gravity_compared_to_earth'])

	# add some data for earth (orange dot on plot)
	earth_mass = 5.972e24
	earth_g = 1

	# plot
	plt.clf()

	plt.suptitle("A graph to show the G-force as a measure compared to earth (1 G) (vs. its radius) \n of all detected habitable exoplanets with Earth plotted as an organge point.", fontsize=10)
	plt.xlabel("Planet's radius / km")
	plt.ylabel("G-Force compared to Earth / G's")

	plt.scatter(x_planet_radius, y_g_force, s=5)
	plt.scatter(6371, earth_g, s=15)

	# Humans could build the strength to survive up to 4 G's potentially (though i have seen studies suggeting we can only survive
	# 3 G's for up to 2 minuets, so not sure on the reliability of this.) Add a line to indicate this cut off point. 
	# Source: https://www.discovermagazine.com/the-sciences/whats-the-maximum-gravity-we-could-survive
	plt.axhline(y=4, color='r', linestyle='-') # plot line

	plt.savefig("./output/g_force_all_exoplanets_habitable_radius.png")

	# plot
	plt.clf()

	g_f = t_df['gravity_compared_to_earth'].to_dict()

	# Create a pie chart of planets greater than, and less than, 4 G's of habitable exos
	#less_than = len(combined[combined.iloc[:,0] <= 4])
	less_than = len([g for g in g_f.values() if int(g) <= 4])
	more_than = len([g for g in g_f.values() if int(g) >= 4.01])
	#more_than = len(combined[combined.iloc[:,0] >= 4.01])

	arr = np.array([less_than, more_than])

	key = [f"Planets under 4G's: {less_than}", f"Planets greater than 4 G's: {more_than}"]
	
	plt.suptitle("A pie chart to show the number of habitable exoplanets that are over and under 4 G's.", fontsize=10)


	plt.pie(arr, labels = key)

	plt.savefig("./output/g_force_all_exoplanets_habitable_pie_chart.png")


def round_it(x, sig):
	'''
	I have taken this code from https://www.delftstack.com/howto/python/round-to-significant-digits-python/
	thank you for providing this function!
	'''
	return round(x, sig-int(floor(log10(abs(x))))-1)

