# Programming opentrons robot

This script automates a portion of the new [opentrons pipetting robot](https://opentrons.com/) using the [opentrons api (OT-2 API V2)](https://docs.opentrons.com/v2/index.html). More specifically, it automates the dilution step (concentration normalisation) after pcr amplification and a picogreen assay in the arctic protocol. It accepts DNA concentration data in the following format, saved as a csv file

|    | 1   | 2     | 3    | 4    | 5   | 6   | 7   | 8   | 9   | 10  | 11  | 12  |
|----|-----|-------|------|------|-----|-----|-----|-----|-----|-----|-----|-----|
| A  | 677 | 28594 | 3233 | 121  | 121 | 121 | 121 | 121 | 121 | 121 | 121 | 121 |
| B  |26822| 27726 | 43193| 43244| 121 | 121 | 121 | 121 | 121 | 121 | 121 | 121 |
| C  |41125| 1523  | 19965| 5330 | 121 | 121 | 121 | 121 | 121 | 121 | 121 | 121 |
| D  |7455 | 42273 | 2204 | 709  | 121 | 121 | 121 | 121 | 121 | 121 | 121 | 121 |
| E  |38978| 43020 | 312  | 186  | 121 | 121 | 121 | 121 | 121 | 121 | 121 | 121 |
| F  |3312 | 6831  | 121  | 121  | 121 | 121 | 121 | 121 | 121 | 121 | 121 | 121 |
| G  |1476 | 44124 | 121  | 121  | 121 | 121 | 121 | 121 | 121 | 121 | 121 | 121 |
| H  |1650 | 2212  | 121  | 121  | 121 | 121 | 121 | 121 | 121 | 121 | 121 | 121 |

## Simlulate protocol

Create and activate a conda environment to get the minimum python version required for a [non-jupyter opentrons installation](https://docs.opentrons.com/v2/writing.html#non-jupyter-installation)

```bash
conda create -n opentrons_env python=3.7.6
conda activate opentrons_env
```

Install opentrons within conda environment

```bash
pip install opentrons
```

Simulate the protocol [from the command line](https://docs.opentrons.com/v2/writing.html#from-the-command-line)

```bash
opentrons_simulate dilutions_opentrons.py
```
