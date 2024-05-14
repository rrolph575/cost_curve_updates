# Basic ORBIT run to get export system costs
from copy import deepcopy
import sys
sys.path.insert(0, '/Users/sbredenk/Repos/ORBIT') # only include this if notebook path and repo path are different
from ORBIT import ProjectManager
from ORBIT.phases.design import ElectricalDesign

base = {
    'export_cable_install_vessel': 'example_cable_lay_vessel',
    'site': {'distance': 100, 'depth': 45, 'distance_to_landfall': 100},
    'plant': {'capacity': 1200}, 
    'turbine': {'turbine_rating': 12},
    'oss_install_vessel': 'example_heavy_lift_vessel',
    'feeder': 'future_feeder',
    'export_system_design': {
        'cables': "XLPE_1000mm_220kV",
    },
    'design_phases': [
        'ElectricalDesign'
    ],
    'install_phases': [
        'ExportCableInstallation',
        'OffshoreSubstationInstallation'
    ],
}

config = deepcopy(base)

# CHANGE THESE TO CHANGE PROJECT SPECS
plant_capacity = 1200
cable = 'XLPE_1000mm_220kV'


config['plant']['capacity'] = plant_capacity
config['export_system_design']['cables'] = cable

project = ProjectManager(base)
project.run()

oss_design = project.capex_breakdown['Offshore Substation']
cable_design = project.capex_breakdown['Export System']
oss_install = project.capex_breakdown['Offshore Substation Installation']

if project.phases['ElectricalDesign'].cable.cable_type == 'HVAC':
    cable_install = config['site']['distance_to_landfall']*0.621*1.3e6*3
    
elif project.phases['ElectricalDesign'].cable.cable_type == 'HVDC-monopole': 
    cable_install = config['site']['distance_to_landfall']*0.621*1.6e6
else:
    cable_install = config['site']['distance_to_landfall']*0.621*2.7e6
    

# OUTPUTS
print('Offshore Substation Costs: ', oss_design + oss_install)
print('Export Cable Costs: ', cable_design + cable_install)
print('Total Export Costs: ', oss_design + oss_install + cable_design + cable_install)