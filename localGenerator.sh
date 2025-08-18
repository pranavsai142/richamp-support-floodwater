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

# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --wavesExists true --waveswh /scratch/workspace/pranav_sai_uri_edu-runup/AugustSeaLevelRun/forecast/swan_HS.63.nc --wavemwd /scratch/workspace/pranav_sai_uri_edu-runup/AugustSeaLevelRun/forecast/swan_DIR.63.nc --wavemwp /scratch/workspace/pranav_sai_uri_edu-runup/AugustSeaLevelRun/forecast/swan_TMM10.63.nc --wavepwp /scratch/workspace/pranav_sai_uri_edu-runup/AugustSeaLevelRun/forecast/swan_TPS.63.nc --waverad /scratch/workspace/pranav_sai_uri_edu-runup/AugustSeaLevelRun/forecast/rads.64.nc --waterExists true --water /scratch/workspace/pranav_sai_uri_edu-runup/AugustSeaLevelRun/forecast/fort.63.nc --backgroundChoice EAST_COAST_OUTLINE --tempDir /scratch/workspace/pranav_sai_uri_edu-runup/temp/

# python generateFunGraphs.py --stations OBS_STATIONS.json --input /Volumes/ssd/downloads/input.txt --obsExists true --etaExists true --output /Volumes/ssd/downloads/output_funwave/ --backgroundChoice RHODE_ISLAND_CHAMP --tempDir /Volumes/ssd/temp/

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
# 
# python generateGraphs.py --stations NAPATREE_NORMAL_STATIONS.json \
# --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_TPS.63.nc \
# --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/fort.63.nc \
# --meshExists true --mesh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/fort.14 \
# --generateRunup true \
# --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE
# 

# python generateGraphs.py --stations WINNAPAUG_STATIONS.json --obsExists true --gfsExists true --wind /scratch3/workspace/pranav_sai_uri_edu-runup/Feb25PrinciplesRun/feb25.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice WINNAPAUG_OUTLINE

# python generateGraphs.py --stations WINNAPAUG_STATIONS.json --obsExists true --gfsExists true --wind /scratch3/workspace/pranav_sai_uri_edu-runup/Feb25PrinciplesRun/feb25next.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice WINNAPAUG_OUTLINE

# python generateGraphs.py --stations WINNAPAUG_STATIONS.json --obsExists true --meshExists true --mesh /scratch3/workspace/pranav_sai_uri_edu-runup/Feb25PrinciplesRun/forecast_RI_track/fort.14 --gfsExists true --wind /scratch3/workspace/pranav_sai_uri_edu-runup/Feb25PrinciplesRun/feb25.nc --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/Feb25PrinciplesRun/forecast_RI_track/fort.63.nc --tidewaterExists true --tidewater /scratch3/workspace/pranav_sai_uri_edu-runup/Feb25PrinciplesRun/forecast_RI_track_tides/fort.63.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice WINNAPAUG_OUTLINE

# python generateGraphs.py --stations WINNAPAUG_STATIONS.json --obsExists true --meshExists true --mesh /scratch3/workspace/pranav_sai_uri_edu-runup/Feb25PrinciplesRun/forecast_RI_track_next/fort.14 --gfsExists true --wind /scratch3/workspace/pranav_sai_uri_edu-runup/Feb25PrinciplesRun/feb25next.nc --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/Feb25PrinciplesRun/forecast_RI_track_next/fort.63.nc --tidewaterExists true --tidewater /scratch3/workspace/pranav_sai_uri_edu-runup/Feb25PrinciplesRun/forecast_RI_track_next_tides/fort.63.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice WINNAPAUG_OUTLINE

# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --gfsExists true --wind /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/dec23wind.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE_BEACH

# USE THIS
# python generateGraphs.py --stations NAPATREE_NORMAL_STATIONS.json \
# --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_master_build/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_TPS.63.nc \
# --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/fort.63.nc \
# --stillwaterExists true --stillwater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_wind/fort.63.nc \
# --tidewaterExists true --tidewater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_tides/fort.63.nc \
# --meshExists true --mesh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/fort.14 \
# --generateRunup true \
# --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE

# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --gfsExists true --wind /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/dec23wind.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE


# python generateGraphs.py --stations NAPATREE_NORMAL_STATIONS.json --meshExists true --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE --mesh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/fort.14

# python generateGraphs.py --obsExists true --stations OBS_STATIONS.json --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/fort.63.nc --stillwaterExists true --stillwater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_wind/fort.63.nc --tidewaterExists true --tidewater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_tides/fort.63.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE
# 

# python generateGraphs.py --obsExists true --stations OBS_STATIONS.json --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_master_build/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_TPS.63.nc \
#  --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE

# python generateGraphs.py --stations NAPATREE_NORMAL_STATIONS_OBS.json \
# --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/swan_TPS.63.nc \
# --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/fort.63.nc \
# --stillwaterExists true --stillwater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_wind/fort.63.nc \
# --tidewaterExists true --tidewater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_tides/fort.63.nc \
# --meshExists true --mesh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/fort.14 \
# --generateRunup true \
# --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/dec2022_runup_temp/ --backgroundChoice NAPATREE --graphDirectory Runup2022Profile/

# Graph 2022 Transect
# python generateGraphs.py --stations NAPATREE_NORMAL_TRANSECT_STATIONS.json \
# --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/swan_TPS.63.nc \
# --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/fort.63.nc \
# --stillwaterExists true --stillwater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_wind/fort.63.nc \
# --tidewaterExists true --tidewater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_tides/fort.63.nc \
# --meshExists true --mesh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/fort.14 \
# --generateRunup true \
# --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/dec2022_transect_temp/ --backgroundChoice NAPATREE --graphDirectory Transect2022/

# python generateGraphs.py --obsExists true --stations OBS_STATIONS.json --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/fort.63.nc --stillwaterExists true --stillwater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_wind/fort.63.nc --tidewaterExists true --tidewater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_tides/fort.63.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE --graphDirectory ObsWater2022/

# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --gfsExists true --wind /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/dec22conv.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE --graphDirectory ObsWind2022/

# Watch Hill Mesh
# python generateGraphs.py --stations NAPATREE_NORMAL_TRANSECT_STATIONS.json --obsExists true --meshExists true --mesh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/fort.14 --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE_OFFSHORE


# Correctly format multipanel graphs and create figures
# Obs Water
# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track/fort.63.nc --stillwaterExists true --stillwater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_wind/fort.63.nc --tidewaterExists true --tidewater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_tides/fort.63.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE

# Water swath
# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/fort.63.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE --graphDirectory ObsWaterSwath2022/

# python generateGraphs.py --stations OBS_STATIONS.json --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/fort.63.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE --graphDirectory ObsWaterSwath2022/


# Obs GFS and swath
# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --gfsExists true --wind /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/dec22conv.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice BLOCK_ISLAND_SOUND_OUTLINE --graphDirectory ObsWindSwath2022/

# Obs Waves
# python generateGraphs.py --obsExists true --stations OBS_STATIONS.json --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_waves/swan_TPS.63.nc \
#  --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE --graphDirectory ObsWave2022/
 
#  Wave swath
#  python generateGraphs.py --stations OBS_STATIONS.json --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track/swan_TPS.63.nc \
#  --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE

# Napatree Mesh Map
# python generateGraphs.py --stations NAPATREE_NORMAL_STATIONS.json --meshExists true --mesh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track/fort.14 --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE --graphDirectory NapatreeMesh/


# Napatree Transect Graph
# python generateGraphs.py --stations NAPATREE_NORMAL_STATIONS.json \
# --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track/swan_TPS.63.nc \
# --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track/fort.63.nc \
# --stillwaterExists true --stillwater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_wind/fort.63.nc \
# --tidewaterExists true --tidewater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track_tides/fort.63.nc \
# --meshExists true --mesh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec222022RunupRun/forecast_RI_track/fort.14 \
# --generateRunup true \
# --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE


