#!/bin/sh

cd examples
# run some test script and look at the output to find possible errors introduced in a recent code change

python xrayutilities_experiment_Powder_signal_calculation.py  
python xrayutilities_peak_angles_beamtime.py
python xrayutilities_experiment_angle_calculation.py
python xrayutilities_polefigure.py
python xrayutilities_angular2hkl_conversion.py              
python xrayutilities_experiment_kappa.py                      
python xrayutilities_read_panalytical.py
#python xrayutilities_ccd_parameter.py # no data included for this example
#python xrayutilities_export_data2vtk.py # no data included for this example                    
#python xrayutilities_read_seifert.py # no data included for this example
python xrayutilities_components_of_the_structure_factor.py
python xrayutilities_id01_functions.py
python xrayutilities_read_spec.py
python xrayutilities_define_material.py
python xrayutilities_io_cif_parser.py
python xrayutilities_reflection_strength.py
python xrayutilities_energy_dependent_structure_factor.py   
python xrayutilities_io_cif_parser_bi2te3.py
#python xrayutilities_example_plot_3D_ESRF_ID01.py # no data included for this example
#python xrayutilities_linear_detector_parameters.py # no data included for this example
python xrayutilities_experiment_Powder_example_Iron.py
python xrayutilities_materials_Alloy_contentcalc.py
python xrayutilities_orientation_matrix.py

