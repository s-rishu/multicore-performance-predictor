# performance-predictor
A performance predictor for parallel applications on multicore architecture.
## Dependencies
The data generation is built and tested on NYU CIMS server and thus require a linux environment to work. Other dependencies include:
1. Python3
## Installation and build guides
1. Install multi2sim
2. Run the following command `export m2s=<path_to_m2s_binary>` to set the environment variable. The `m2s` binary should be located in the `bin` folder of the installation directory.
3. Run `python3 .\configgen\gen_all_configs.py` to generate all the hardware configurations. These configs will be used in `Step 4` to run simulations.
4. Run `.\datagen\datagen.sh` to generate the metric data of all the programs in the `datagen` folder.
