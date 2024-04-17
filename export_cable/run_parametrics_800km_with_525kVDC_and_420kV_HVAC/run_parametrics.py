"""Run parametrics and fit cost curves."""


####### Make sure you run this using the electrical-refractor branch of ORBIT

__author__ = "Matt Shields, modified by Becca Fuchs"
__copyright__ = "Copyright 2023, National Renewable Energy Laboratory"
__maintainer__ = "Matt Shields"
__email__ = "matt.shields@nrel.gov"

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
#custom_config  = 'configs/base_config.yaml'
custom_config  = 'configs/base_config_2GW.yaml'
# custom_weather = "data/weather/swh_ws100m_maine_2010_thru_2022.csv"


if __name__ == '__main__':
    # Point ORBIT to the custom data libraries in the anlaysis repo
    # initialize_library(custom_library)
    # Load in the input configuration YAML
    
    # Point ORBIT to the custom data libraries in the analysis repo
    initialize_library(custom_library)
    
    config = load_config(custom_config)

    # Print out the required information for input config
    phases = ['ArraySystemDesign',
                'ElectricalDesign', # Changed from ElectricalDesign
                'SemiSubmersibleDesign',
                #'SemiTautMooringSystemDesign',
                'MooringSystemDesign',
                'ArrayCableInstallation',
                'ExportCableInstallation',
                'MooringSystemInstallation',
                'FloatingSubstationInstallation',
                'MooredSubInstallation']
    expected_config = ProjectManager.compile_input_dict(phases)
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(expected_config)

    # Initialize and run project
