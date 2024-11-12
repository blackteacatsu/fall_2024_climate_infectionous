

## Import required libraries
########################################################################################
import xarray as xr              # for working with netcdf files
import pandas as pd              # we'll use dataframe objects from this library to do most data manipulation
import matplotlib.pyplot as plt  # for plotting
import os                        # for checking whether we need to create a new directory when saving plots



## Define file directories and paths
########################################################################################
fDir_thisFile = '/home/local/WIN/cyasana1/Code/course_climInfDis/projectExample/' # directory in which this file lives
fDir_rawData = fDir_thisFile + 'rawData/'
filepath_T2M_dly     = fDir_rawData + 'MERRA2_tavg1_2d_slv_Nx.19800101_20211231.SUB.T2M.dly.nc'
filepath_prcp_dly    = fDir_rawData + 'mergedDly_2001_2020.nc'



## Process data and store in dataframes
########################################################################################

# Subset data to locations of interest
Negombo_lat = 7.2008  # deg N
Negombo_lon = 79.8737 # deg E
Jaffna_lat  = 9.6615  # deg N
Jaffna_lon  = 80.0255 # deg E

ds_T2M_dly = xr.open_dataset(filepath_T2M_dly)
T2M_dly_Negombo = ds_T2M_dly['T2M'].sel(lat=Negombo_lat, lon=Negombo_lon, method="nearest")
T2M_dly_Negombo = T2M_dly_Negombo.drop_vars(['lat', 'lon'])
T2M_dly_Jaffna = ds_T2M_dly['T2M'].sel(lat=Jaffna_lat, lon=Jaffna_lon, method="nearest")
T2M_dly_Jaffna = T2M_dly_Jaffna.drop_vars(['lat', 'lon'])

ds_prcp_dly = xr.open_dataset(filepath_prcp_dly)
prcp_dly_Negombo = ds_prcp_dly['precipitationCal'].sel(lat=Negombo_lat, lon=Negombo_lon, method="nearest")
prcp_dly_Negombo = prcp_dly_Negombo.drop_vars(['lat', 'lon'])
prcp_dly_Jaffna = ds_prcp_dly['precipitationCal'].sel(lat=Jaffna_lat, lon=Jaffna_lon, method="nearest")
prcp_dly_Jaffna = prcp_dly_Jaffna.drop_vars(['lat', 'lon'])

# Subest data to a common time range
start_date = '2007-01-01' # earliest time across datasets (denInc)
end_date   = '2020-12-31' # latest time across datasets (IMERG prcp)

T2M_dly_Negombo = T2M_dly_Negombo.sel(time=slice(start_date, end_date))
T2M_dly_Jaffna = T2M_dly_Jaffna.sel(time=slice(start_date, end_date))
prcp_dly_Negombo = prcp_dly_Negombo.sel(time=slice(start_date, end_date))
prcp_dly_Jaffna = prcp_dly_Jaffna.sel(time=slice(start_date, end_date))

# Convert data from DataArrays to Pandas DataFrames
T2M_dly_Negombo = T2M_dly_Negombo.to_dataframe()
T2M_dly_Jaffna = T2M_dly_Jaffna.to_dataframe()
prcp_dly_Negombo = prcp_dly_Negombo.to_dataframe()
prcp_dly_Jaffna = prcp_dly_Jaffna.to_dataframe()

# Combine data into one dataframe per variable, where each column is a different location
T2M_dly = pd.concat([T2M_dly_Negombo, T2M_dly_Jaffna], axis=1)
T2M_dly.columns = ['Negombo', 'Jaffna']
prcp_dly = pd.concat([prcp_dly_Negombo, prcp_dly_Jaffna], axis=1)
prcp_dly.columns = ['Negombo', 'Jaffna']

# Convert units: the T2M data is in K but we want degrees C.
T2M_dly = T2M_dly - 273.15

print(T2M_dly)



## Plot full daily timeseries for each location
########################################################################################

# Set colors for plotting
# Colors are from colorbrewer2.org (qualitative data; colorblind safe)
color_Negombo = '#7570b3'
color_Jaffna = '#d95f02'

# First, the temperature plot
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(T2M_dly.index, T2M_dly['Negombo'], label='Negombo', color=color_Negombo, linestyle='-', linewidth=2)
ax.plot(T2M_dly.index, T2M_dly['Jaffna'], label='Jaffna', color=color_Jaffna, linestyle='-', linewidth=2)

