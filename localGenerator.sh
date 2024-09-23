# python generateWindGraphs.py --stations OBS_STATIONS.json --wind RICHAMP_wind.nc --rain RICHAMP_rain.nc --obs True

# python scale_and_subset.py -o RICHAMP_wind -sl up-down -hr NLCD_z0_RICHAMP_Reg_Grid.nc -w gfs_wind.nc -wfmt "generic-netcdf" -wr gfs-roughness.nc -z0name generated_z0_interp $z0_sv -r 3000 -sigma 1000 -t 3 -wasync

# python scale_and_subset.py -o RICHAMP_wind -sl up-down -hr NLCD_z0_RICHAMP_Reg_Grid.nc -w ../ObservationalWind/scenario_wind/ramram6_222.txt -wfmt "owi-ascii" -wr gfs-roughness.nc -z0name generated_z0_interp $z0_sv -r 3000 -sigma 1000

# python scale_and_subset.py -o RICHAMP_wind -sl up-down -hr NLCD_z0_RICHAMP_Reg_Grid.nc -w ../ObservationalWind/scenario_wind/news_hwrf_subset_10v3_27oct_0_1nov_23_fort.22 -wfmt "owi-306" -wr gfs-roughness.nc -z0name generated_z0_interp $z0_sv -r 3000 -sigma 1000

# python scale_and_subset.py -o RICHAMP_wind -sl up-down -hr NLCD_z0_RICHAMP_Reg_Grid.nc -w ../ObservationalWind/scenario_wind/adjusted_m38.nc -wfmt "owi-netcdf" -wr gfs-roughness.nc -z0name generated_z0_interp $z0_sv -r 3000 -sigma 1000

# python scale_and_subset.py -o RICHAMP_wind -sl up-down -hr NLCD_z0_RICHAMP_Reg_Grid.nc -w ../ObservationalWind/gfs_wind_owi_ascii_2023120818-2023121318_00.wnd -wfmt "owi-ascii" -wr gfs-roughness.nc -z0name generated_z0_interp -r 3000 -sigma 1000 -t 3 -wasync

# python scale_and_subset.py -o RICHAMP_wind -sl up-down -hr NLCD_z0_RICHAMP_Reg_Grid.nc -w ../ObservationalWind/scenario_wind/adjusted_m38_222.txt -wfmt "owi-ascii" -wr gfs-roughness.nc -z0sv -r 3000 -sigma 1000 -t 3 -wasync

# Wave
# python generateWindGraphs.py --stations OBS_STATIONS.json --waverad /Volumes/ssd/downloads/wave_data/rads.64.nc --waveswh /Volumes/ssd/downloads/wave_data/swan_HS.63.nc --wavemwd /Volumes/ssd/downloads/wave_data/swan_DIR.63.nc --wavemwp /Volumes/ssd/downloads/wave_data/swan_TMM10.63.nc --wavepwp /Volumes/ssd/downloads/wave_data/swan_TPS.63.nc


