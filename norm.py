from opentrons import protocol_api
import pandas as pd
import numpy as np
import string
import sys
import glob
import os
import time

#!{sys.executable} -m pip install xlrd


# Set the required concentration of final diluted solution per well (ng/ul)
final_conc = 2


## Get most recent uploaded input file from plate reader 
list_of_xlsx_files = glob.glob('*.xlsx') # will need path of where these are on the robot file system
latest_file = max(list_of_xlsx_files, key=os.path.getctime)
c_time = os.path.getctime(latest_file)
local_time = time.ctime(c_time) 
print("Input file created:", local_time) 
## Continue if correct
input("Press Enter to continue...")

## Get raw data from excel file (sheet = "End point")
optima_raw = pd.read_excel(latest_file, usecols="B:E", skiprows=14)  

## Calc standard curve equation
stnds_values = optima_raw.loc[:4,4] ## Make sure this is set up clearly in the SOP 
stnds_concs = [0, 1000, 100, 10, 1] ## Make sure this is set up clearly in the SOP 

## Standard curve equation 
f = np.polyfit(stnds_values, stnds_concs, deg=1)

## Calc the concentrations of each sample.
sample_concs = (optima_raw.loc[:,:3]*f[0]+f[1])/10
## Set to Nan of too low to be useful. This will 'count' what samples are to be processed 
sample_concs = sample_concs.applymap(lambda x: np.NaN if x <= (final_conc * 2) else x)

## Complementry functions to calulate the dilution volumes
## Assume a max PCR vol avaliable of 20ul 

def get_pcr_prod(sample_conc, final_conc = final_conc):
    ## Amount of PCR product to get for nomalisation. Skip if too low.
    if sample_conc > 200:
        ## Just get the min the pipette can transfer
        vol1 = 1
    elif 10 <= sample_conc <= 200:  
        vol1 = (final_conc/sample_conc) * 100
    elif final_conc <= sample_conc < 10:
        ## Just take all of it 
        vol1 = 20
    else: #if the conc is too low or 
        return np.NaN 
    
    return round(vol1, 1)


def dilute(sample_conc, final_conc = 2):
    ## Amount of H2o to add to get the conc to final_conc
    if sample_conc > 200:
        ## We know we have one ul for all samples over 200ng/ul
        vol2 = (sample_conc/final_conc) - 1
    elif 10 <= sample_conc <= 200:  
        vol2 = 100 - ((final_conc/sample_conc) * 100)
        
    elif final_conc <= sample_conc < 10:
        vol2 = ((sample_conc * 20) / final_conc) - 20 
        
    else: #if the conc is too low 
        return np.NaN 
    
    return round(vol2, 1)
    

## Make some df for the amounts to be transfered
add_pcr_df = sample_concs.applymap(lambda conc: get_pcr_prod(conc))
add_water_df = sample_concs.applymap(lambda conc: dilute(conc))


##A 96 well plate coordinate dataframe
plate_96 = pd.DataFrame({k:[letter + str(k) for letter in string.ascii_uppercase[:8]] for k in range(1,13)})


#Where to use the p20 to add dilutant (transposed across plate to empty columns)
p20_dilute_pos_nans =  plate_96.shift(-4,axis='columns')[add_water_df < 20].values.flatten() ## convert df to list for robot input
p20_dilute_pos = [pos for pos in p20_dilute_pos_nans if type(pos) == str] ## drop nan vlaues from list

#Vol list for p20 addition of dilutant
p20_dilute_vol_nans = add_water_df[add_water_df < 20].values.flatten()
p20_dilute_vol = [vol for vol in p20_dilute_vol_nans if vol > 0]

#Where to use the p300 to add dilutant (transposed across plate to empty columns)
p300_dilute_pos_nans = plate_96.shift(-4,axis='columns')[add_water_df > 20].values.flatten()
p300_dilute_pos = [pos for pos in p300_dilute_pos_nans if type(pos) == str]

#Vol list for p300 addition of dilutant
p300_dilute_vol_nans = add_water_df[add_water_df > 20].values.flatten() 
p300_dilute_vol = [vol for vol in p300_dilute_vol_nans if vol > 0] 


## PCR vols and pos lists for pipettes (always going to be 20ul or less so p20)

##list of volumes of PCR product to transfer
p20_pcr_vols = [vol for vol in add_pcr_df.values.flatten() if vol > 0] ## dataframe to list with no NaNs

## List of positions to transfer from
p20_pcr_pos_from_nan = plate_96[add_pcr_df > 0].values.flatten() 
p20_pcr_pos_from = [pos for pos in p20_pcr_pos_from_nan if type(pos) == str] ##rm NaNa
## List of positions to transfer from
p20_pcr_pos_to_nan = plate_96.shift(-4,axis='columns')[add_pcr_df > 0].values.flatten()
p20_pcr_pos_to = [pos for pos in p20_pcr_pos_to_nan if type(pos) == str]



print(p20_dilute_pos)
print(p300_dilute_pos)


## Robot setup ## 
metadata = {
    'apiLevel': '2.2',
    'author': 'Kemp and Storey'}

def run(protocol: protocol_api.ProtocolContext):
    # Create labware
    sample_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 1)
    
    tiprack_20ul_1 = protocol.load_labware('opentrons_96_filtertiprack_20ul', 4)
    tiprack_300ul_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 3)
    
    dilutant = protocol.load_labware('usascientific_12_reservoir_22ml', 5)
    
    p20 = protocol.load_instrument('p20_single_gen2', 'left', tip_racks = [tiprack_20ul_1])
    p300 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks = [tiprack_300ul_1])
    

    ## Transfer any volumes of H2O under 20ul with the p20
    p20.distribute(p20_dilute_vol, dilutant['A1'], [sample_plate.wells_by_name()[well_name] for well_name in p20_dilute_pos])
    ## Transfer any volumes of H2O for dilution over 20ul with the p300
    p300.distribute(p300_dilute_vol, dilutant['A1'], [sample_plate.wells_by_name()[well_name] for well_name in p300_dilute_pos])
    
    
    ## Transfer the PCR products over
    p20.transfer(p20_pcr_vols, 
                 [sample_plate.wells_by_name()[well_name] for well_name in p20_pcr_pos_from], 
                 [sample_plate.wells_by_name()[well_name] for well_name in p20_pcr_pos_to], 
                 new_tip='always')
    
    
