if echo $RICHAMP_INDIR | grep -q $ENSEMBLE_MEMBER >/dev/null 2>&1; then
    while squeue -u $USER | grep -q pst_init >/dev/null 2>&1
    do
        exit
    done
    rm -f *.start *.finish *.submit
    $POSTHOME/richamp_scale_and_subset_post_init.sh
    while ! test -e richamp_scale_and_subset_post_init.scr.start
    do
        sleep 5
    done
    job_string=$(cat richamp_scale_and_subset_post_init.scr.start)
    search=jobid
    left_job_string=${job_string%%$search*}
    jobid_lit_idx=${#left_job_string}
    jobid_idx=$(($jobid_lit_idx+10))
    jobid_endidx=$((${#job_string}-$jobid_idx-1))
    jobid=${job_string:$jobid_idx:$jobid_endidx}
    i=0
    while squeue -j $jobid | grep -q $jobid >/dev/null 2>&1
    do
        sleep 10
        i=i+1
        if [[ i > 5000 ]]; then
            exit
        fi
    done
fi