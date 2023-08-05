"""
Core classes and functions of the pybps package
"""

import os
import sys
import re
import sqlite3
from copy import deepcopy
from ConfigParser import SafeConfigParser
from multiprocessing import Pool, cpu_count, freeze_support
from time import time, sleep
from random import uniform
from shutil import copy, copytree
import pandas as pd
from pandas.io import sql

from pybps import util
import pybps.preprocess.trnsys as trnsys_pre
import pybps.preprocess.daysim as daysim_pre
import pybps.postprocess.trnsys as trnsys_post
import pybps.postprocess.daysim as daysim_post



def run_job(job):
    """Prepare, Preprocess, Run and Close a BPSJob
    This function is called by the multiprocessing.pool.map method"""
	
    print("Running simulation job %d ..." % job.jobID)
    job.prepare()
    job.preprocess()
    job.run()
    job.close()
	
    return job.runsumdict
	
	
	
def sort_key_dfcolnames(x):
    """Sort key function for list of pandas DataFrame column names.
    Used to put 'JobID' column first in pandas DataFrame"""
	
    if x == 'JobID':
        return (0, x)
    elif x == 'ModelFile':
        return (1, x)
    elif x == 'SampleFile':
        return (2, x)
    else:
        return (3, x)
        
	
		
class BPSProject(object):
    """
    Comment
    """
	
    def __init__(self, path=None, validCheck=True):
        # Create a unique id to identify current serie of job runs
        self.seriesID = util.random_str(8)
        print("\nBatch Series ID: %s" % self.seriesID)
        # A flag to enable or disable validity checking
        self.valid_check = validCheck
        # Simulation tool to be used
        self.simtool = None 
        # Config info for detected simulation tool		
        self.config = {}
        # Variable that holds the name of the 'run_jobs' function to be used
        self.runjob_func = run_job
        # True if project is a simulation batch, False otherwise
        self._batch = False
        # Simulation run time
        self.simtime = 0
        # Relative path to model file to be used in current run
        self.model_relpath = None
        # List of jobs to be run		
        self.jobs = []
        # List of dicts containing run summaries for all jobs
        self.runsummary = []
        # Absolute path to base directory for jobs
        self.jobsdir_abspath = None
        # Absolute path to jobs results directory
        self.resultsdir_abspath = None
        # Name of results database
        self.db_name = 'SimResults.db'
        # Name of jobs csv file
        self.jobscsv_name = 'SimJobs.csv'
        # Name of results csv file
        self.resultscsv_name = 'SimResults.csv'
        # Name of run summary csv file
        self.runsumcsv_name = 'RunSummary.csv'
        # List of relative paths to template simulation files		
        self.temp_relpaths = []
        # List of parameters found in template files
        self.temp_params = []
        # Relative path to csv file containing list of jobs to be run		
        self.samp_relpath = None
        # List of parameters found in sample file
        self.samp_params = []	
        # Raw sample extracted from csv file. It's a list of dicts with
        # each dict holding all parameter for a particular job
        self.sample = []
        # Pandas DataFrame for jobs list
        self.jobs_df = None
        # Pandas DataFrame for simulation results
        self.results_df = None
        # Pandas DataFrame for run summary
        self.runsum_df = None
        if path is not None:
            # Absolute path to simulation project directory
            self.abspath = os.path.abspath(path)
            print("\nBPS project directory: " + self.abspath)
            # Launch method to detect sim tool and store related config info
            self.check()
        else:
            self.abspath = []
			
			
    def set_abspath(self, path):
        """Comment"""
		
        self.abspath = os.path.abspath(path)
        print("\nBPS project directory: " + self.abspath)
        self.check()
	
		
    def get_sample(self, src='samplefile', seriesID=None):
        """Comment"""
		
        # Empty any previously created jobs list
        self.sample = []
		
        if src == 'samplefile':
		    # Get information needed to find jobs file in folder
            samp_sstr = self.config['samplefile_searchstring']
            samp_abspathlist = util.get_file_paths([samp_sstr], self.abspath)
            
            # Check if there is no more than 1 sample file in directory
            if len(samp_abspathlist) > 0:
                samp_relpathlist = [os.path.relpath(fname, self.abspath) 
                                       for fname in samp_abspathlist]
                if len(samp_relpathlist) > 1:
                    print('\nVarious sample files found in directory' +
                        '\nPlease select sample to be used in current run:')
                    for i, path in enumerate(samp_relpathlist):
                        print("(%d) %s" % (i+1, os.path.splitext(path)[0]))
                    select = int(raw_input("Sample ID number: "))
                    self.samp_relpath = samp_relpathlist[select - 1]
                    print("You selected %s" % self.samp_relpath)
                else:					
                    self.samp_relpath = samp_relpathlist[0]
                # Build list of dicts with parameter values for all job runs
                samp_abspath = os.path.join(self.abspath, self.samp_relpath)
                self.sample = util.csv2dict(samp_abspath)
                # Add model and sample file names as parameters
                for s in self.sample:
                    s['ModelFile'] = self.model_relpath
                    s['SampleFile'] = self.samp_relpath					
            else:
                sys.stderr.write("Could not find any sample file in " +
                    "project directory\nPlease put a \'" + samp_sstr +
                    "\' file in directory and re-run 'get_sample' method\n")                
        elif src == 'database' and not seriesID:
            print("\nPlease provide a seriesID to retrieve parameter list" +
                " from database")
	
	
    def get_parameterlist(self, src, tmp_relpathlist=[]):
        """Returns parameter list from sample or template files.
        
        Parameter list is returned sorted after eliminating duplicates.
        """

        if src == 'sample':
            self.samp_params = self.sample[0].keys()
            self.samp_params.sort()
        elif src == 'tempfile':
            pattern = re.compile(r'%(.*?)%')
            self.temp_params = []
            for temp_relpath in tmp_relpathlist:
                # Open jobs file
                temp_abspath = os.path.join(self.abspath, temp_relpath)
                with open(temp_abspath, 'rU') as tmp_f:
                    # Read the entire file and store it in a temporary variable
                    temp = tmp_f.read()
                    # Build a list of all paramaters found in file
                    # Parameters are identified as strings surrounded by '%'
                    self.temp_params.extend(pattern.findall(temp))
            # Remove duplicates, then sort list
            self.temp_params = list(set(self.temp_params))
            self.temp_params.sort()     
        else:
            print("Unrecognized argument.")
	
	
    def add_jobs(self):
        """Comment"""
		
        # Create main directory for simulation jobs if it doesn't exists
        self.jobsdir_abspath = self.abspath + '_BATCH'
        util.tmp_dir('create', self.jobsdir_abspath)
        # Create directory to store jobs results in main project directory
        # if it doesn't already exists
        self.resultsdir_abspath = os.path.join(self.jobsdir_abspath, 'Results')
        util.tmp_dir('create', self.resultsdir_abspath)
        # Remove any previously created job
        self.jobs = []
        # Then, add jobs
        if self._batch:
            njob = len(self.sample)
            # Get list of all parameters found in template files
            self.get_parameterlist('tempfile', self.temp_relpaths)
            self.get_parameterlist('sample')
            if self.valid_check == True:
                # Check if template files and jobs file contain the same list
                # of parameters. Raise an error if not
                if set(self.temp_params).issubset(self.samp_params):
                    for jobID in range(1, njob+1):
                        self.jobs.append(BPSJob(self, jobID))
                    print("\n%d jobs added to BPSProject instance" % njob)
                else:
                    print("\nMismatch between template and sample file" + 
                        " parameters!\nNo jobs added to BPSproject instance")
            else:
                for jobID in range(1, njob+1):
                    self.jobs.append(BPSJob(self, jobID))
                print("\n%d jobs added to BPSProject instance" % njob)              			
        else:
            print("\nBPS project not a batch run. Jobs can't be added")
			
			
    def check(self):
        """Comment"""
	
	    # Get information from config file
        conf = SafeConfigParser()
        conf_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),
            'config.ini')
        conf.read(conf_file)
        sections = conf.sections()
		
        # Detect simulation tool used for current simulation job and check if
        # basic simulation input files are there
        found = 0 # Variable to store whether a simulation project was found

        for section in sections:
		    # Get information needed to find model files in folder
            model_ext = conf.get(section, 'ModelFile_Extensions')
            model_ext = model_ext.split(',')
            tmp_sstr = conf.get(section, 'TemplateFile_SearchString')
	        # Check if we can find a model file for the selected simtool
            model_abspathlist = util.get_file_paths(model_ext, self.abspath)
            if model_abspathlist:
                model_relpathlist = [os.path.relpath(fname, self.abspath)
                                        for fname in model_abspathlist]
                # If another simtool was already detected, raise an error            
                if found > 0:
                    sys.stderr.write("\nInput files for different BPS " +
                        "tools found\nNo more than 1 kind of simulation " +
                        "file allowed in a same folder")
                    sys.exit(1)
                # If not, store the name of detected simulation tool
                self.simtool = section
                print(self.simtool + " simulation project found in directory")
                # Strip search string from model file names
                for i, relpath in enumerate(model_relpathlist):
                    match = re.search(r'(.*)' + tmp_sstr + r'(.*)',
                                os.path.basename(relpath))
                    if match:
                        relpath = os.path.join(os.path.dirname(
                            relpath), match.group(1) + match.group(2))
                        model_relpathlist[i] = relpath
                # If more than 1 model file found, ask user to select 1 model
                if len(model_relpathlist) > 1:
                    if (len(model_relpathlist) == 2 and 
                           model_relpathlist[0] == model_relpathlist[1]):
                        self.model_relpath = model_relpathlist[0]
                    else:
                        print('\nVarious model files found in directory' +
                            '\nPlease select model to be used in current run:')
                        print("(%d) %s" % (0, 'all models'))
                        for i, path in enumerate(model_relpathlist):
                            print("(%d) %s" % (i+1, os.path.splitext(
                                os.path.basename(path))[0]))
                        select = int(raw_input("Model ID number: "))
                        if select == 0:
                            self.model_relpath = model_relpathlist
                            print('You selected all models')
                        else:
                            self.model_relpath = model_relpathlist[select - 1]
                            print("You selected %s" % self.model_relpath)
                else:
                    self.model_relpath = model_relpathlist[0]
                found += 1

        if found == 0:
            sys.stderr.write("\nNo BPS project found in the specified " +
                "folder\nPlease check the folder path is correct and " +
                "simulation files are in given folder")
            sys.exit(1)
				
        # Once simulation tool has been detected, store config info in 'config'
        items = conf.items(self.simtool)
        for (name, value) in items:
            self.config[name] = value
				
		# Once we have found a simulation project and stored config info,
        # let's see if we can find a template file for this project	
        tmpfile_sstr = self.config['templatefile_searchstring']
        temp_abspathlist = util.get_file_paths([tmpfile_sstr], self.abspath)
        
        if temp_abspathlist:
            self._batch = True
            self.temp_relpaths = [os.path.relpath(f_name, self.abspath) 
                                     for f_name in temp_abspathlist]            
	        # If template(s) found, check directory for sample file 
            self.get_sample()
        # Identify project as batch run if user selected to run all models
        elif len(self.model_relpath) > 1:
            print("All model files will be run in batch mode when 'run' " +
                "method is called.")
            self._batch = True
            # Add model and sample files relative paths as parameters
            for i,(m,s) in enumerate(zip(self.model_relpath,self.samp_relpath)):
                self.sample.append({})
                self.sample[i]['ModelFile'] = m
                self.sample[i]['SampleFile'] = s				
		# If no template file was found, give message to user
        else:
            print("No template found. BPS project identified as single run")
			
        
    def run(self, ncore='max', stopwatch=False, run_mode='silent', debug=False):
        """Comment"""
        
        #Create executable path for selected simulation tool
        if self.simtool == 'TRNSYS':
            executable_abspath = self.config['trnexe_path']
            silent_flag = '/h'
            nostop_flag = '/n'
        elif self.simtool == 'DAYSIM':
            executable_abspath = self.config['exe_path']
            silent_flag = ''
            nostop_flag = ''            
		
        # If simulation project is identified as single run, directly
        # call simulation tool to run simulation
        if self._batch == False:
            # Build absolute path to model file
            model_abspath = os.path.join(self.abspath, self.model_relpath)		
            # Run the simulation, by default in silent mode
            if run_mode == 'silent': flag = silent_flag
            elif run_mode == 'nostop': flag = nostop_flag
            elif run_mode == 'normal': flag = None
            cmd = [executable_abspath, model_abspath, flag]
            # Measure simulation run time
            start_time = time()
            # Launch command
            if debug == False:
                util.run_cmd(cmd)
            else:
                util.run_cmd(cmd, debug=True)
            # Save simulation time
            self.simtime = round(time() - start_time, 3)
        # If simulation project corresponds to a batch run, run jobs
        # in parallel
        else:
            # Check first if there are some jobs defined
            if self.jobs:
                print('\nStarting batch run ...')
                # Start timer if stopwatch requested by user
                if stopwatch == True:
                    start_time = time()			
                # Create multiprocessing pool for parallel subprocess run
                if ncore == 'max':
                    pool = Pool(None)
                    print(str(cpu_count()) + 
                        ' core(s) used in current run (max local cores)\n')
                else:
                    pool = Pool(ncore)
                    print(str(ncore) + ' core(s) used in current run\n')
                # This method automatically assigns processes to available
                # cores and the entire operation stops when all values from
                # jobs from the jobs list have been evaluated.
                # A callback function is used to retrieve run summary from job
                # and store it in runsummary list
                r = pool.map_async(self.runjob_func, self.jobs, chunksize=1,
                        callback=self.runsummary.extend)
                r.wait()
                pool.close()
                pool.join()
                # Stop timer if stopwatch requested by user
                if stopwatch == True:
                    print('\nSimulation batch runtime: ' + 
                        str(time()-start_time) + ' seconds')	        
		    # Print an error message if no jobs were found
            else:
                print("\nNo simulation jobs found" +
                "\n\nYou should first add simulation jobs to your BPSProject" +
                "with the 'add_job' or " +
                "\n'add_jobs' methods prior to calling the 'run' method")
		

    def jobs2df(self):
        """Create pandas DataFrame from sample"""

        # Build a 'pandas' DataFrame with all jobs parameters
        jobdict_list = []
        for job in self.jobs:
            jobdict = deepcopy(job.jobdict)
            jobdict['JobID'] = job.seriesID + '_' + '%0*d' % (5,job.jobID)
            jobdict_list.append(jobdict)
        colnames = jobdict_list[0].keys()
        colnames.sort(key = sort_key_dfcolnames)
        self.jobs_df = pd.DataFrame(jobdict_list, columns=colnames)

		
    def runsum2df(self):
        """Create pandas DataFrame from run summary"""
		
        # Build a 'pandas' DataFrame with run summaries for all jobs
        colnames = ['JobID','Message','Warnings','Errors','SimulTime(sec)']
        self.runsum_df = pd.DataFrame(self.runsummary, columns=colnames)        
	
											  
    def results2df(self):
        """Create pandas DataFrame from simulation results"""

        # Get extensions of results files
        results_ext = self.config['resultfile_extensions']
        results_ext = results_ext.split(',')	
        # Get list of paths to results files
        results_abspathlist = util.get_file_paths(results_ext, 
                                  self.resultsdir_abspath)
        # Go through all results files from all simulated jobs
        df_exists = False
        for results_abspath in results_abspathlist:
            # Get Series/Job IDs 
            match = re.search(r'([A-Z0-9]{8})_[0-9]{5}', results_abspath)
            if match:
                # Only parse results within sub-folders pertaining to
                # current batch run identified by seriesID
                if match.group(1) == self.seriesID:
                    # Build a 'pandas' dataframe with results from all jobs
                    if self.simtool == 'TRNSYS':
                        dict_list = trnsys_post.parse_type46(
                                               results_abspath)
                    elif self.simtool == 'DAYSIM':
                        if (os.path.splitext(os.path.basename(
                            results_abspath))[1] == '.htm'):
                            dict_list = daysim_post.parse_el_lighting(
                                            results_abspath)
                    if dict_list:
                        for dict in dict_list:
                            dict['JobID'] = match.group()
                        colnames = dict_list[0].keys()
                        colnames.sort(key = sort_key_dfcolnames)
                        if not df_exists:
                            self.results_df = pd.DataFrame(dict_list, 
                                              columns=colnames)
                            df_exists = True
                        else:
                            df = pd.DataFrame(dict_list, columns=colnames)
                            self.results_df = self.results_df.append(df, 
                                                  ignore_index=True)
                    else:
                        print("No results dataframe created")                    
		 
	
    def save2db(self, items='all'):
        """Save results to database"""
		
        db_abspath = os.path.join(self.resultsdir_abspath, self.db_name)
        cnx = sqlite3.connect(db_abspath)
		
        if items == 'all' or items == 'jobs':
            sql.write_frame(self.jobs_df, name='Jobs', con=cnx, 
                if_exists='append')
        if items == 'all' or items == 'results':		
            sql.write_frame(self.results_df, name='Results', con=cnx, 
                if_exists='append')
        if items == 'all' or items == 'runsummary':		
            sql.write_frame(self.runsum_df, name='RunSummary', con=cnx, 
                if_exists='append')

        cnx.close()


    def save2csv(self, items='all'):
        """Save results to csv file"""
		
        jobscsv_abspath = os.path.join(self.resultsdir_abspath, 
                              self.jobscsv_name)
        resultscsv_abspath = os.path.join(self.resultsdir_abspath, 
                                 self.resultscsv_name)
        runsumcsv_abspath = os.path.join(self.resultsdir_abspath, 
                                self.runsumcsv_name)
		
        if items == 'all' or items == 'jobs':
            self.jobs_df.to_csv(jobscsv_abspath)
        if items == 'all' or items == 'results':	
            self.results_df.to_csv(resultscsv_abspath)
        if items == 'all' or items == 'runsummary':	
            self.runsum_df.to_csv(runsumcsv_abspath)

		
    def getfromdb_jobs(self, seriesID=None, db_name="SimResults.db"):
        """Comments"""
		
        self.seriesID = seriesID
        self.db_abspath = os.path.join(self.resultsdir_abspath, db_name)
        cnx = sqlite3.connect(self.db_abspath)
        if self.seriesID:
            sql_query = (r"SELECT * FROM Parameters WHERE _JOB_ID LIKE '%s%%'" 
                            % seriesID)
        else:
            sql_query = r"SELECT * FROM Parameters"
        parameters_df = sql.read_frame(sql_query, cnx)
        cnx.close()
        return parameters_df

		
    def getfromdb_results(self, seriesID=None, month=None, db_name="SimResults.db"):
        """Comments"""
		
        self.db_abspath = os.path.join(self.resultsdir_abspath, db_name)
        cnx = sqlite3.connect(self.db_abspath)
        if seriesID and month:
            sql_query = (r"SELECT * FROM Results WHERE (_JOB_ID LIKE '%s%%')" +
                            " AND (Month LIKE '%s')" % (seriesID, month))
        elif seriesID:
            sql_query = (r"SELECT * FROM Results WHERE _JOB_ID LIKE '%s%%'" 
                            % seriesID)
        else:
            sql_query = r"SELECT * FROM Results"
        results_df = sql.read_frame(sql_query, cnx)
        cnx.close()
        return results_df
	
		

