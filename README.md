# performance-predictor
A performance predictor for parallel applications on multicore architecture. Using the performance metrics of a parallel program on single and double software threads on some hardware configuration, predicting the overall speedup of the program when running on different hardware.
## Installation and build guides
The data generation is built and tested on NYU CIMS server and thus require a linux environment to work. Other dependencies include:
1. Install `multi2sim`
2. Install `Python3` and `pip3`
2. Python3 libraries like: `pandas`, `numpy` and `seaborn`
3. Run the following command `export m2s=<path_to_m2s_binary>` to set the environment variable. The `m2s` binary should be located in the `bin` folder of the installation directory.
## Training the model
1. `cd configgen\`
2. Run `python3 .\gen_all_configs.py` to generate all the hardware configurations. These configs will be used in `Step 3` to run simulations.
3. `cd ..\datagen\`
4. Run `.\datagen\datagen.sh` to generate the metric data of all the programs in the `exe` folder using `ctx_config` and hardware configurations generated in `Step 3`. The generated data will be stored in `\memout`, `\out` and `\sysout` folders.
5. `cd ..\sim_data\`
6. Run `python3 .\etl_data.py` to populate `stats.csv` with the metrics required for training the ML model.
7. `cd ..\predictor\`
8. Run `python3 .\generate_performance_predictor.py`. This will automatically use the `stats.csv` file to train the ML model on the generated data.
## Predicting the performance
First, we need to collect the same metric as the training step about the program in question. To do that, run the following command: 

```$m2s --x86-sim detailed --x86-config <path-to-x86-config-file> --mem-config <path-to-mem-config-file> --mem-report <path-to-mem-output-file> <exename> <args>```

This command needs to be run in the same folder containing the `<exename>` to be run. Also, the program `<exename>` should be run once using single software thread and another time using two software threads in the program. The `<mem-config-file>` and `<x86-config-file>` should be created using the reference of `.\configgen\configs\mem_configs\16\1.ini` and `.\configgen\configs\x86_configs\16\1.ini` files respectively. To see all the possible values of these hardware configuration files, please refer to `.\configgen\mem_config.ini` and `.\configgen\x86_config.ini`, or visit: http://www.multi2sim.org/downloads/m2s-guide-4.2.pdf.

The data will be outputed on the screen as well as `<path-to-mem-output-file>` file. Using these two data points, populate the fields of `.\predictor\test_input.yml` (Check `.\predictor\example_test_input.yml` for a sample). After that, do the following steps:
1. `cd .\predictor\`
2. `python3 test_performance_predictor.py` 