# Add title and labels
ax.set_xlabel('Date')
ax.set_ylabel('Temperature (°C)')

# Show legend
ax.legend()

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Adjust layout to avoid label cutoff
plt.tight_layout()

# Save the figure
dir_out = '/home/local/WIN/cyasana1/Code/course_climInfDis/projectExample/outputPlots/'
fileName = 'tseries_temp_dly_allTime'
if not os.path.isdir(dir_out):
    os.makedirs(dir_out)
plt.savefig(dir_out + fileName + ".png", dpi=300, bbox_inches="tight")
plt.close(fig)


# Next, the precipitation plot
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(prcp_dly.index, prcp_dly['Negombo'], label='Negombo', color=color_Negombo, linestyle='-', linewidth=2)
ax.plot(prcp_dly.index, prcp_dly['Jaffna'], label='Jaffna', color=color_Jaffna, linestyle='-', linewidth=2)

# Add title and labels
ax.set_xlabel('Date')
ax.set_ylabel('Precipitation (mm/day)')

# Show legend
ax.legend()

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Adjust layout to avoid label cutoff
plt.tight_layout()

# Save the figure
dir_out = '/home/local/WIN/cyasana1/Code/course_climInfDis/projectExample/outputPlots/'
fileName = 'tseries_prcp_dly_allTime'
if not os.path.isdir(dir_out):
    os.makedirs(dir_out)
plt.savefig(dir_out + fileName + ".png", dpi=300, bbox_inches="tight")
plt.close(fig)



## Calculate daily climatologies
########################################################################################

# The full data record doesn't clearly show the seasonality of the two locations as well as we'd like
# (while it's decently obvious in temp, it's not obvious in prcp).
# So, let's calculate the climatologies for the two locations and plot those.

# Calculate climatologies
T2M_dly['DOY']  = T2M_dly.index.day_of_year # create day of year column
T2M_dlyClim_Negombo = T2M_dly.groupby('DOY')['Negombo'].mean() # calculate climatology
T2M_dlyClim_Jaffna  = T2M_dly.groupby('DOY')['Jaffna'].mean()   # calculate climatology
T2M_dlyClim = pd.DataFrame({'Negombo': T2M_dlyClim_Negombo, 'Jaffna': T2M_dlyClim_Jaffna}) # combine data into one df

prcp_dly['DOY'] = prcp_dly.index.day_of_year # create day of year column
prcp_dlyClim_Negombo = prcp_dly.groupby('DOY')['Negombo'].mean() # calculate climatology
prcp_dlyClim_Jaffna  = prcp_dly.groupby('DOY')['Jaffna'].mean()   # calculate climatology
prcp_dlyClim = pd.DataFrame({'Negombo': prcp_dlyClim_Negombo, 'Jaffna': prcp_dlyClim_Jaffna})  # combine data into one df

print(T2M_dlyClim)



## Plot daily climatologies
########################################################################################

# First, the temperature plot
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(T2M_dlyClim.index, T2M_dlyClim['Negombo'], label='Negombo', color=color_Negombo, linestyle='-', linewidth=2)
ax.plot(T2M_dlyClim.index, T2M_dlyClim['Jaffna'], label='Jaffna', color=color_Jaffna, linestyle='-', linewidth=2)

# Add title and labels
ax.set_xlabel('Day of Year')
ax.set_ylabel('Temperature (°C)')

# Show legend
ax.legend()

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Adjust layout to avoid label cutoff
plt.tight_layout()

# Save the figure
dir_out = '/home/local/WIN/cyasana1/Code/course_climInfDis/projectExample/outputPlots/'
fileName = 'tseries_temp_dlyClim'
if not os.path.isdir(dir_out):
    os.makedirs(dir_out)
plt.savefig(dir_out + fileName + ".png", dpi=300, bbox_inches="tight")
plt.close(fig)

# Next, the precipitation plot
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(prcp_dlyClim.index, prcp_dlyClim['Negombo'], label='Negombo', color=color_Negombo, linestyle='-', linewidth=2)
ax.plot(prcp_dlyClim.index, prcp_dlyClim['Jaffna'], label='Jaffna', color=color_Jaffna, linestyle='-', linewidth=2)

