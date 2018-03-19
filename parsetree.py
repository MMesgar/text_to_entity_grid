import logging
import argparse
import sys
import os
import gzip
import shlex
import subprocess
import multiprocessing
import traceback
import time
import itertools
from multiprocessing import Pool
from functools import partial


def make_grid(trees):

    prs_dir = './prs/'

    if type(trees) is dict:

        prs_path = os.path.join(prs_dir, trees['key'])
        
        trees = trees['trees']
    
    # Save parse trees 
    prs_file = open(prs_dir+'tmp.prs', 'w')
    
    if type(trees)==list:
    
        prs_file.write('\n'.join(trees))
    
    else:
    
        prs_file.write(trees)
    
    prs_file.close()

    # run TestGrid to get the entity grid
    params = {'TestGrid': './bin64/TestGrid','prs_trees':'tmp.prs'}
    
    cmd_line = ' %(TestGrid)s ../text_to_entity_grid/prs/%(prs_trees)s )' %(params)

    print cmd_line

    cmd_args = shlex.split(cmd_line)
    
    proc = subprocess.Popen(cmd_args, cwd='../browncoherence', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    stdout, stderr = proc.communicate()
    
    # if os.path.exists(prs_file_path):
    
    #     os.remove(prs_file_path)
    
    # before returning we replace trees of empty segments (marked as so) by empty trees
    return stdout

def parse(content, args):
    """
    Parse a number of segments.

    Arguments
    ---------
    mem: how much memory is available to the parser
    parser: path to jar
    models: path to jar
    grammar: path to gz
    threads: how many threads are available to the parser
    maxlength: segment maximum length (longer segments are skipped and the output is an empty parse tree: (())
    empty_seg: the token that marks an empty segment

    Returns
    -------
    list of parse trees (as strings)
    """
    params = {'mem': args['mem'],
            'parser': args['parser'],
            'models': args['models'],
            'grammar': args['grammar'],
            'threads': args['threads'],
            'maxlength': args['max_length'],
            }
    #print content
    cmd_line = 'java -mx%(mem)dm -cp "%(parser)s:%(models)s" edu.stanford.nlp.parser.lexparser.LexicalizedParser -nthreads %(threads)d -sentences newline -maxLength %(maxlength)d -outputFormat oneline %(grammar)s -' % (params)
     
    cmd_args = shlex.split(cmd_line)
    logging.debug('running: %s', cmd_line)
    proc = subprocess.Popen(cmd_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate(content)
    #print stdout
    #print stderr
    # before returning we replace trees of empty segments (marked as so) by empty trees
    output = [line.strip() for line in stdout.split('\n')]
    return [ptb if seg != '<EMPTY>' else '(())' for seg, ptb in itertools.izip(content.split('\n'), output)]

def wrap_parse(content, args):
    """
    Wraps a call to `parse` in a try/except block so that one can use a Pool
    and still get decent error messages.

    Arguments
    ---------
    content: segments are strings
    args: a namespace, see `parse`

    Returns
    -------
    parse trees and time to parse
    """
    if content.strip()=="" or content is None:
        return None
    try:
        trees = parse(content, args)
        if len(trees)!=0:
            return trees
        else:
            return None
    except:
        raise Exception(''.join(traceback.format_exception(*sys.exc_info())))

def wrap_grid(trees):
    """
    Wraps a call to `parse` in a try/except block so that one can use a Pool
    and still get decent error messages.

    Arguments
    ---------
    trees: parse trees

    Returns
    -------
    parse grids 
    """
    if trees is None:

        return None

    try:
        grid = make_grid(trees)

        return grid
    
    except:
    
        raise Exception(''.join(traceback.format_exception(*sys.exc_info())))

def get_parsed_trees_multi_documents(contents,args):
    # distributes the jobs
    pool = Pool(args['jobs'])
    logging.info('Distributing %d jobs to %d workers', len(contents), args['jobs'])
    trees_list = pool.map(partial(wrap_parse, args=args), contents)
    pool.terminate()
    return trees_list

def get_grids_multi_documents(testgrid_path,trees_list,jobs):
    # distributes the jobs
    pool = Pool(jobs)
    logging.info('Distributing %d jobs to %d workers', len(trees_list), jobs)
    gird_list = pool.map(partial(wrap_grid, testgrid_path=testgrid_path), trees_list)
    pool.close()
    pool.join()
    return gird_list

def get_grids_a_document(trees):
    grid = wrap_grid(trees)
    return grid

def get_parsed_trees_a_document(content,args):
    trees = wrap_parse(content, args)
    return trees

######################
## Test the class
#####################
if __name__=="__main__":

    args = {'mem': 150,
            'parser': "../stanford-parser/stanford-parser.jar",
            'models': "../stanford-parser/stanford-parser-3.5.2-models.jar",
            'grammar': "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz",
            'threads': 1,
            'max_length': 30,
            }
    
    import glob

    txt_files = glob.glob("./txt/*.txt")

    for txt_file in txt_files:

        # get the file name, for saving parse tree and egrid
        file_name = os.path.basename(txt_file).split('.')[0]

        # read the txt_file
        with open(txt_file,'rb') as tf:

            text = tf.read()

        print text

        # pars the txt file; get list of trees, one tree for each sentence in txt file
        trees = get_parsed_trees_a_document(text, args)

        print trees

        # save prs trees in prs folder
        with open('./prs/%s.prs'%file_name, 'wb') as prs_file:
        
            if type(trees)==list:
        
                prs_file.write('\n'.join(trees))
        
            else:
        
                prs_file.write(trees)
        

        # make entity grid of pars trees

        grid = get_grids_a_document(trees)

        print grid

        grid =  grid.split('\n')

        grid = [l.strip() for l in grid]

        grid = '\n'.join(grid)

        # save grid 
        with open('./grids/%s.grid'%file_name, 'wb') as grid_file:
        
            grid_file.write(grid)

