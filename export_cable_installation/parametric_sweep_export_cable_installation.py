# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 10:21:43 2023

Runs different scenarios for export cable installation. These scenarios can be used to generate a cost curve.

__author__ = "Ashesh Sharma, Becca Fuchs, Matt Shields"
__copyright__ = "Copyright 2022, National Renewable Energy Laboratory"

"""

#import openpyxl
import pandas as pd
#import datetime as dt
import pprint
import numpy as np
import matplotlib.pyplot as plt

from ORBIT import load_config
from ORBIT import ProjectManager
from ORBIT.core.library import initialize_library
import os

from sklearn.linear_model import LinearRegression




export_cable_installation_dir = 'C:/Users/rrolph/OneDrive - NREL/cost_curve_updates/export_cable_installation/'
os.chdir(export_cable_installation_dir)
write_mode = False
base_config = load_config('configs/base_config.yaml')
# Point ORBIT to the custom data libraries in the anlaysis repo
initialize_library(os.path.join(os.getcwd(), "library"))  ## !!! this does not work, so manually copied configs into ORBIT library
cable_type = 'HVDC_2500mm_525kV'  # HVDC_2000mm_320kV_dynamic, HVDC_2500mm_525kV, XLPE_1000m_220kV_dynamic (HVAC). !!! Note if you want combined least-cost equation then choose a HVDC type.

print_least_cost_equation = True
DC_voltage = 525

if print_least_cost_equation == True:
    if DC_voltage == 320:
        cable_type = ['XLPE_1000m_220kV_dynamic', 'HVDC_2000mm_320kV_dynamic']
    if DC_voltage == 525:
        cable_type = ['XLPE_1000m_220kV_dynamic', 'HVDC_2500mm_525kV']

distance = np.arange(10, 850, 100) # distance from installation port  .. #must be same length as export cable length array (see loop below)
distance_from_landfall = np.arange(10,850,100) # export cable length
system_costs = np.empty((len(cable_type), distance.shape[0]))

for i, cable in enumerate(cable_type):
    for ind, dist in enumerate(distance):
        #print("\n")
        #print(depth)
    
        if __name__ == '__main__':
    
            mod_config = {
                'site': {
                    'distance': distance[ind],
                    'distance_from_landfall': distance_from_landfall[ind]
                    },
                'export_system_design': {
                    'cables': cable
                    }
                }
    
            # create run config
            run_config = ProjectManager.merge_dicts(base_config, mod_config)
    
            # Print out the required information for input config
            phases = ['ElectricalDesign', 'ExportCableInstallation']
            expected_config = ProjectManager.compile_input_dict(phases)
            pp = pprint.PrettyPrinter(indent=4)
            # pp.pprint(expected_config)
    
            # Initialize and run project
            project = ProjectManager(run_config)
            project.run(include_onshore_construction=False)
    
            # Print some output results
            #pp.pprint(project.capex_breakdown_per_kw)
        
            # print detailed ouptus
            #pp.pprint(project.detailed_outputs)
    
            # make an array of only system costs
            system_costs[i, ind] = project.capex_breakdown['Export System Installation']
          
            
            # Combine the distance from port and distance to POI into one variable becuase they are so correlated
            x = distance*distance_from_landfall
            df = pd.DataFrame(data= {'dist_times_distPOI': x, 'export_installation_cost': system_costs[i]})
            x = df['dist_times_distPOI'].values.reshape(-1,1)
            export_install_cost_to_fit = df['export_installation_cost'].values
            
            # do a simple linear regression on the 'data' to come up with the model
            model = LinearRegression().fit(x, export_install_cost_to_fit)
            
            # Predict export system installation cost
            export_install_cost_pred = model.predict(x)
    
    # Print model equation
    m = model.coef_
    intercept = model.intercept_
    print('Export cable installation ($/kW) for '+ cable_type[i] + ' for a 1 GW farm = ' + str(m[0]) + '*distance*distance_from_landfall + ' + str(intercept))
    
    
    
    # Step 1:
    # Plot distance and distance_from_landfall on each axis, with z axis showing the export installation cost
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.scatter(distance, distance_from_landfall, export_install_cost_pred, label = 'Modelled')
    ax.set_title('Export system installation cost ($/kW) for 1 GW farm using ' + cable_type[i])
    ax.set_title('Export installation ' + cable_type[i])
    # Step 2: 
    # Plot Hs and distance on each axis, with z axis showing the OpEx actual
    ax.plot3D(distance, distance_from_landfall, system_costs[i], label='ORBIT output')
    print('system costs ...........' + str(system_costs[i]))
    ax.set_xlabel('Distance to port [km]')
    ax.set_ylabel('Distance to landfall [km]')
    ax.set_zlabel('Cost * 10 ($/kW)')
    ax.dist = 13
    plt.legend()
    plt.savefig('figures/modelled_vs_orbit_export_install_cost_func_of_dist_and_distPOI_' + str(cable_type[i]) + '.png', bbox_inches='tight')
    
    
    # Step 3:
    # Calculate the difference between modelled and actual OpEx
    percent_diff_modelled_and_actual = (100*np.abs(system_costs[i]-export_install_cost_pred)/np.mean([system_costs[i], export_install_cost_pred], axis=0))
    
    
    # Step 4: Plot Hs and distance on each axis, with z axis showing the difference btwn modelled and actual OpEx
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.scatter(distance, distance_from_landfall, percent_diff_modelled_and_actual)
    ax.set_title('% difference fit vs ORBIT ' + cable_type[i])
    ax.set_xlabel('Distance to port [km]')
    ax.set_ylabel('Distance to landfall [km]')
    ax.set_zlabel('% Difference')
    ax.dist = 13
    plt.savefig('figures/percent_diff_btwn_modelled_and_ORBIT_export_system_install_cost_' + str(cable_type[i]) + '.png', bbox_inches='tight')
    #ax.invert_xaxis()
    #ax.view_init(azim=45)



### Calculate the least cost export cable installation

# Specify the threshold distance where the HVDC becomes cheaper than HVAC.  This depends on the voltage of HVDC.


# Find crossover point
where_least_cost = ()











    
    
    
    
    