# Add title and labels
ax.set_xlabel('Day of Year')
ax.set_ylabel('Precipitation (mm/day)')

# Show legend
ax.legend()

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Adjust layout to avoid label cutoff
plt.tight_layout()

# Save the figure
dir_out = '/home/local/WIN/cyasana1/Code/course_climInfDis/projectExample/outputPlots/'
fileName = 'tseries_prcp_dlyClim'
if not os.path.isdir(dir_out):
    os.makedirs(dir_out)
plt.savefig(dir_out + fileName + ".png", dpi=300, bbox_inches="tight")
plt.close(fig)



## Calculate monthly values, monthly climatologies, and min/max values for each calendar month
########################################################################################

# Calculate monthly values from the daily data
T2M_monthly  = T2M_dly.resample('M').mean() # average over month
prcp_monthly = prcp_dly.resample('M').sum() # sum over month

print(T2M_monthly)

# Calculate monthly climatology from the daily values
T2M_monthly['month']  = T2M_monthly.index.month # create month column
T2M_monthlyClim_Negombo = T2M_monthly.groupby('month')['Negombo'].mean() # calculate climatology
T2M_monthlyClim_Jaffna  = T2M_monthly.groupby('month')['Jaffna'].mean()   # calculate climatology
T2M_monthlyClim = pd.DataFrame({'Negombo': T2M_monthlyClim_Negombo, 'Jaffna': T2M_monthlyClim_Jaffna}) # combine data into one df

prcp_monthly['month']  = prcp_monthly.index.month # create month column
prcp_monthlyClim_Negombo = prcp_monthly.groupby('month')['Negombo'].mean() # calculate climatology
prcp_monthlyClim_Jaffna  = prcp_monthly.groupby('month')['Jaffna'].mean()   # calculate climatology
prcp_monthlyClim = pd.DataFrame({'Negombo': prcp_monthlyClim_Negombo, 'Jaffna': prcp_monthlyClim_Jaffna}) # combine data into one df

print(T2M_monthlyClim)

# Calculate min/max values for each calendar month
T2M_monthlyMin_Negombo = T2M_monthly.groupby('month')['Negombo'].min() # calculate min value
T2M_monthlyMin_Jaffna  = T2M_monthly.groupby('month')['Jaffna'].min()  # calculate min value
T2M_monthlyMin = pd.DataFrame({'Negombo': T2M_monthlyMin_Negombo, 'Jaffna': T2M_monthlyMin_Jaffna}) # combine data into one df
T2M_monthlyMax_Negombo = T2M_monthly.groupby('month')['Negombo'].max() # calculate max value
T2M_monthlyMax_Jaffna  = T2M_monthly.groupby('month')['Jaffna'].max()  # calculate max value
T2M_monthlyMax = pd.DataFrame({'Negombo': T2M_monthlyMax_Negombo, 'Jaffna': T2M_monthlyMax_Jaffna}) # combine data into one df

prcp_monthlyMin_Negombo = prcp_monthly.groupby('month')['Negombo'].min() # calculate min value
prcp_monthlyMin_Jaffna  = prcp_monthly.groupby('month')['Jaffna'].min()  # calculate min value
prcp_monthlyMin = pd.DataFrame({'Negombo': prcp_monthlyMin_Negombo, 'Jaffna': prcp_monthlyMin_Jaffna}) # combine data into one df
prcp_monthlyMax_Negombo = prcp_monthly.groupby('month')['Negombo'].max() # calculate max value
prcp_monthlyMax_Jaffna  = prcp_monthly.groupby('month')['Jaffna'].max()  # calculate max value
prcp_monthlyMax = pd.DataFrame({'Negombo': prcp_monthlyMax_Negombo, 'Jaffna': prcp_monthlyMax_Jaffna}) # combine data into one df

print(T2M_monthlyMin)
print(T2M_monthlyMax)


## Plot monthly values
########################################################################################

# First, the temperature plot
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(T2M_monthly.index, T2M_monthly['Negombo'], label='Negombo', color=color_Negombo, linestyle='-', linewidth=2)
ax.plot(T2M_monthly.index, T2M_monthly['Jaffna'], label='Jaffna', color=color_Jaffna, linestyle='-', linewidth=2)

