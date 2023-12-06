# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression



# Read in data
df_monopile_tp_cost_data = pd.read_csv('monopile_tp_cost_data.csv')
water_depth = df_monopile_tp_cost_data['Water depth (m)']
turbine_rating = df_monopile_tp_cost_data['Turbine rating (W)']
monopile_cost = df_monopile_tp_cost_data['Monopile cost ($/kW)']
transition_piece_cost = df_monopile_tp_cost_data['TP cost ($/kW)']
#plant_capacity = 600 # this is to convert the units from $/kW monopile cost to USD monopile cost


### Start with monopile fit
# Plot the raw data
fig, ax = plt.subplots()
ax.scatter(water_depth, monopile_cost)
ax.set_xlabel("Water Depth [m]")
ax.set_ylabel("Monopile cost ($/kW)")
plt.show()



# Make the fit 
def func(water_depth, m, b):
    monopile_cost_in_USD = m*water_depth + b
    return monopile_cost_in_USD

fig, ax = plt.subplots(figsize=(8,6))
for rating in [12, 15, 18, 20]:
    print(rating)
    df_monopile_tp_cost_data_subset = df_monopile_tp_cost_data.loc[df_monopile_tp_cost_data['Turbine rating (W)'] == rating]
    x = df_monopile_tp_cost_data_subset['Water depth (m)']
    x = x.values.reshape((5,1))
    y = df_monopile_tp_cost_data_subset['Monopile cost ($/kW)']

    # Make a fit
    regr = LinearRegression()
    regr.fit(x, y)
    
    # Make a prediction 
    y_pred = regr.predict(np.array([5, 35, 45,60]).reshape(4,1))
    
    #print('Intercept: \n', regr.intercept_)
    #print('Coefficients: \n', regr.coef_)
    
    curve_label = str(rating) + 'MW Monopile_cost ($/kW) = ' + str(round(regr.coef_[0],3)) + ' * water_depth_m + ' + str(round(regr.intercept_,3)) #str(600*1000)
    print(curve_label)
    
    ## Plot the model fit over the data
    plt.scatter(x, y.values, label=curve_label)
    plt.plot(np.array([5, 35, 45, 60]), y_pred)
    
plt.legend(bbox_to_anchor=(1, 0.5))
ax.set_xlabel('Water depth [m]')
ax.set_ylabel('Monopile cost [$/kW]')
ax.set_title('Monopile $/kW value as a function of water depth')
plt.savefig('monopile_cost_curve_USD_per_kW.png', bbox_inches='tight')



#### Do a fit for unit cost instead of $/kW
fig, ax = plt.subplots(figsize=(8,6))
for rating in [12, 15, 18, 20]:
    print(rating)
    df_monopile_tp_cost_data_subset = df_monopile_tp_cost_data.loc[df_monopile_tp_cost_data['Turbine rating (W)'] == rating]
    x = df_monopile_tp_cost_data_subset['Water depth (m)']
    x = x.values.reshape((5,1))
    y = df_monopile_tp_cost_data_subset['Monopile cost ($/kW)']*600*1000 # converting to unit cost for a 600 MW plant.

    # Make a fit
    regr = LinearRegression()
    regr.fit(x, y)
    
    # Make a prediction 
    y_pred = regr.predict(np.array([5, 35, 45,60]).reshape(4,1))
    
    #print('Intercept: \n', regr.intercept_)
    #print('Coefficients: \n', regr.coef_)
    
    curve_label = str(rating) + 'MW Monopile_cost [USD] = ' + str(round(regr.coef_[0],3)) + ' * water_depth_m + ' + str(round(regr.intercept_,3)) #str(600*1000)
    print(curve_label)
    
    ## Plot the model fit over the data
    plt.scatter(x, y.values, label=curve_label)
    plt.plot(np.array([5, 35, 45, 60]), y_pred)
    
plt.legend(bbox_to_anchor=(1, 0.5))
ax.set_xlabel('Water depth [m]')
ax.set_ylabel('Monopile farm cost [USD]')
ax.set_title('Monopile farm cost [USD] as a function of water depth')
plt.savefig('monopile_cost_curve_farm_cost.png', bbox_inches='tight')


# print('This is the old 15MW cost at 30m depth: ')
# print('30 * 2536465.45717362 + 78715384.23273994')
# print('Out[9]: 154809347.94794852'
      
#       monopile_cost_USD_per_kW_15MW_30m_depth_new = 268.1839251 

#       unit_cost_new_for_600MW_farm = monopile_cost_USD_per_kW_15MW_30m_depth_new*600*1000

#       unit_cost_new_for_600MW_farm
#       Out[14]: 160910355.06