# __________________________________________________________________________
# Dec 2023 Figures

#  Mesh Map, and Runup
# python generateGraphs.py --stations NAPATREE_NORMAL_STATIONS.json \
# --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_master_build/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_TPS.63.nc \
# --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/fort.63.nc \
# --stillwaterExists true --stillwater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_wind/fort.63.nc \
# --tidewaterExists true --tidewater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_tides/fort.63.nc \
# --meshExists true --mesh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/fort.14 \
# --generateRunup true \
# --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/dec2023_runup_temp/ --backgroundChoice NAPATREE --graphDirectory Runup2023Hard/

# python generateGraphs.py --stations NAPATREE_NORMAL_STATIONS.json \
# --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_master_build/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_TPS.63.nc \
# --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/fort.63.nc \
# --stillwaterExists true --stillwater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_wind/fort.63.nc \
# --tidewaterExists true --tidewater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_tides/fort.63.nc \
# --meshExists true --mesh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/fort.14 \
# --generateRunup true \
# --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/dec23_profile_temp/ --backgroundChoice NAPATREE --graphDirectory Runup2023Profile/


# python generateGraphs.py --stations NAPATREE_NORMAL_STATIONS_OBS_2023.json \
# --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_master_build/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_TPS.63.nc \
# --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/fort.63.nc \
# --stillwaterExists true --stillwater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_wind/fort.63.nc \
# --tidewaterExists true --tidewater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_tides/fort.63.nc \
# --meshExists true --mesh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/fort.14 \
# --generateRunup true \
# --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/dec23_profile_hires_temp/ --backgroundChoice NAPATREE --graphDirectory Runup2023ProfileHiRes/

# ERIN

python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --gfsExists true --wind /scratch3/workspace/pranav_sai_uri_edu-runup/ErinRun/Erin_1612.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE --graphDirectory ErinObsParametricWind/

# python generateGraphs.py --stations OBS_STATIONS.json --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/ErinRun/forecast_RI_track_clean/fort.63.nc --stillwaterExists true --stillwater /scratch3/workspace/pranav_sai_uri_edu-runup/ErinRun/forecast_RI_track_1700_wind/fort.63.nc --tidewaterExists true --tidewater /scratch3/workspace/pranav_sai_uri_edu-runup/ErinRun/forecast_RI_track_tides/fort.63.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE --graphDirectory ErinObsWater/
# 
#  python generateGraphs.py --stations OBS_STATIONS.json --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/ErinRun/forecast_RI_track_clean/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/ErinRun/forecast_RI_track_clean/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/ErinRun/forecast_RI_track_clean/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/ErinRun/forecast_RI_track_clean/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/ErinRun/forecast_RI_track_clean/swan_TPS.63.nc \
#  --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice EAST_COAST_OUTLINE --graphDirectory ErinAdv21ObsWaves/
# 



# EXTREME
# python generateGraphs.py --stations NAPATREE_NORMAL_STATIONS.json \
# --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_master_build/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_TPS.63.nc \
# --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/fort.63.nc \
# --stillwaterExists true --stillwater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_wind/fort.63.nc \
# --tidewaterExists true --tidewater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_tides/fort.63.nc \
# --meshExists true --mesh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/fort.14 \
# --generateRunup true \
# --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/dec23_extreme_temp/ --backgroundChoice NAPATREE --graphDirectory Runup2023Extreme/
# Water swath
# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/fort.63.nc --stillwaterExists true --stillwater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_wind/fort.63.nc --tidewaterExists true --tidewater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_tides/fort.63.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE --graphDirectory ObsWater2023/

# python generateGraphs.py --stations OBS_STATIONS.json --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/fort.63.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE --graphDirectory ObsWaterSwath2023/


# Obs GFS and swath
# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --gfsExists true --wind /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/dec23wind.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice BLOCK_ISLAND_SOUND_OUTLINE --graphDirectory ObsWindSwath2023/

