This folder contains scripts that are used to run ORBIT sweeps.  The output of the ORBIT runs are used to create a cost curve.

The sweeps performed for this semsubmersible model included several turbines that may or may not exist in 
the default ORBIT library. The specifications (mass, rotor diameter, tower dimensions) were capture from ATB 2022 
and other upscaling turbine references that range from 10MW-20MW size. 

The output folder includes 3 files. A "baseline", which uses the existing ORBIT semisubmersible model. As well as a custom_IEA
and custom_IEA2. 

custom_IEA and IEA2 are based on the custom semisubmersible platform designed for the IEA15MW turbine (UMaine Volturn Ref. Platform)

The difference between the two files is the pontoon wall thickness because the UMaine paper did not specific how thick the 
substructure steel was. A thickness of 3.5mm was chosen such that the curve passed through the UMaine's results

The run_semisub_analysis.py is a python script that runs and generates the data files found in the output folder. 
It is best to update some of the variable names and turbine names between lines 16 and 25 prior to running. 

Then plot_semisub_analysis.ipynb is a Jupyter notebook that plots the results from run_semisub_analysis. You may have to adjust
some of the file paths to ensure that the read_csv calls point to the correct file. 