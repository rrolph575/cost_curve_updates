# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 10:21:43 2023

Runs different scenarios for mooring system design. These scenarios can be used to generate a cost curve.

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
mooring_system_dir = 'C:/Users/rrolph/OneDrive - NREL/cost_curve_updates/mooring_system/'
os.chdir(mooring_system_dir)
write_mode = False
base_config = load_config('base_config.yaml')

depths = np.arange(500, 1301, 100)
system_costs = np.empty(depths.shape)

for ind, depth in enumerate(depths):
    print("\n")
    print(depth)

    if __name__ == '__main__':

        mod_config = {
            'site': {
                'depth': depth,
                }
            }

        # create run config
        run_config = ProjectManager.merge_dicts(base_config, mod_config)

        # Print out the required information for input config
        phases = ['SemiTautMooringSystemDesign']
        expected_config = ProjectManager.compile_input_dict(phases)
        pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(expected_config)

        # Initialize and run project
        project = ProjectManager(run_config)
        project.run(include_onshore_construction=False)

        # Print some output results
        #pp.pprint(project.capex_breakdown_per_kw)
    
        # print detailed ouptus
        pp.pprint(project.detailed_outputs)

        # make an array of only system costs
        system_costs[ind] = project.detailed_outputs['system_cost']


        
### create an equation from the cost data
polyorder = 3
bestfit = np.polyfit(depths, system_costs, polyorder)

f = np.poly1d(bestfit)
x = depths
y = f(x)
print(f)

fig, ax = plt.subplots()
ax.plot(x, y/15000, '--', label = 'Cost curve')
#ax.plot(x, system_costs/15000, label = 'Costs') # plotting actual 'data'
#ax.legend()
ax.set_xlabel('Depth (m)')
ax.set_ylabel('Mooring system cost, ($/kW)')
plt.savefig('mooring_cost_curve.png', bbox_inches = 'tight')









        
        
        
        
        