# Obs Waves
# python generateGraphs.py --stations OBS_STATIONS.json --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_TPS.63.nc \
#  --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE --graphDirectory ObsWave2023/


# Transect Graph/
# python generateGraphs.py --stations NAPATREE_NORMAL_TRANSECT_STATIONS.json \
# --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_master_build/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_TPS.63.nc \
# --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/fort.63.nc \
# --stillwaterExists true --stillwater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_wind/fort.63.nc \
# --tidewaterExists true --tidewater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_tides/fort.63.nc \
# --meshExists true --mesh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/fort.14 \
# --generateRunup true \
# --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/dec2023_transectlong_temp/ --backgroundChoice NAPATREE --graphDirectory Transect2023DailyAverage/

# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --waterExists true --water /project/pi_iginis_uri_edu/pranav_sai_uri_edu/RICHAMPHenriAdvisory18-June23/RICHAMP_fort63.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE --graphDirectory HenriObsWaterAdvisory18/


# python generateGraphs.py --obsExists true --stations RUNUP_NAPATREE_STATIONS.json --meshExists true --mesh /Users/pranav/projects/trackfiles/v18.fort.14 --backgroundChoice NAPATREE --tempDir temp --graphDirectory test/

# python generateGraphs.py --stations NAPATREE_NORMAL_STATIONS.json \
# --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track/swan_TPS.63.nc \
# --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track/fort.63.nc \
# --stillwaterExists true --stillwater /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track/fort.63.nc \
# --tidewaterExists true --tidewater /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track/fort.63.nc \
# --meshExists true --mesh /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track/fort.14 \
# --generateRunup true \
# --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE_BEACH


# python generateGraphs.py --stations OBS_STATIONS.json --waterExists true --water /project/pi_iginis_uri_edu/pranav_sai_uri_edu/RICHAMPFilesHenriAdvisory17_1ft/RICHAMP_fort63.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice RHODE_ISLAND_CHAMP

# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --postExists true --wind /project/pi_iginis_uri_edu/pranav_sai_uri_edu/RICHAMPHenriAdvisory18-June23/RICHAMP_wind.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice RHODE_ISLAND_CHAMP

# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --postExists true --wind /scratch3/workspace/pranav_sai_uri_edu-runup/RICHAMP/RICHAMP_wind.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice RHODE_ISLAND_CHAMP
# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/RICHAMP/RICHAMP_fort63.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice PROVIDENCE --graphDirectory barrierOpen/
# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/RICHAMPHenriBarrierClosedGFS/RICHAMP_fort63.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp2/ --backgroundChoice PROVIDENCE --graphDirectory barrierClosed/

# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --rainExists true --rain /scratch3/workspace/pranav_sai_uri_edu-runup/RICHAMP/RICHAMP_rain.nc --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice RHODE_ISLAND_CHAMP


# python generateGraphs.py --stations NAPATREE_NORMAL_STATIONS.json \
# --wavesExists true \
# --waverad /Volumes/ssd/ObservationalWind/wave_data/rads.64.nc \
# --waveswh /Volumes/ssd/ObservationalWind/wave_data/swan_HS.63.nc \
# --wavemwd /Volumes/ssd/ObservationalWind/wave_data/swan_DIR.63.nc \
# --wavemwp /Volumes/ssd/ObservationalWind/wave_data/swan_TMM10.63.nc \
# --wavepwp /Volumes/ssd/ObservationalWind/wave_data/swan_TPS.63.nc \
# --meshExists true --mesh /Volumes/ssd/ObservationalWind/wave_data/fort.14 \
# --waterExists true --water /Volumes/ssd/ObservationalWind/wave_data/fort.63.nc \
# --generateRunup true \
# --tempDir /Volumes/ssd/temp/ --backgroundChoice NAPATREE


# python generateGraphs.py --stations NAPATREE_NORMAL_STATIONS.json \
# --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_plus/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_plus/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_plus/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_plus/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_plus/swan_TPS.63.nc \
# --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_plus/fort.63.nc \
# --meshExists true --mesh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_plus/fort.14 \
# --generateRunup true \
# --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice NAPATREE

