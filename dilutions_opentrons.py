import pandas as pd
from opentrons import protocol_api

##### Configuration #####

# Set the required concentration of final diluted solution per well (ng/ul)
C2 = 2
# Set the desired final amount/volume of diluted solution per well (ul) (Max 360ul)
V2 = 300

##### Input data #####

# Read in stock concentation data output by picogreen assay (ensuring data is formatted 
# correctly for a 96 well plate: columns 1-12 and rows A-H)
stock_conc_data = pd.read_csv('picogreen.csv', 
    usecols = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 
    nrows = 8,
    index_col = 0)

##### Data manipulations #####

# Transpose data so the final list of stock and dilutant volumes are used by p300.distribute
# and p300.transfer 'column-wise' (ie. A1, A2, A3 ... H10, H11, H12)
stock_conc_data = stock_conc_data.transpose()

# Calculate volume of stock and dilutant required for each well (ul)
stock_vol_data = C2*V2/stock_conc_data
dilutant_vol_data = V2-stock_vol_data

# Convert to list
stock_vol = stock_vol_data.values.flatten().tolist()
dilutant_vol = dilutant_vol_data.values.flatten().tolist()

# Drop any empty wells/missing values
stock_vol = [x for x in stock_vol if str(x) != 'nan']
dilutant_vol = [x for x in dilutant_vol if str(x) != 'nan']

##### Opentrons protocol #####
metadata = {
    'apiLevel': '2.2',
    'author': 'Leah Kemp'}

def run(protocol: protocol_api.ProtocolContext):
    # Create labware
    plate_stock = protocol.load_labware('corning_96_wellplate_360ul_flat', 1)
    plate_diluted = protocol.load_labware('corning_96_wellplate_360ul_flat', 2)
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 3)
    tiprack_2 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    dilutant = protocol.load_labware('usascientific_12_reservoir_22ml', 5)
    p300 = protocol.load_instrument('p300_single', 'right', tip_racks = [tiprack_1, tiprack_2])

    # Distribute variable volumes of dilutant from dilutant reservoir to all wells of 
    # 'plate_diluted' and automatically refill when more dilutant is required. Use one tip.
    p300.distribute(
        dilutant_vol, 
        dilutant['A12'], 
        plate_diluted.wells()[:len(dilutant_vol)],
        new_tip = 'once')

    # Move variable volumes of stock (pcr product) from 'plate_stock' to 'plate_diluted'. 
    # Mix with dilutant, get a new tip before each sample and blow out after every 
    # dispense. Mix with 80% of the total volume.
    p300.transfer(
        stock_vol, 
        plate_stock.wells()[:len(stock_vol)],
        plate_diluted.wells()[:len(dilutant_vol)],
        mix_after = (3, V2*0.8),
        blow_out = True,
        new_tip = 'always')