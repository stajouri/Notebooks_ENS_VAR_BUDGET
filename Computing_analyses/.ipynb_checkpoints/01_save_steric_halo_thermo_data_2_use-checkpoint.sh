#!/bin/bash
#SBATCH --job-name="Save_STE_HALO_THE_2use"
#SBATCH --time=05:30:00
#SBATCH --mem=100GB
#SBATCH --account=isotipic
#SBATCH --partition=standard
#SBATCH --qos=standard
#SBATCH -o err_Save_STE_HALO_THE_2use%j.out
#SBATCH -e out_Save_STE_HALO_THE_2use%j.err

# executable
module load jaspy

python 01_save_steric_halo_thermo_data_2_use.py