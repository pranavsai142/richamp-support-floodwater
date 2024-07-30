. $POST_ENV
indirIndex=0
numberSlashesFound=0
ecfNameLength=${#ECF_NAME}
ecfNameLength=$[ecfNameLength-1]
while (( $indirIndex < $ecfNameLength ))
do
    charEndIndex=${indirIndex+1}
    char=${ECF_NAME:indirIndex:charEndIndex}

    if [[ $char == "/" ]]; then
        numberSlashesFound=$[numberSlashesFound+1]
    fi
    if (( $numberSlashesFound == 5 )); then
        break
    fi
    indirIndex=$[indirIndex+1]
done
RICHAMP_INDIR=${ECF_NAME:0:indirIndex}
export RICHAMP_INDIR=$ECF_HOME$RICHAMP_INDIR/simulation
echo $RICHAMP_INDIR $POST_ENSEMBLE
if echo $RICHAMP_INDIR | grep -q $POST_ENSEMBLE >/dev/null 2>&1; then
    while squeue -u $USER | grep -q pst_init >/dev/null 2>&1
    do
        exit
    done
    rm -f $POSTHOME/*.start $POSTHOME/*.finish $POSTHOME/*.submit
    $POSTHOME/richamp_scale_and_subset_post_init.sh
    while ! test -e $POSTHOME/richamp_scale_and_subset_post_init.scr.start
    do
        sleep 5
    done
    job_string=$(cat $POSTHOME/richamp_scale_and_subset_post_init.scr.start)
    search=jobid
    left_job_string=${job_string%%$search*}
    jobid_lit_idx=${#left_job_string}
    jobid_idx=$(($jobid_lit_idx+10))
    jobid_endidx=$((${#job_string}-$jobid_idx-1))
    jobid=${job_string:$jobid_idx:$jobid_endidx}
    i=0
    MAX_RUN_TIME=5000
    while squeue -j $jobid | grep -q $jobid >/dev/null 2>&1
    do
        sleep 10
        i=$[i+1]
        echo EXECUTING POSTPROCESSING! Step: $i
        if [[ "$i" -gt "$MAX_RUN_TIME" ]]; then
            exit
        fi
    done
fi