# 
# python generateGraphs.py --stations NAPATREE_NORMAL_STATIONS.json \
# --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_master_build/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_master_build/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_master_build/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_master_build/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_master_build/swan_TPS.63.nc \
# --waterExists true --water /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_master_build/fort.63.nc \
# --stillwaterExists true --stillwater /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_padcirc_master_build/fort.63.nc \
# --meshExists true --mesh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_master_build/fort.14 \
# --generateRunup true \
# --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice BLOCK_ISLAND_SOUND_OUTLINE


# python generateGraphs.py --stations OBS_STATIONS.json \
# --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_master_build/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_master_build/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_master_build/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_master_build/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track_master_build/swan_TPS.63.nc \
# --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice BLOCK_ISLAND_SOUND_OUTLINE


# Water dec 23
# python generateGraphs.py --stations RUNUP_NORMAL_STATIONS.json --wavesExists true --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_HS.63.nc --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_DIR.63.nc --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_TMM10.63.nc --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_TPS.63.nc --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/rads.64.nc --backgroundChoice RHODE_ISLAND_CHAMP --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/
# Waves for dec23
# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --wavesExists true --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_HS.63.nc --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_DIR.63.nc --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_TMM10.63.nc --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/swan_TPS.63.nc --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Dec172023RunupRun/forecast_RI_track/rads.64.nc --backgroundChoice RHODE_ISLAND_CHAMP --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/

# python generateGraphs.py --stations OBS_STATIONS.json --meshExists true --mesh ../trackfiles/v18.fort.14 --tempDir temp/ --backgroundChoice CAPE_COD

# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --gfsExists true --wind /Volumes/ssd/ObservationalWind/feb25.nc --tempDir /Volumes/ssd/temp/ --backgroundChoice EAST_COAST
# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --waterExists true --water /Volumes/ssd/ObservationalWind/wave_data/fort.63.nc --tempDir /Volumes/ssd/temp/

# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --waterExists true --water /Volumes/ssd/ObservationalWind/Dec172023WaveData/fort.63.nc --tempDir /Volumes/ssd/temp/


# python generateGraphs.py --stations OBS_STATIONS.json --gfsExists true --wind /project/pi_iginis_uri_edu/pranav_sai_uri_edu/scenario_files/1938392025.nc --backgroundChoice CAPE_COD_BAY_OUTLINE --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/
# python generateGraphs.py --stations OBS_STATIONS.json --gfsExists true --wind /project/pi_iginis_uri_edu/pranav_sai_uri_edu/scenario_files/1938Modified3725.nc --backgroundChoice CAPE_COD_BAY_OUTLINE --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/
# python generateGraphs.py --stations OBS_STATIONS.json --gfsExists true --wind /work/pi_iginis_uri_edu/pranav_sai_uri_edu/scenario_files/v18Runs/FinalWaterFiles/WindFiles/1938Night.nc --backgroundChoice EAST_COAST_OUTLINE --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/
# python generateGraphs.py --stations OBS_STATIONS.json --waterExists true --water /work/pi_iginis_uri_edu/pranav_sai_uri_edu/scenario_files/v18Runs/FinalWaterFiles/1938_night.fort.63.nc --backgroundChoice RHODE_ISLAND_CHAMP --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/
# python generateGraphs.py --stations OBS_STATIONS.json --rainExists true --rain RICHAMP_rain.nc --backgroundChoice EAST_COAST_OUTLINE --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/


