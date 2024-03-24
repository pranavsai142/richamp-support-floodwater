# python generateWindGraphs.py --stations OBS_STATIONS.json --wind RICHAMP_wind.nc --rain RICHAMP_rain.nc --obs True

# python scale_and_subset.py -o RICHAMP_wind -sl up-down -hr NLCD_z0_RICHAMP_Reg_Grid.nc -w gfs_wind.nc -wfmt "generic-netcdf" -wr gfs-roughness.nc -z0name generated_z0_interp $z0_sv -r 3000 -sigma 1000 -t 3 -wasync

# Wave
python generateWindGraphs.py --stations OBS_STATIONS.json --waverad /Volumes/ssd/downloads/wave_data/rads.64.nc --waveswh /Volumes/ssd/downloads/wave_data/swan_HS.63.nc --wavemwd /Volumes/ssd/downloads/wave_data/swan_DIR.63.nc --wavemwp /Volumes/ssd/downloads/wave_data/swan_TMM10.63.nc --wavepwp /Volumes/ssd/downloads/wave_data/swan_TPS.63.nc

#  --args.waverad /Volumes/ssd/downloads/wave_data/rads.64.nc --args.waveswh /Volumes/ssd/downloads/wave_data/swan_HS.63.nc --args.wavemwd /Volumes/ssd/downloads/wave_data/swan_DIR.63.nc --args.wavemwp /Volumes/ssd/downloads/wave_data/swan_TMM10.63.nc --args.wavepwp /Volumes/ssd/downloads/wave_data/swan_TPS.63.nc