#     weather = pd.read_csv(custom_weather, parse_dates=['datetime']).set_index("datetime") # Project installation begins at start of weather file unless otherwise specified in install_phase in input config
#     weather.to_pickle('output/weather_' + custom_config[8:-5] + '.pkl')
    
    # Set up Parametric Manager runs
    distance_range = np.arange(10,400,10)
    cable_range = ['XLPE_2500mm_420kV_dynamic', 'HVDC_2500mm_525kV_dynamic', 'XLPE_1000m_220kV_dynamic'] 
    #cable_range = ['HVDC_2500mm_525kV_dynamic']
    parameters = {
            'export_system_design.cables': cable_range,
            'site.distance_to_landfall': distance_range
    }
        
    results = {
            'num_cables': lambda run: run.num_cables,
            'cable_cost': lambda run: run.total_cable_cost * 1e-6,
            'oss_cost': lambda run: run.total_substation_cost * 1e-6,
            'num_substations': lambda run: run.num_substations,
            'onshore_cost': lambda run: run.onshore_cost * 1e-6,
            'cable_length': lambda run: run.total_cable_length_by_type 
            #'cable_install': lambda run: run.capex_breakdown['Export System Installation'],
            #'oss_install': lambda run: run.capex_breakdown['Offshore Substation Installation'],
    }
    
    # Run batch
    parametric = ParametricManager(config, parameters, results, module=ElectricalDesign, product=True) 
    parametric.run()
    
    
    # Append total costs and extract each cable type
    
    dist = np.concatenate([distance_range, distance_range, distance_range])
    cable_install_dc = 2.7 / 1.61 /2 * np.ones(distance_range.shape[0]) # 2.7 $M/mi is the install cost per cable (not pair) of 525 kV static HVDC cable.  1.61 mi/km is the unit conversion factor. divided by 2 to get cost per cable not per pair.
    cable_install_ac = 1.3 * 2.25 / 1.61 * np.ones(distance_range.shape[0]) # install cost per km ($/km). Explanation: 1.3 is $M/mile (TRC from Atlantic project), 1.61 mi/km = $/km; 2.25 is the scaling factor from 220 kV to 420 kV HVAC from Xiang et al. (2016)
    cable_install_ac_220 = 1.3 / 1.61 * np.ones(distance_range.shape[0]) # install cost per km ($/km). Explanation: 1.3 is $M/mile (TRC from Atlantic project), 1.61 mi/km = $/km; 2.25 is the scaling factor from 220 kV to 420 kV HVAC from Xiang et al. (2016)
    
    #oss_install = np.concatenate([oss_install_ac, oss_install_dc])
    cable_install = np.concatenate([cable_install_ac, cable_install_dc, cable_install_ac_220])
    
    print('The cost of one OSS substation at selected index: ' + str(parametric.results['oss_cost'][0]*1.3)) # index 9 is 100 km.

    parametric.results['total_cost'] = parametric.results['cable_cost'] + cable_install * dist * parametric.results['num_cables'] + (parametric.results['oss_cost'] * 1.3) * parametric.results['num_substations'] + parametric.results['onshore_cost'] # 1.3 multiplier for installation, install rate of +%30 frmm DNV
    
    # parametric.results['export_system_design.cables'].unique()
    # Out[6]: 
    # array(['XLPE_2500mm_420kV_dynamic', 'HVDC_2500mm_525kV_dynamic',
    #        'XLPE_1000m_220kV_dynamic'], dtype=object)
    
    

    #pp.pprint(parametric.results)
    
    fig, ax = plt.subplots()
    
    cable_results = {}
    for c in cable_range:
        l = 'ORBIT data for ' + str(c)
        cable_results[c] = parametric.results.loc[parametric.results['export_system_design.cables'] == c]['total_cost'].values * 1e6 / (config['plant']['capacity'] * 1000)
    
    
    # Print equations for HVAC and HVDC separately
    poly_order = 3
    bestfit = np.polyfit(distance_range, cable_results[cable_range[0]], poly_order)
    f = np.poly1d(bestfit)
    print('Equation for HVAC 420 kV: ', f)
    
    poly_order = 3
    bestfit = np.polyfit(distance_range, cable_results[cable_range[1]], poly_order)
    f = np.poly1d(bestfit)
    print('Equation for HVDC 525 kV: ', f)
    
    poly_order = 3
    bestfit = np.polyfit(distance_range, cable_results[cable_range[2]], poly_order)
    f = np.poly1d(bestfit)
    print('Equation for HVAC 220 kV: ', f)
    
    # HVAC uneconomical at least past 400 k (which is around index 40), so putting placeholders of NaN so values to not appear on plot and skew scale.
    cable_results[cable_range[0]][40:] = np.nan
       
    ax.plot(distance_range, cable_results[cable_range[1]], '.', label = 'ORBIT results for 525 kV HVDC system')
    
    # Put NaNs for HVAC cables past 70 km.
    cable_420_to_plot = cable_results[cable_range[0]]
    cable_420_to_plot[10:] = np.nan
    ax.plot(distance_range, cable_420_to_plot, 'x', label = 'ORBIT results for 420 kV HVAC system')
    
    cable_220_to_plot = cable_results[cable_range[2]] 
    cable_220_to_plot[10:] = np.nan
    ax.plot(distance_range, cable_220_to_plot, '.', label = 'ORBIT results for 220 kV HVAC system')
        
        
    # Find crossover point and plot single curve
    cable_comp = (cable_results[cable_range[0]] < cable_results[cable_range[1]])
    crossover_ind = [i for i, x in enumerate(cable_comp) if not x][0]
    print(crossover_ind)
    
    print('HVDC_2500mm_525kV_dynamic')
    print(parametric.results.loc[parametric.results['export_system_design.cables']=='HVDC_2500mm_525kV_dynamic'].cable_cost)
    
    print('price per cable $/kW')
    #print('XLPE_2500mm_420kV_dynamic')
    #print(parametric.results.loc[parametric.results['export_system_design.cables']=='XLPE_2500mm_420kV_dynamic'].cable_cost)
 
    ax.legend()
    ax.set_xlabel('Export cable length (km)')
    ax.set_ylabel('Export system cost, ($/kW)')
    ax.set_ylim(ymin=0)
    ax.set_xlim(xmin=10)
    plt.margins(x=10)
    ax.get_yaxis().set_major_formatter(mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

    plt.savefig('output/export_cable_new.png')
    


    