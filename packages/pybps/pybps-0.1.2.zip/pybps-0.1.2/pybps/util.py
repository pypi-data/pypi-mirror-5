"""
Miscellaneous utility functions
"""

import os
import sys
import re
import csv
import string
import random
from subprocess import check_call, STDOUT
from tempfile import NamedTemporaryFile
from shutil import rmtree


def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

		
def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
	
	
def random_str(n):
    """Generates a random string of length n containing upper and lowercase
    letters and numbers"""
    return "".join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(n))     

	
def tmp_dir(action, tmp_dir):
	"""Create/remove temporary folder.

    Creates or removes a temporary folder at the indicated path.	

    Args:
        action: either 'create' or 'remove' temporary folder.
        tmp_dir: absolute path to temporary folder to be created/removed.

    Returns:
        nothing
		
    Raises:
        IOError: Exception:
    """

    # Create temporary folder
        if action == 'create':
            if not os.path.exists(tmp_dir):
                try:
                    os.mkdir(tmp_dir)
                except:
                    print("Exception: ", str(sys.exc_info()))

    # Remove temporary folder
        elif action == 'remove':
            if os.path.exists(tmp_dir):
                try:
                    rmtree(tmp_dir)
                except:
                    print("Exception: ", str(sys.exc_info()))

					
def get_file_paths(pattern_list, dir):
    """Get paths to files with name following specified pattern.

    Args:
        pattern_list: list of search patterns (each pattern as string).
        dir: absolute path to directory to search for files.

    Returns:
        list of paths to files containing specified pattern.
    """
	
    paths_list = []
	
    for root, dirs, files in os.walk(dir):
        for name in files:
            for pattern in pattern_list:
                match = re.search(r'.*' + pattern.strip() + r'.*', name)
                if match:
                    paths_list.append(os.path.join(root, name))

    return paths_list

	
def csv2dict(csv_abspath):
    """Reads specified csv file and returns a list of dicts.
    
    Each dict of the list contains parameter names (found in header) as keys
    and parameter values for a particular simulation as values.

    Args:
        file_abspath: absolute path to csv file.

    Returns:
        list of dicts.

    Raises:
        IOError: problem reading file
    """
	
    with open(csv_abspath, 'rb') as csv_f:
        csvdict = csv.DictReader(csv_f, delimiter=',')
        dict_list = list(csvdict)
    for dict in dict_list:
        for k in dict.keys():
            if is_float(dict[k]):
                if is_int(dict[k]):
                    dict[k] = int(dict[k])
                else:
                    dict[k] = float(dict[k])

    return dict_list


def dict2csv(dict, csv_abspath, fieldnames=None):
    """Writes given dict to csv file at indicated path.

    Args:
        dict: dict to be written in csv file
        csv_abspath: absolute path to output csv file.

    Raises:
        IOError: problem reading file
    """
	
    with open(csv_abspath,'wb') as f: #Remember `newline=""` in Python 3.x
        if fieldnames:
            w = csv.DictWriter(f, fieldnames)
        else:
            w = csv.DictWriter(f, dict.keys())
        w.writeheader()
        w.writerow(dict)

        
def dict_cleanconvert(dict):
    """Clean and convert dict keys and values.
    
    Strips whitespaces from dict keys and values, convert string identified as
    numbers to float and removes empty dict keys and values.

    Args:
        dict: dict to cleaned.
        
    Returns:
        Cleaned dict.
    """

    for key in dict.keys():
        # Convert all strings identified as numbers to float type
        if is_float(dict[key]):
            dict[key] = round(float(dict[key]), 3)
        # Remove unwanted whitespaces in all other values
        else:
            dict[key] = dict[key].strip()
        # Remove unwanted whitespace also in dict keys
        if any(key):
            if key != key.strip():
                dict[key.strip()] = dict[key]
                del dict[key]
        # Remove empty dict keys (and corresponding values)
        else:
            del dict[key]
		
    return dict
        
	
def run_cmd(cmd, debug=False):
    """Run a shell command.

    Args:
        cmd: shell command in list format.

    Raises:
        Problem executing: cmd
    """
	
    try:
        if debug == False:
            with NamedTemporaryFile() as f:
                check_call(cmd, stdout=f, stderr=STDOUT)
                #f.seek(0)
                #output = f.read()
        else:
            check_call(cmd)
    except OSError:
        sys.stderr.write('Problem executing: ' + ' '.join(cmd))