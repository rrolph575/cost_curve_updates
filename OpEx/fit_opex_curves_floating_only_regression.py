# -*- coding: utf-8 -*-
"""
Created on Wed May 24 14:11:13 2023

@author: rrolph
"""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression



###### Scaling. This converts the OpEx ($/kW-yr) from the 15 MW 1 GW value into a $/kW-yr value for a 1GW farm on the respective turbine size.
# Find scaling factor from Shields et al. (2021). These scaling factors are for the 1000 MW farm.
o_and_m_costs = {'Turbine rating': [6, 8, 10, 12, 15, 18, 20], 'O_and_M_in_USDperkW': [100.9, 89.1, 80.34, 74.72, 69.13, 66.91, 66.92]}
scaling_df = pd.DataFrame(data=o_and_m_costs)
# Add column normalized to the lowest value
scaling_df['scaling_factor'] = scaling_df['O_and_M_in_USDperkW']/scaling_df.loc[scaling_df['Turbine rating'] == 15, 'O_and_M_in_USDperkW'].values



## Apply scaling factor to the OpEx data and get new equations
### Inputs for fit
csv_ifile = "opex_15MW_floating_USD_per_kWyr.csv" # output of WOMBAT
df_wombat = pd.read_csv(csv_ifile, header=None).iloc[:,:-1]
swh = df_wombat.iloc[0,1:].values.astype('float')
dist_to_port = df_wombat.iloc[1:,0].values.astype('float')
opex_wombat = df_wombat.iloc[1:,1:].values # this is the value of OpEx ($/kW-yr) for a 1 GW plant with 15 MW. (67 * 15 MW) 

for turbine in [12, 15, 18, 20]:
    print(turbine)
    if turbine == 15: # I am not doing the 15 WM scaling factor because that is what we have data for.
        scaling_factor = 1
    # Convert the WOMBAT OpEx 15 MW for 1 GW ($/kW-year) into $/kW-year for respective turbine ratings in a 1 GW farm
    else:
        scaling_factor = scaling_df.loc[scaling_df['Turbine rating'] == turbine, 'scaling_factor'].values
    opex_scaled_in_USD_per_kWyr = opex_wombat*scaling_factor # This converts the OpEx ($/kW-yr) from the 15 MW 1 GW value into a $/kW-yr value for a 1GW farm on the respective turbine size.
    
    # reshape to final arrays to take the regression on
    opex_scaled_in_USD_per_kWyr = opex_scaled_in_USD_per_kWyr.reshape(dist_to_port.shape[0]*swh.shape[0])
    # make dist_to_port repeat
    dist = dist_to_port.repeat(swh.shape[0])
    wave_height = np.tile(swh, dist_to_port.shape[0])
    
    ### Set up variables by combining the wave height and distance to shore because they are so correlated. Then we have 1 indep variable.
    x = dist*wave_height
    df = pd.DataFrame(data={'dist_times_swh': x, 'opex_scaled': opex_scaled_in_USD_per_kWyr})
    x = df['dist_times_swh'].values.reshape(-1,1)
    opex_to_fit = df['opex_scaled'].values
    
    ### do a simple linear regression on the 'data' to come up with a model
    model = LinearRegression().fit(x,opex_to_fit)
    
    ### predict opex cost based on a new distance to shore and wave height 
    opex_pred = model.predict(x)
    
    # Print the model equation
    m = model.coef_
    intercept = model.intercept_
    print('OpEx ($/kW) for ' + str(turbine) + ' MW at 1 GW farm = ' + str(m[0]) + '*Distance*swh + ' + str(intercept))

    
    # Step 1:
    # Plot Hs and distance on each axis, with z axis showing the OpEx modelled
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.scatter(dist, wave_height, opex_pred, label = 'Modelled_opex')
    ax.set_title('OpEx ($/kW-yr) for 1 GW farm using ' + str(turbine) + 'MW')
    
    # Step 2: 
    # Plot Hs and distance on each axis, with z axis showing the OpEx actual
    ax.plot3D(dist, wave_height, opex_to_fit, label='Scaled opex data')
    ax.set_xlabel('Distance from shore [km]')
    ax.set_ylabel('Wave height [m]')
    ax.set_zlabel('OpEx ($/kW-yr)')
    plt.legend()
    plt.savefig('figures/modelled_vs_scaled_opex_func_of_dist_and_swh_' + str(turbine) + '.png', bbox_inches='tight')
    
    
    # Step 3:
    # Calculate the difference between modelled and actual OpEx
    percent_diff_modelled_and_actual_opex = (100*np.abs(opex_to_fit-opex_pred)/np.mean([opex_to_fit, opex_pred], axis=0))
    
    
    # Step 4: Plot Hs and distance on each axis, with z axis showing the difference btwn modelled and actual OpEx
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    #ax.plot3D(dist, wave_height, percent_diff_modelled_and_actual_opex)
    ax.scatter(dist, wave_height, percent_diff_modelled_and_actual_opex)
    ax.set_title('% difference of Modelled and Actual OpEx')
    ax.set_xlabel('Distance from shore [km]')
    ax.set_ylabel('Wave height [m]')
    ax.set_zlabel('% Difference')
    #ax.cbar()
    plt.savefig('figures/percent_diff_btwn_modelled_and_actual' + str(turbine) + '.png', bbox_inches='tight')
    #ax.invert_xaxis()
    #ax.view_init(azim=45)
    
    
    
    ### Make a 2d plot with colorbar showing the error
    fig, ax = plt.subplots()
    scatter = plt.scatter(dist, wave_height, c=percent_diff_modelled_and_actual_opex, s=175, vmin=0, vmax=10)
    cbar = plt.colorbar(scatter)
    cbar.ax.get_yaxis().labelpad=15
    cbar.ax.set_ylabel('% Difference', rotation=270)
    ax.set_title('% Difference of Modelled and Actual OpEx')
    ax.set_xlabel('Distance from shore [km]')
    ax.set_ylabel('Wave height [m]')
    plt.savefig('figures/percent_diff_btwn_modelled_and_actual_2d' + str(turbine) + '.png', bbox_inches='tight')
    













