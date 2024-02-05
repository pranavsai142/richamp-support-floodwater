#!/bin/bash  

#SBATCH --output=matlabW.out
#SBATCH --error=matlabW.err
#SBATCH -n 1
##SBATCH --mail-user=dcrowley@uri.edu
##SBATCH --mail-type=END
#SBATCH -t 24:00:00
#SBATCH --mem=0
#SBATCH --partition=uri-cpu,cpu
#SBATCH --constraint=avx512 
export FI_PROVIDER=verbs


module purge
module load matlab/r2021a
matlab -nodisplay -nosplash -nodesktop -singleCompThread -r "run('read_RICHAMP_wind.m');exit;"



