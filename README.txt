Hi - 
I adapted the scripts that I have been using to run on unity, I have attached output from the latest forecast.  FYI - I think the water level is underpredicting by ~.2-.3 m looking at the latest observations.  
These figures come out different looking on unity and the wind script takes a long time to run and the plot of maximum wind does not plot correctly, I am not sure why - probably something memory/graphics wise as the time series look fine.  

Pranav - Up to you if you want to copy these and use them as a starting point, something different will have to be done to make the max wind plot and it probably makes sense to try to do that from within the script that makes the subset.  The necessary files are all at /work/pi_iginis_uri_edu/djc/c_ric/aaa_postproc/. I edit INP.txt to contain the path to your latest asgs directory and then the it creates an output directory with that name for water level plots and a subdirectory Wind for wind plots

the water level processing is run using sbatch runmu
the wind processing is run using sbatch runW

Thanks
Deb