# python generateGraphs.py --stations OBS_STATIONS.json --adcircExists true --wind /Volumes/ssd/ObservationalWind/RICV1_Unity_Dec15_fort.74.nc
# python generateGraphs.py --stations OBS_STATIONS.json --adcircExists true --wind /Volumes/ssd/ObservationalWind/RICV1_Unity_Dec15_fort.74.nc --obsExists true --rainExists true --rain /Volumes/ssd/ObservationalWind/rain_gfs.nc
# python generateGraphs.py --stations OBS_STATIONS.json --rainExists true --rain /Volumes/ssd/ObservationalWind/rain_gfs.nc
# python generateGraphs.py --stations OBS_STATIONS.json --postExists true --wind /Volumes/ssd/downloads/wind_data/RICHAMP_wind.nc --obsExists true
# python generateGraphs.py --stations OBS_STATIONS.json --gfsExists true --wind /Volumes/ssd/ObservationalWind/wind_gfs.nc --obsExists true --rainExists true --rain /Volumes/ssd/ObservationalWind/rain_gfs.nc
# python generateGraphs.py --stations OBS_STATIONS.json --wavesExists true --waverad /Volumes/ssd/downloads/wave_data/rads.64.nc --waveswh /Volumes/ssd/downloads/wave_data/swan_HS.63.nc --wavemwd /Volumes/ssd/downloads/wave_data/swan_DIR.63.nc --wavemwp /Volumes/ssd/downloads/wave_data/swan_TMM10.63.nc --wavepwp /Volumes/ssd/downloads/wave_data/swan_TPS.63.nc
# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true
#python generateGraphs.py --stations OBS_STATIONS.json --wavesExists true --waverad /Volumes/ssd/downloads/wave_data/rads.64.nc --waveswh /Volumes/ssd/downloads/wave_data/swan_HS.63.nc --wavemwd /Volumes/ssd/downloads/wave_data/swan_DIR.63.nc --wavemwp /Volumes/ssd/downloads/wave_data/swan_TMM10.63.nc --wavepwp /Volumes/ssd/downloads/wave_data/swan_TPS.63.nc
# python generateGraphs.py --stations OBS_STATIONS.json --gfsExists true --wind ../ObservationalWind/adcirc_gfs_analysis_wind_pressure_2024051400-2024051900.nc --obsExists true --rainExists true --rain ../ObservationalWind/adcirc_gfs_analysis_rain_2024051400-2024051900.nc

# python generateGraphs.py --stations OBS_STATIONS.json --gfsExists true --wind ../ObservationalWind/gfs_wind.nc --backgroundChoice RHODE_ISLAND_CHAMP
# python generateGraphs.py --stations OBS_STATIONS.json --postExists true --wind ../ObservationalWind/RICHAMP_wind.nc --rainExists true --rain ../ObservationalWind/RICHAMP_rain.nc

# python generateGraphs.py --stations OBS_STATIONS.json --gfsExists true --wind ../ObservationalWind/scenario_wind/test1938.nc --backgroundChoice RHODE_ISLAND_CHAMP

# python generateGraphs.py --stations OBS_STATIONS.json --waterExists true --water sandy.deb.fort.63.nc --backgroundChoice EAST_COAST_OUTLINE --tempDir temp/

# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --waterExists true --water v18.tidal.fort.63.nc --backgroundChoice EAST_COAST_OUTLINE --tempDir temp/


# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --wavesExists true --waveswh swan_HS.63.nc --wavemwd swan_DIR.63.nc --wavemwp swan_TMM10.63.nc --wavepwp swan_TPS.63.nc --waverad rads.64.nc --backgroundChoice EAST_COAST_OUTLINE --tempDir temp/

# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --wavesExists true --waveswh /scratch/workspace/pranav_sai_uri_edu-manrun/AugustSeaLevelRun/forecast/swan_HS.63.nc --wavemwd /scratch/workspace/pranav_sai_uri_edu-manrun/AugustSeaLevelRun/forecast/swan_DIR.63.nc --wavemwp /scratch/workspace/pranav_sai_uri_edu-manrun/AugustSeaLevelRun/forecast/swan_TMM10.63.nc --wavepwp /scratch/workspace/pranav_sai_uri_edu-manrun/AugustSeaLevelRun/forecast/swan_TPS.63.nc --waverad /scratch/workspace/pranav_sai_uri_edu-manrun/AugustSeaLevelRun/forecast/rads.64.nc --waterExists true --water /scratch/workspace/pranav_sai_uri_edu-manrun/AugustSeaLevelRun/forecast/fort.63.nc --backgroundChoice EAST_COAST_OUTLINE --tempDir /scratch/workspace/pranav_sai_uri_edu-manrun/temp/

python generateFunGraphs.py --stations OBS_STATIONS.json --obsExists true --etaExists true --output /Volumes/ssd/downloads/output_funwave/ --backgroundChoice RHODE_ISLAND_CHAMP --tempDir /Volumes/ssd/temp/

# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --rainExists true --rain /Volumes/ssd/ObservationalWind/Ram_RICHAMP_rain.nc --backgroundChoice RHODE_ISLAND_CHAMP --tempDir /Volumes/ssd/temp/
# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --rainExists true --rain /Volumes/ssd/ObservationalWind/henri_gfs_rain.nc --backgroundChoice EAST_COAST_OUTLINE --tempDir /Volumes/ssd/temp/

