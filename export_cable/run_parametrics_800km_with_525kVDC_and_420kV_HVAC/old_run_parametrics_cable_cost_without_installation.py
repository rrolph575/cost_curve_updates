"""Run parametrics and fit cost curves."""


####### Make sure you run this using the electrical-refractor branch of ORBIT



import sys
#sys.path.insert(0, '/Users/sbredenk/Repos/ORBIT')
#import sys
import pprint
import numpy as np
import pandas as pd
from ORBIT.phases.design import ElectricalDesign
from ORBIT import ParametricManager, ProjectManager, load_config
from ORBIT.core.library import initialize_library
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import cm

import os
if 'DATA_LIBRARY' in os.environ:
    del os.environ['DATA_LIBRARY']

# set relative paths (alternatively, set absolute paths)
custom_library = "library"
custom_config  = 'configs/base_config.yaml'
# custom_weather = "data/weather/swh_ws100m_maine_2010_thru_2022.csv"


if __name__ == '__main__':
    # Point ORBIT to the custom data libraries in the anlaysis repo
    # initialize_library(custom_library)
    # Load in the input configuration YAML
    
    # Point ORBIT to the custom data libraries in the anlaysis repo
    initialize_library(custom_library)
    
    config = load_config(custom_config)

    # Print out the required information for input config
    phases = ['ArraySystemDesign',
                'ElectricalDesign',
                'SemiSubmersibleDesign',
                #'SemiTautMooringSystemDesign',
                'MooringSystemDesign',
                'ArrayCableInstallation',
                'ExportCableInstallation',
                'MooringSystemInstallation',
                'FloatingSubstationInstallation',
                'MooredSubInstallation']
    #expected_config = ProjectManager.compile_input_dict(phases)
    pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(expected_config)

    # Initialize and run project
#     weather = pd.read_csv(custom_weather, parse_dates=['datetime']).set_index("datetime") # Project installation begins at start of weather file unless otherwise specified in install_phase in input config
#     weather.to_pickle('output/weather_' + custom_config[8:-5] + '.pkl')
    
    # Set up Parametric Manager runs
    distance_range = np.arange(10,800,10)
    cable_range = ['XLPE_1000m_220kV_dynamic', 'HVDC_2500mm_525kV'] # 'XLPE_1000m_220kV_dynamic'
    parameters = {
            'export_system_design.cables': cable_range,
            'site.distance_to_landfall': distance_range
    }
        
    results = {
            'num_cables': lambda run: run.num_cables,
            'cable_cost': lambda run: run.total_cable_cost * 1e-6,
            'oss_cost': lambda run: run.total_substation_cost * 1e-6,
            'num_substations': lambda run: run.num_substations,
            #'cable_install': lambda run: run.capex_breakdown['Export System Installation'],
            #'oss_install': lambda run: run.capex_breakdown['Offshore Substation Installation'],
    }
    
    # Run batch
    parametric = ParametricManager(config, parameters, results, module=ElectricalDesign, product=True)
    parametric.run()
    
    
    # Append total costs and extract each cable type
    
    dist = np.concatenate([distance_range, distance_range])
    oss_install_dc = 64 * np.ones(distance_range.shape[0])
    oss_install_ac = 3 * np.ones(distance_range.shape[0])
    cable_install_dc = 1.6 / 1.61 * np.ones(distance_range.shape[0])
    cable_install_ac = 0.609* 3 * np.ones(distance_range.shape[0])
    
    #oss_install = np.concatenate([oss_install_ac, oss_install_dc])
    #cable_install = np.concatenate([cable_install_ac, cable_install_dc])
    oss_install = 0  ### setting to zero to only include cabling capex 
    cable_install = 0 
    
    parametric.results['total_cost'] = parametric.results['cable_cost'] + cable_install * dist + (parametric.results['oss_cost'] + oss_install) * parametric.results['num_substations']
    

    pp.pprint(parametric.results)
    
    fig, ax = plt.subplots()
    
    cable_results = {}
    for c in cable_range:
        l = 'ORBIT data for ' + str(c)
        cable_results[c] = parametric.results.loc[parametric.results['export_system_design.cables'] == c]['total_cost'].values * 1e6 / (config['plant']['capacity'] * 1000)
    
    
    # Print equations for HVAC and HVDC separately
    poly_order = 3
    bestfit = np.polyfit(distance_range, cable_results[cable_range[0]], poly_order)
    f = np.poly1d(bestfit)
    print('Equation for HVAC 220 kV: ', f)
    
    poly_order = 3
    bestfit = np.polyfit(distance_range, cable_results[cable_range[1]], poly_order)
    f = np.poly1d(bestfit)
    print('Equation for HVDC 525 kV: ', f)
    
    # HVAC uneconomical at least past 400 k (which is around index 40), so putting placeholders of NaN so values to not appear on plot and skew scale.
    cable_results[cable_range[0]][40:] = np.nan
    
    ax.plot(distance_range, cable_results[cable_range[0]], 'x', label = 'ORBIT results for 220 kV HVAC system')
    
    ax.plot(distance_range, cable_results[cable_range[1]], '.', label = 'ORBIT results for 525 kV HVDC system')
        
    # Find crossover point and plot single curve
    cable_comp = (cable_results[cable_range[0]] < cable_results[cable_range[1]])
    crossover_ind = [i for i, x in enumerate(cable_comp) if not x][0]
    print(crossover_ind)
        
    least_cost = np.append(cable_results[cable_range[0]][0:crossover_ind], cable_results[cable_range[1]][crossover_ind:])
    
#     ax.plot(distance_range,least_cost,'--', label='Least cost cable')
    
    # Create cost curve
    poly_order = 3
    bestfit = np.polyfit(distance_range, least_cost, poly_order)
    
    f = np.poly1d(bestfit)
    x = np.linspace(distance_range[0], distance_range[-1], 50)
    y = f(x)
    print(f)
    
    ax.plot(x, y, '--', label='Cost curve')
    
    # Include old ORCA cost curve
    orca_float_export = 0.75 * (0.0000000003 * x ** 5 -
          0.0000004450 * x ** 4 +
          0.0002307800 * x ** 3 -
          0.0590666309 * x ** 2 +
          9.6855829573 * x + 83.12)
    
#     ax.plot(x, orca_float_export, ':', label='ORCA cost equation')
    
    
    # Add DNV data
    
    DNV_HVDC = 533 + 2.63 * x
    DNV_HVAC = 235 + 3 * 2.03 * x
    
#     ax.plot(x, DNV_HVAC, label='DNV (HVAC)')
#     ax.plot(x, DNV_HVDC, label='DNV (HVDC monopole)')
    
    ax.legend()
    ax.set_xlabel('Export cable length (km)')
    ax.set_ylabel('Export system cost, ($/kW)')
    ax.get_yaxis().set_major_formatter(mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

    plt.savefig('output/export_cable_new.png')
    
    
    
    # pp.pprint(parametric.results.head())
    
    # cable_vec = np.zeros((40,20))
    # oss_vec = np.zeros((40,20))
    # total_vec = np.zeros((40,20))
    # num2 = int(len(cable_vec) / 2)
    # print(num2)
    # for i in np.arange(20):
        # for j in np.arange(40):
            # index = 20 * j + i 
            # cable_vec[j,i] = parametric.results.cable_cost[index]
            # oss_vec[j,i] = parametric.results.oss_cost[index] * parametric.results.num_substations[index]
            # total_vec[j,i] = parametric.results.cable_cost[index] + parametric.results.oss_cost[index]

    # ind = 18
    
    