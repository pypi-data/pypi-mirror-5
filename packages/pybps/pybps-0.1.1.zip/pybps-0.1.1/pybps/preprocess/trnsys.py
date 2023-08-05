"""
A set of functions required to pre-process TRNSYS simulation input files
"""

import os
import sys
import shutil
import re
from ConfigParser import SafeConfigParser

from pybps import util


def parse_deck_const(deck_abspath):
    """Parse constants in control cards and equations from TRNSYS deck file"""
    
    const_dict = {}
    
    f = open(deck_abspath, 'r')
              
    split_blocks_pat = re.compile(r'[*][-]+')
    equa_pat = re.compile(r'[*]\sEQUATIONS\s"(.+?)"')
    const_pat = re.compile(r'\b(\w+)\b\s=\s(\d+\.*\d*)\s')
                
    with f:
        data = f.read()
        blocks = split_blocks_pat.split(data)
        for block in blocks:
            if block[0] == 'V':
                match_par = const_pat.findall(block)
                if match_par:
                    group = "Control Cards"
                    const_dict[group] = {}
                    for (m,v) in match_par:       
                        const_dict[group][m] = v            
            else:
                match_eq = equa_pat.findall(block)
                if match_eq:
                    group = match_eq[0]
                    match_par = const_pat.findall(block)
                    if match_par:
                        const_dict[group] = {}
                        for (m,v) in match_par:
                            const_dict[group][m] = v

    return const_dict

    
def prepare_deck_template(deck_abspath, param_list):
    """Prepare a template TRNSYS deck file for parametric analysis"""
       
    templ_deck_abspath = os.path.splitext(deck_abspath)[0] + "_Template.dck"
    
    shutil.copyfile(deck_abspath, templ_deck_abspath)
    
    f = open(templ_deck_abspath, 'r+')
                  
    with f:
        data = f.read()

        for par in param_list:
            data = re.sub(r'(' + par + r')\s=\s(\d+\.*\d*)', r'\g<1> = %\g<1>%', data)
        
        f.seek(0)
        f.write(data)
        f.truncate()
    
    
def gen_type56(model_abspath, select='all'):
    """Generate Type56 matrices and idf files"""
	
	# Get information from config file
    conf = SafeConfigParser()
    conf_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),
        '..\config.ini')
    conf.read(conf_file)
    trnbuild_path = os.path.abspath(conf.get('TRNSYS', 'TRNBuild_Path'))
    trnsidf_path = os.path.abspath(conf.get('TRNSYS', 'trnsIDF_Path'))

    # Get b17 file path from deck file
    pattern = re.compile(r'ASSIGN "(.*b17)"')
    with open(model_abspath, 'rU') as m_f:
        temp = m_f.read()
        match = pattern.search(temp)
        # TRNBUILD is only called if Type56 is found in deck file.
        if match:
            b17_relpath = match.group(1)
            b17_abspath = os.path.join(os.path.dirname(model_abspath), b17_relpath)
            # Generate shading/insolation matrix
            if select == 'all' or select == 'matrices' or select == 'masks':
                cmd = [trnbuild_path, b17_abspath, '/N', '/masks']
                util.run_cmd(cmd)
            # Generate view factor matrix
            if select == 'all' or select == 'matrices' or select == 'vfm':					
                cmd = [trnbuild_path, b17_abspath, '/N', '/vfm']
                util.run_cmd(cmd)
            # Generate trnsys3D idf file, to view geometry in Sketchup
            if select == 'all' or select == 'idf':				
                cmd = [trnsidf_path, b17_abspath]
                util.run_cmd(cmd)