# python generateGraphs.py --stations OBS_STATIONS.json --obsExists true --gfsExists true --wind /work/pi_iginis_uri_edu/pranav_sai_uri_edu/scenario_files/v18Runs/FinalWaterFiles/WindFiles/Jan24Wind.nc --backgroundChoice EAST_COAST_OUTLINE --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/
# python generateGraphs.py --stations OBS_STATIONS.json --rainExists true --obsExists true --rain /work/pi_iginis_uri_edu/pranav_sai_uri_edu/scenario_files/v18Runs/FinalWaterFiles/RainFiles/Jan24Rain.nc --backgroundChoice EAST_COAST_OUTLINE --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/
# 
# python generateGraphs.py --stations OBS_STATIONS.json --waterExists true --obsExists true --water /work/pi_iginis_uri_edu/pranav_sai_uri_edu/scenario_files/v18Runs/FinalWaterFiles/Jan24.fort.63.nc --backgroundChoice RHODE_ISLAND_CHAMP --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/


# python generateGraphs.py --stations OBS_STATIONS.json \
# --obsExists true \
# --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track/swan_TPS.63.nc \
# --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice BLOCK_ISLAND_SOUND_OUTLINE


# python generateGraphs.py --stations OBS_STATIONS.json --waterExists true --water /work/pi_iginis_uri_edu/pranav_sai_uri_edu/scenario_files/v18Runs/FinalWaterFiles/Jan24_1ft.fort.63.nc --backgroundChoice RHODE_ISLAND_CHAMP --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/
# 
# python generateGraphs.py --stations OBS_STATIONS.json \
# --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track_1ft/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track_1ft/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track_1ft/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track_1ft/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track_1ft/swan_TPS.63.nc \
# --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice BLOCK_ISLAND_SOUND_OUTLINE

# python generateGraphs.py --stations OBS_STATIONS.json \
# --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/Jan92024RunupRun/forecast_RI_track/swan_TPS.63.nc \
# --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice BLOCK_ISLAND_SOUND_OUTLINE


# /scratch3/workspace/pranav_sai_uri_edu-runup/1938NightRun/forecast_RI_track_1ft

# python generateGraphs.py --stations OBS_STATIONS.json \
# --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/1938NightRun/forecast_RI_track_1ft/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/1938NightRun/forecast_RI_track_1ft/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/1938NightRun/forecast_RI_track_1ft/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/1938NightRun/forecast_RI_track_1ft/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/1938NightRun/forecast_RI_track_1ft/swan_TPS.63.nc \
# --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice BLOCK_ISLAND_SOUND_OUTLINE


# python generateGraphs.py --stations OBS_STATIONS.json \
# --wavesExists true \
# --waverad /scratch3/workspace/pranav_sai_uri_edu-runup/1938NightRun/forecast_RI_track/rads.64.nc \
# --waveswh /scratch3/workspace/pranav_sai_uri_edu-runup/1938NightRun/forecast_RI_track/swan_HS.63.nc \
# --wavemwd /scratch3/workspace/pranav_sai_uri_edu-runup/1938NightRun/forecast_RI_track/swan_DIR.63.nc \
# --wavemwp /scratch3/workspace/pranav_sai_uri_edu-runup/1938NightRun/forecast_RI_track/swan_TMM10.63.nc \
# --wavepwp /scratch3/workspace/pranav_sai_uri_edu-runup/1938NightRun/forecast_RI_track/swan_TPS.63.nc \
# --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/ --backgroundChoice BLOCK_ISLAND_SOUND_OUTLINE

# python generateGraphs.py --stations OBS_STATIONS.json --waterExists true --water /work/pi_iginis_uri_edu/pranav_sai_uri_edu/scenario_files/v18Runs/FinalWaterFiles/1938.fort.63.nc --backgroundChoice CAPE_COD_BAY_OUTLINE --tempDir /scratch3/workspace/pranav_sai_uri_edu-runup/temp/


# python generateGraphs.py --stations MIDWEST_STATIONS.json --gfsExists true --wind ../WeatherVisualizer/wind_gfs.nc --backgroundChoice MIDWEST --tempDir temp/

# python generateGraphs.py --stations OBS_STATIONS.json --waterExists true --water /Volumes/ssd/ObservationalWind/1938_night_1ft.fort.63.nc --backgroundChoice RHODE_ISLAND_CHAMP --tempDir /Volumes/ssd/temp/
