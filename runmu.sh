#!/bin/bash  

#SBATCH --output=matlab.out
#SBATCH --error=matlab.err
#SBATCH -n 1
##SBATCH --mail-user=dcrowley@uri.edu
##SBATCH --mail-type=END
#SBATCH -t 24:00:00
#SBATCH --mem=0
#SBATCH --partition=uri-cpu
#SBATCH --constraint=avx512 
export FI_PROVIDER=verbs


module purge
module load matlab/r2021a
matlab -nodisplay -nosplash -nodesktop -singleCompThread -r "run('Plot_Eonly_asgs.m');exit;"
cp -r *_OUT $RICHAMP_OUTDIR


