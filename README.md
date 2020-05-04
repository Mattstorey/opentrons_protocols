# Programming opentrons robot

This script automates a portion of the new [opentrons pipetting robot](https://opentrons.com/) using the [opentrons api (OT-2 API V2)](https://docs.opentrons.com/v2/index.html). More specifically, it automates the dilution step (concentration normalisation) after PCR amplification and a picogreen assay in the arctic protocol on all samples above the threshold concentration. It then performs the end-repair and barcoding on all normalized samples. Samples are then consolidated into a single tube.

## Input data

This protocol accepts raw DNA concentration data from the Optima plate reader in .xlsx format. The most recent .xlsx file will be read in from /path/on/robot/ to serve as an entry point to the script. Upload an .xlsx file relating to the samples to run the script.

## Info

- Save plate reader output as a .xlsx file in /path/on/robot/
- The samples will need to be laid out as described in the SARS_SOP.
- Up to 24 samples per run.
- Samples with a concentration < 4ng/ul will be skipped.
- The position of the sample on the plate will determine which barcode is used.
- Columns 1,2 and 3 can contain sample data. Column 4 must contain Pico standards data.

Example of a plate layout of 21 samples and Pico green standards, with optima data in cells:

|    |Sample|Sample |Sample |Pico  |     |     |     |     |     |     |     |     |
|----|------|-------|-------|------|-----|-----|-----|-----|-----|-----|-----|-----|
|    | 1    | 2     | 3     | 4    | 5   | 6   | 7   | 8   | 9   | 10  | 11  | 12  |
| A  | 677  | 28594 | 3233  |121   |     |     |     |     |     |     |     |     |
| B  |26822 | 27726 | 43193 |43244 |     |     |     |     |     |     |     |     |
| C  |41125 | 1523  | 19965 |5330  |     |     |     |     |     |     |     |     |
| D  |7455  | 42273 | 2204  |709   |     |     |     |     |     |     |     |     |
| E  |38978 | 43020 | 312   |186   |     |     |     |     |     |     |     |     |
| F  |3312  | 6831  |       |      |     |     |     |     |     |     |     |     |
| G  |1476  | 44124 |       |      |     |     |     |     |     |     |     |     |
| H  |1650  | 2212  |       |      |     |     |     |     |     |     |     |     |

## Simulate protocol

Create and activate a conda environment to get the minimum python version required for a [non-jupyter opentrons installation](https://docs.opentrons.com/v2/writing.html#non-jupyter-installation)

```bash
conda env create -f opentrons_env.yaml
conda activate opentrons_env
```

Simulate the protocol [from the command line](https://docs.opentrons.com/v2/writing.html#from-the-command-line)

```bash
opentrons_simulate normalisation.py
```

## Deck lay out

This protocol requires:

- Tips
- Temp block
- End repair kit
- Barcodes