#python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --waterExists true --water /Volumes/ssd/downloads/ricv1.august.gfs.fort.63.nc --backgroundChoice EAST_COAST_OUTLINE --tempDir /Volumes/ssd/temp/


# python generateGraphs.py --stations OBS_STATIONS.json --postExists true --wind RICHAMP_wind.nc --backgroundChoice RHODE_ISLAND_CHAMP


# python generateGraphs.py --stations OBS_STATIONS.json --gfsExists true --wind ../ObservationalWind/gfs_wind.nc

# python generateGraphs.py --stations OBS_STATIONS.json --gfsExists true --wind ../ObservationalWind/test_american_wind.nc

# python generateGraphs.py --stations OBS_STATIONS.json --rainExists true --rain RICHAMP_rain.nc --tempDir temp/ --backgroundChoice EAST_COAST_OUTLINE

# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --rainExists true --rain henri_rain_gfs.nc --tempDir temp/ --backgroundChoice EAST_COAST_OUTLINE

# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --rainExists true --rain ernesto_rain_gfs.nc --tempDir temp/ --backgroundChoice EAST_COAST_OUTLINE



# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --gfsExists true --wind wind_gfs.nc --tempDir post_temp/ --backgroundChoice RHODE_ISLAND_CHAMP


# python generateGraphs.py --stations MIDWEST_STATIONS.json --rainExists true --rain ../ObservationalWind/test_midwest_rain.nc --gfsExists true --wind ../ObservationalWind/test_midwest_wind.nc --backgroundChoice MIDWEST

# testing end value maps

#python generateGraphs.py --stations OBS_STATIONS.json --gfsExists true --wind /Volumes/ssd/ObservationalWind/wind_gfs.nc
#python generateGraphs.py --stations OBS_STATIONS.json --gfsExists true --wind /Volumes/ssd/ObservationalWind/wind_gfs.nc --wavesExists true --waverad /Volumes/ssd/downloads/wave_data/rads.64.nc --waveswh /Volumes/ssd/downloads/wave_data/swan_HS.63.nc --wavemwd /Volumes/ssd/downloads/wave_data/swan_DIR.63.nc --wavemwp /Volumes/ssd/downloads/wave_data/swan_TMM10.63.nc --wavepwp /Volumes/ssd/downloads/wave_data/swan_TPS.63.nc


#  --args.waverad /Volumes/ssd/downloads/wave_data/rads.64.nc --args.waveswh /Volumes/ssd/downloads/wave_data/swan_HS.63.nc --args.wavemwd /Volumes/ssd/downloads/wave_data/swan_DIR.63.nc --args.wavemwp /Volumes/ssd/downloads/wave_data/swan_TMM10.63.nc --args.wavepwp /Volumes/ssd/downloads/wave_data/swan_TPS.63.nc


# nhc_merge_2024_al_5_018.trk
# python generateRunProperties.py --indir rundir
# 
# python readParametricTrack.py --file ../trackfiles/scenariofiles/datefix.track.ramram6

# python readParametricTrack.py --file ../trackfiles/scenariofiles/datefix.track.m38002
#  nhc_merge_2024_al_5_018.trk

# python readHurdatTrack.py --file ../trackfiles/scenariofiles/datefix.SandyHurdatTrack.txt

# python readHurdatTrack.py --file ../trackfiles/scenariofiles/HoneHurdatTrack.txt

# python generateGraphs.py --stations OBS_STATIONS.json --rainExists true --rain ../WeatherVisualizer/Sandy_RICHAMP_rain.nc --tempDir temp/ --backgroundChoice NORTH_ATLANTIC

# python generateGraphs.py --stations HAWAII_STATIONS.json --rainExists true --rain RICHAMP_rain.nc --tempDir temp/ --backgroundChoice HAWAII


# python generateGraphs.py --stations HAWAII_STATIONS.json --rainExists true --rain hone_rain_gfs.nc --tempDir temp/ --backgroundChoice HAWAII

# python generateGraphs.py --stations HAWAII_STATIONS.json --gfsExists true --wind hone_wind_gfs.nc --tempDir temp/ --backgroundChoice HAWAII
