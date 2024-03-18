# python generateWindGraphs.py --stations OBS_STATIONS.json --wind RICHAMP_wind.nc --rain RICHAMP_rain.nc --obs True

python scale_and_subset.py -o RICHAMP_wind -sl up-down -hr NLCD_z0_RICHAMP_Reg_Grid.nc -w gfs_wind.nc -wfmt "generic-netcdf" -wr gfs-roughness.nc -z0name generated_z0_interp $z0_sv -r 3000 -sigma 1000 -t 3 -wasync