# Add title and labels
ax.set_xlabel('Date')
ax.set_ylabel('Temperature (°C)')

# Show legend
ax.legend()

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Adjust layout to avoid label cutoff
plt.tight_layout()

# Save the figure
dir_out = '/home/local/WIN/cyasana1/Code/course_climInfDis/projectExample/outputPlots/'
fileName = 'tseries_temp_monthly_allTime'
if not os.path.isdir(dir_out):
    os.makedirs(dir_out)
plt.savefig(dir_out + fileName + ".png", dpi=300, bbox_inches="tight")
plt.close(fig)


# Next, the precipitation plot
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(prcp_monthly.index, prcp_monthly['Negombo'], label='Negombo', color=color_Negombo, linestyle='-', linewidth=2)
ax.plot(prcp_monthly.index, prcp_monthly['Jaffna'], label='Jaffna', color=color_Jaffna, linestyle='-', linewidth=2)

# Add title and labels
ax.set_xlabel('Date')
ax.set_ylabel('Precipitation (mm/month)')

# Show legend
ax.legend()

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Adjust layout to avoid label cutoff
plt.tight_layout()

# Save the figure
dir_out = '/home/local/WIN/cyasana1/Code/course_climInfDis/projectExample/outputPlots/'
fileName = 'tseries_prcp_monthly_allTime'
if not os.path.isdir(dir_out):
    os.makedirs(dir_out)
plt.savefig(dir_out + fileName + ".png", dpi=300, bbox_inches="tight")
plt.close(fig)



## Plot monthly climatologies with shading showing min/max for each calendar month
########################################################################################

# First, the temperature plot
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(T2M_monthlyClim.index, T2M_monthlyClim['Negombo'], label='Negombo', color=color_Negombo, linestyle='-', linewidth=2)
ax.plot(T2M_monthlyClim.index, T2M_monthlyClim['Jaffna'], label='Jaffna', color=color_Jaffna, linestyle='-', linewidth=2)

ax.fill_between(T2M_monthlyClim.index, T2M_monthlyMin['Negombo'], T2M_monthlyMax['Negombo'], color=color_Negombo, linewidth=0, alpha=0.2)
ax.fill_between(T2M_monthlyClim.index, T2M_monthlyMin['Jaffna'], T2M_monthlyMax['Jaffna'], color=color_Jaffna, linewidth=0, alpha=0.2)

# Add title and labels
ax.set_xlabel('Month')
ax.set_ylabel('Temperature (°C)')

# Show legend
ax.legend()

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Adjust layout to avoid label cutoff
plt.tight_layout()

# Save the figure
dir_out = '/home/local/WIN/cyasana1/Code/course_climInfDis/projectExample/outputPlots/'
fileName = 'tseries_temp_monthlyClim_wShading'
if not os.path.isdir(dir_out):
    os.makedirs(dir_out)
plt.savefig(dir_out + fileName + ".png", dpi=300, bbox_inches="tight")
plt.close(fig)

# Next, the precipitation plot
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(prcp_monthlyClim.index, prcp_monthlyClim['Negombo'], label='Negombo', color=color_Negombo, linestyle='-', linewidth=2)
ax.plot(prcp_monthlyClim.index, prcp_monthlyClim['Jaffna'], label='Jaffna', color=color_Jaffna, linestyle='-', linewidth=2)

ax.fill_between(prcp_monthlyClim.index, prcp_monthlyMin['Negombo'], prcp_monthlyMax['Negombo'], color=color_Negombo, linewidth=0, alpha=0.2)
ax.fill_between(prcp_monthlyClim.index, prcp_monthlyMin['Jaffna'], prcp_monthlyMax['Jaffna'], color=color_Jaffna, linewidth=0, alpha=0.2)

# Add title and labels
ax.set_xlabel('Month')
ax.set_ylabel('Precipitation (mm/month)')

# Show legend
ax.legend()

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Adjust layout to avoid label cutoff
plt.tight_layout()

# Save the figure
dir_out = '/home/local/WIN/cyasana1/Code/course_climInfDis/projectExample/outputPlots/'
fileName = 'tseries_prcp_monthlyClim_wShading'
if not os.path.isdir(dir_out):
    os.makedirs(dir_out)
plt.savefig(dir_out + fileName + ".png", dpi=300, bbox_inches="tight")
plt.close(fig)