class BPSJob(BPSProject):
    """Comment"""
	
    def __init__(self, bpsproject, jobID):
        #BPSProject.__init__(self, path=None, batch=True)
        # Define variables specific to BPSJob class instances
        self.jobID = jobID # ID of current job run	
        self.runsumdict = {} # Run summary dict
        self.simtime = 0 # Simulation run time
        # Define basic instance variables from main BPSProject class instance
        self.seriesID = bpsproject.seriesID
        self.simtool = bpsproject.simtool
        self.config = bpsproject.config
        self.jobdict = bpsproject.sample[jobID-1]
        self.base_abspath = bpsproject.abspath
        self.abspath = os.path.join(bpsproject.jobsdir_abspath, self.seriesID +
                          '_' + '%0*d' % (5, self.jobID))
        self.resultsdir_abspath = bpsproject.resultsdir_abspath
        self.model_relpath = self.jobdict['ModelFile']
        # The following instance variables are used only if project
        # has template and sample files
        self.temp_params = bpsproject.temp_params
        self.samp_params = bpsproject.samp_params	
        # IMPORTANT: instance of BPSJob class are by default identified
        # as single runs (self.batch = False).
        # The 'batch' instance variable MUST NOT BE CHANGED to 'True'!!!
        self._batch = False

		
    def prepare(self):
        """Comment"""
		
		# Check whether a single model file has been selected
        if isinstance(self.model_relpath, list):
            print("Multiple model files selected for job run!" +
                " Please select a single model file.")
        else:
	        # Create temp dir for current simulation job and copy files to it
            copytree(self.base_abspath, self.abspath)
            
    
    def preprocess(self):
        """Comment"""
            
		# Following code only runs when project uses template/sample files
        if self.jobdict:
            # Get template file search string and look for them
            tmp_sstr = self.config['templatefile_searchstring']	
            temp_abspathlist = util.get_file_paths([tmp_sstr], self.abspath)
	        # Once we have a list of paths to template files, loop through 
            for temp_abspath in temp_abspathlist:
                # Build name for simulation file 
                #(same name as tmp, without search string)
                match = re.search(r'(.*)' + tmp_sstr + r'(.*)', 
                            os.path.basename(temp_abspath))
                if match:
                    siminput_abspath = os.path.join(
                                           os.path.dirname(temp_abspath), 
                                           match.group(1) + match.group(2))
                # Replace parameters with sample values in template file 
                with open(temp_abspath, 'rU') as tmp_f:
                    # Read the entire file and store it in a temp variable
                    temp = tmp_f.read()
                    # Find parameters to be replaced in template files and
                    # replace them
                    for p in self.temp_params:
		                # If search string is found, replace with 
                        # corresponding parameter value			
                        temp = temp.replace('%' + p + '%', 
                                   str(self.jobdict[p]))
                    # Replace special &PROJECT_DIR& var with cur dir path 
                    temp = temp.replace('&PROJ_DIR&', str(self.abspath))
                    # Proper way to manage existing model files
                    if os.path.exists(siminput_abspath):
                        try:
                            os.remove(siminput_abspath)
                        except:
                            print("Exception: ", str(sys.exc_info()))
                    # Open output file and write replaced content to it
                    with open(siminput_abspath, 'w') as sim_f:
                        sim_f.write(temp)
                # Remove template file, which is not needed anymore
                try:
                    os.remove(temp_abspath)
                except:
                    print("Exception: ", str(sys.exc_info()))            
			
            # If simtool is TRNSYS, generate TRNBUILD shading/insolation, 
            # view factor matrices and IDF file corresponding to .b17 file
            if self.simtool == 'TRNSYS':
                wait_t = uniform(0,3)
                #print("Waiting %.2f seconds before calling TRNBUILD" % wait_t)
                sleep(wait_t)
                model_abspath = os.path.join(self.abspath, self.model_relpath)
                trnsys_pre.gen_type56(model_abspath)
            # If simtool is DAYSIM, rotate scene and generate material and
            # geometry radiance files required by Daysim
            if self.simtool == 'DAYSIM':
                model_abspath = os.path.join(self.abspath, self.model_relpath)
                daysim_pre.rotate_scene(model_abspath)
                daysim_pre.radfiles2daysim(model_abspath)
			

    def close(self):
        """Close job by copying results and log file to main results
        directory and removing temporary job directory"""
	
        # Parse info about simulation run from TRNSYS lst and log files
        if self.simtool == 'TRNSYS':
            # Get TRNSYS error/warning count from log file
            log_fname = os.path.splitext(self.model_relpath)[0]+'.log'
            log_abspath = os.path.join(self.abspath, log_fname)
            self.runsumdict = trnsys_post.parse_log(log_abspath)
	
        # Save jobID and simulation time in run summary dict
        self.runsumdict['JobID'] = self.seriesID + '_' + '%0*d' % (5, self.jobID)
        self.runsumdict['SimulTime(sec)'] = self.simtime
	
        # Create a subfolder in main results folder to store simulation results
        simresdir_abspath = os.path.join(self.resultsdir_abspath, 
                             self.seriesID + '_' + '%0*d' % (5, self.jobID))
        util.tmp_dir('create', simresdir_abspath)
				
        # Get extensions of results files
        results_ext = self.config['resultfile_extensions']
        results_ext = results_ext.split(',')	
        # Get list of paths to job results files
        jobresfile_abspathlist = util.get_file_paths(results_ext, self.abspath)
	    # Copy job results files to simulation results folder
        for jobresfile_abspath in jobresfile_abspathlist:
            copy(jobresfile_abspath, simresdir_abspath)
	
        # Get extensions of log files
        log_ext = self.config['logfile_extensions']
        log_ext = log_ext.split(',')
        # Get list of paths to job log files
        joblogfile_abspathlist = util.get_file_paths(log_ext, self.abspath)
	    # Copy log files to simulation results folder
        for joblogfile_abspath in joblogfile_abspathlist:
            copy(joblogfile_abspath, simresdir_abspath)

        # Remove temporary simulation folder
        util.tmp_dir('remove', self.abspath)
	