###### Below code is trying to make a function using both as independent variables.  Can come back to this later but the fit did not work.
# x = df_monopile_tp_cost_data[['Water depth (m)', 'Turbine rating (W)']]
# y = df_monopile_tp_cost_data['Monopile cost ($/kW)']

# # Make a fit
# regr = LinearRegression()
# regr.fit(x, y)

# print('Intercept: \n', regr.intercept_)
# print('Coefficients: \n', regr.coef_)

# print('The equation for the monopile is: Monopile_cost ($/kW) = (' + str(regr.coef_[0]) + ' * water_depth_m + ' + str(regr.coef_[1]) + ' * turbine_rating_MW / 1e6 + ' +str(regr.intercept_) + ')')


# def monopile_cost_func(depth, rating, plant_capacity):
#     modelled_monopile_cost_in_USD = plant_capacity* (4.568007581500001 * depth + -11.12499961360544 * rating / 1e6 + 300.14513730108837)   
#     return modelled_monopile_cost_in_USD

# # Overlay fit with data
# fig, ax = plt.subplots()
# ax.scatter(water_depth, monopile_cost_func(water_depth, turbine_rating, plant_capacity))
# ax.scatter(water_depth, monopile_cost*plant_capacity, color='k')


### Next do transition piece fit
# Plot the raw data
fig, ax = plt.subplots()
ax.scatter(water_depth, transition_piece_cost)
ax.set_xlabel("Water Depth [m]")
ax.set_ylabel("Transition piece cost ($/kW)")
plt.show()



# Make the fit 
def func(water_depth, m, b):
    tp_cost_in_USD = m*water_depth + b
    return tp_cost_in_USD

fig, ax = plt.subplots(figsize=(8,6))
for rating in [12, 15, 18, 20]:
    print(rating)
    df_monopile_tp_cost_data_subset = df_monopile_tp_cost_data.loc[df_monopile_tp_cost_data['Turbine rating (W)'] == rating]
    x = df_monopile_tp_cost_data_subset['Water depth (m)']
    x = x.values.reshape((5,1))
    y = df_monopile_tp_cost_data_subset['TP cost ($/kW)']

    # Make a fit
    regr = LinearRegression()
    regr.fit(x, y)
    
    # Make a prediction 
    y_pred = regr.predict(np.array([5, 35, 45,60]).reshape(4,1))
    
    #print('Intercept: \n', regr.intercept_)
    #print('Coefficients: \n', regr.coef_)
    
    curve_label = str(rating) + 'MW Transition Piece ($/kW) = ' + str(round(regr.coef_[0],3)) + ' * water_depth_m + ' + str(round(regr.intercept_,3)) #str(600*1000)
    print(curve_label)
    
    ## Plot the model fit over the data
    plt.scatter(x, y.values, label=curve_label)
    plt.plot(np.array([5, 35, 45, 60]), y_pred)
    
plt.legend(bbox_to_anchor=(1, 0.5))
ax.set_xlabel('Water depth [m]')
ax.set_ylabel('TP cost [$/kW]')
ax.set_title('TP $/kW value as a function of water depth')
plt.savefig('TP_cost_curve_USD_per_kW.png', bbox_inches='tight')



#### Do a fit for unit cost instead of $/kW
fig, ax = plt.subplots(figsize=(8,6))
for rating in [12, 15, 18, 20]:
    print(rating)
    df_monopile_tp_cost_data_subset = df_monopile_tp_cost_data.loc[df_monopile_tp_cost_data['Turbine rating (W)'] == rating]
    x = df_monopile_tp_cost_data_subset['Water depth (m)']
    x = x.values.reshape((5,1))
    y = df_monopile_tp_cost_data_subset['TP cost ($/kW)']*600*1000 # converting to unit cost for a 600 MW plant.

    # Make a fit
    regr = LinearRegression()
    regr.fit(x, y)
    
    # Make a prediction 
    y_pred = regr.predict(np.array([5, 35, 45,60]).reshape(4,1))
    
    #print('Intercept: \n', regr.intercept_)
    #print('Coefficients: \n', regr.coef_)
    
    curve_label = str(rating) + 'MW TP_cost [USD] = ' + str(round(regr.coef_[0],3)) + ' * water_depth_m + ' + str(round(regr.intercept_,3)) #str(600*1000)
    print(curve_label)
    
    ## Plot the model fit over the data
    plt.scatter(x, y.values, label=curve_label)
    plt.plot(np.array([5, 35, 45, 60]), y_pred)
    
plt.legend(bbox_to_anchor=(1, 0.5))
ax.set_xlabel('Water depth [m]')
ax.set_ylabel('TP farm cost [USD]')
ax.set_title('TP farm cost [USD] as a function of water depth')
plt.savefig('tp_cost_curve_farm_cost.png', bbox_inches='tight')






