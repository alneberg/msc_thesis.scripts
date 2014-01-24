#!/usr/bin/env python
from concoctr.concoctr import ConcoctParams, ConcoctR
from logbook import TimedRotatingFileHandler, Logger
from argparse import ArgumentParser
import drmaa
import os
import yaml
from os.path import join
import pandas as p


def main(run_name, settings, exec_mode):
    # File path and test data path
    fp = os.path.dirname(__file__) 
    tdp = join(fp,"..", "tests", "test_data")

    composition = settings.get("composition_file", join(tdp,"composition.fa"))
    coverage = settings.get("coverage_file", join(tdp,"coverage"))
    result_path = settings.get("results_path_base", join(fp,"..","tmp_out_test"))
    kmer_lengths = settings.get("kmer_lengths", [4])
    pcas = settings.get("total_percentage_pca", [80])
    thresholds = settings.get("length_threshold", [1000])
    cv_types = settings.get("covariance_type", ["full"])
    clusters = settings.get("clusters", "2,100,2")
    max_n_processors = settings.get("max_n_processors", 1)
    email = settings.get("email", None)

    log_path = settings.get("log_path", 
                            join(os.path.expanduser("~"),"log","concoctr.log"))
    handler = TimedRotatingFileHandler(log_path)
    logger = Logger(run_name)
    handler.push_application()

    result_rows = []
    indx = []
    
    con_ps = []

    if exec_mode == 'drmaa':
        s = drmaa.Session()
        s.initialize()

    result_dir = os.path.join(result_path, run_name)
    os.mkdir(result_dir)
    slurm_dir = os.path.join(result_dir, 'slurm')
    os.mkdir(slurm_dir)
    sbatch_dir = os.path.join(result_dir, 'sbatch')
    os.mkdir(sbatch_dir)
    concoct_dir = os.path.join(result_dir, 'concoct_output')
    os.mkdir(concoct_dir)

    for k in kmer_lengths:
        for pca in pcas:
            for thr in thresholds:
                for cv in cv_types:
                    job_name = "_".join(map(str, [k, pca, thr, cv]))
                    con_p = ConcoctParams(composition,
                                          coverage,
                                          kmer_length = k,
                                          total_percentage_pca= pca,
                                          length_threshold = thr,
                                          covariance_type = cv,
                                          basename = os.path.join(concoct_dir, job_name) + "/",
                                          max_n_processors = max_n_processors,
                                          clusters = clusters)
                    con_ps.append(con_p)

                    cr = ConcoctR()
                    if (k > 9):
                        # Throw in some extra memory
                        n_cores = 4
                    else:
                        n_cores = 1
                    if exec_mode == 'drmaa':
                        jt = s.createJobTemplate()
                        jt.nativeSpecification = '-A b2010008 -p core -n {} -t 7-00:00:00'.format(n_cores)
                        jt.email = email
                        jt.workingDirectory = result_path
                        jobid = cr.run_concoct(con_p, drmaa_s=s, drmaa_jt=jt)
                    elif exec_mode == 'sbatch':
                        script_file = os.path.join(result_dir, 'sbatch', job_name)
                        sbatch_params = ['-A b2010008', 
                                         '-p core', 
                                         '-n {}'.format(n_cores), 
                                         '-t 7-00:00:00', 
                                         "-J {}".format(job_name),
                                         "-o {}".format(os.path.join(result_dir, 'slurm', 'slurm-%j.out'))]
                        cr.generate_sbatch_script(con_p, sbatch_params, script_file)
                        jobid = cr.run_concoct(con_p, sbatch_script = script_file)
                    if jobid:
                        result_rows.append(con_p.options)
                        indx.append(jobid)
                        logger.info("Submitted jobid {0}".format(jobid))

    results_df = p.DataFrame(result_rows, index=indx)
    results_df.to_csv(os.path.join(result_path, run_name + "_all_results.csv"))

    handler.pop_application()

if __name__=="__main__":
    parser = ArgumentParser()
    parser.add_argument('run_name', type=str,
                        help=("Used to name the output files and"
                        " the result directories"))
    parser.add_argument('--settings_file',
                        help=("Yaml file with settings."))
    parser.add_argument('--exec_mode', choices=['drmaa', 'sbatch'], default='sbatch',
                        help=("Execution mode, where sbatch submits explicit shell scripts"))
    settings = {}
    args = parser.parse_args()
    if args.settings_file:
        with open(args.settings_file) as settings_file:
            settings = yaml.load(settings_file)
    main(args.run_name, settings, args.exec_mode)
