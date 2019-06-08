# Improving Generalization in Coreference Resolution via Adversarial Training
This repository contains the code for reproducing the experiments in the paper "Improving Generalization in Coreference Resolution via Adversarial Training" by Sanjay Subramanian and Dan Roth, published at \*SEM 2019.
## Requirements
This code was tested using Python 2.7 and Ubuntu 16.04. The requirements.txt co
ntains the packages and corresponding versions of the Python environment used fo
r running this code. You will need to download the word embedding files necessar
y for running the Lee et al. 2018 model. You will also need to download the chec
kpoint for the Lee et al. 2018 model and insert the corresponding path in the lee2018_log_root field in ```experiments_adv.conf```. git-lfs was used to store the ```adv_checkpoint.zip``` file, so you may need git-lfs to clone the repository.
## Modify paths
Make sure to set the paths in ```experiments_adv.conf``` and ```replace_data.py```` to be correct for your system. The allCountries.txt and countryInfo.txt files can be downloaded from geonames.org, and the last_names.txt file contains the last names from the 1990 census, which can be downloaded from https://www2.census.gov/topics/genealogy/1990surnames/dist.all.last#.
## Reproducing Paper Results
First, unzip the adv_checkpoint.zip file to yield the adv_checkpoint directory. To reproduce the results in the paper, please run ```prepare_data.sh``` and subsequently run ```run_experiments.sh``` when the repository is the working directory. Please note that by default the prepare_data.sh script loads the state of the random number generator that we used to generate replacement names to enable exact reproducibility of our results. If you would like generate replacement names at random, you need only comment out the relevant line in ```generate_noleakage.py```.
The results should match those in the paper: http://cogcomp.org/papers/SubramanianRo19.pdf .
## Citation
If you use this work in your research, please cite our paper:
```
@inproceedings{SubramanianRo19,
    author = {Sanjay Subramanian and Dan Roth},
    title = {{Improving Generalization in Coreference Resolution via Adversarial Training}},
    booktitle = {Proc. of the Joint Conference on Lexical and Computational Sematics},
    month = {6},
    year = {2019},
    url = "http://cogcomp.org/papers/SubramanianRo19.pdf",
}
```
