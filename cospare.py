#!/usr/bin/python
########################################################################
#   Created by Alexander Hanel <alexander.hanel<at>gmail<dot>com>
#   Version: 1.0 
#   Data: November Something 2012
#   This is file is part of cospare.py. A tool that is used for comparing
#   microsoft executable functions using normalization of x86 assembly and
#   cosine similiarity. This script relies on the output from idb2jsin.py
#   For usage information please execute the script. 
#########################################################################

from math import sqrt
import sys 
import json
from optparse import OptionParser
import os
import fnmatch
        
class coSim():
    def __init__(self, ajson, bjson):
        # shhhhh...
        # http://www.youtube.com/watch?v=U6dxYka2tRk
        self.a = self.loadJsons(ajson)
        self.b = self.loadJsons(bjson)
        self.matches = []
        self.count = 0
        self.findMatches()
        
    def loadJsons(self, _json):
        'load the json file into memory'
        with open(_json, 'rb') as f:
            try:
                loadedJson = json.load(f)
            except:
                print 'Error: JSON unload failed'
                return None 
        return loadedJson
        
    def scalar(self, collection):
        # Source https://gist.github.com/288282
        total = 0
        for coin, count in collection.items():
            total += count * count
        return sqrt(total)

    def similarity(self, A,B): # A and B are coin collections
        # Source https://gist.github.com/288282
        total = 0
        for kind in A: # kind of coin
            if kind in B:
                total += A[kind] * B[kind]
        return float(total) / (self.scalar(A) * self.scalar(B))
        
    def differenceSize(self,A,B):
        aLen = float(len(A))
        bLen = float(len(B))
        di = 0.0
        if aLen < bLen:
            di = bLen/aLen - 1
        else:
            di = aLen/bLen - 1  
        return di        
        
    def findMatches(self):
        'finds matching functions' 
        # the md5 is present if needed, must be deleted though  
        del self.a['MD5'] 
        del self.b['MD5']
        for k, v in self.a.iteritems():
            # functions with less than five instructions are prone to false positives 
            if len(v)  < 5: continue 
            for key, value in self.b.iteritems():
                if len(value) < 5: continue 
                diff = float(self. differenceSize(v, value))
                if diff > .15:
                    continue
                o = self.similarity(v, value)
                # similarity percent can be adjusted
                if o > 0.95:
                    if k != key:
                        formatted = "{0:.2%}".format(diff)
                        simm =  "{0:.2%}".format(o)
                        self.matches.append('%s matches %s %s with a size difference %s' % (k,key,simm,formatted)) 
                        self.count += 1

class dirdir():
    def __init__(self, dirArg):
        self.paths = []
        self.directory = dirArg
        self.findJsin()
        
    def findJsin(self):
        'get the path of all files' 
        for root, dirs, files in os.walk(self.directory):
            for basename in files:
                if fnmatch.fnmatch(basename, '*.jsin'):
                    self.paths.append(os.path.join(root,basename))

        
if __name__ == '__main__':
    # yeah this area is a little ugly. I wasted more time thinking about the flow
    # then I did coding the whole program. After a certain point I just gave up
    # and started coding. Comments are welcome. 
    parser = OptionParser()
    parser = OptionParser()
    # setup command line options 
    parser.add_option('-s', '--simple', action='store_true', dest='simple', help='Displays if the files match with yes or no output') 
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose', help='will display all the functions that match')
    parser.add_option('-m', '--multiple', action='store_true', dest='multiple', help='Attempts to recursively compare all jsin in a dir, -m single.json <path>')
    (options, args) = parser.parse_args()
    # check to make sure we have correct arguments
    if len(args) == 0:
        parser.print_help()
        sys.exit() 
    # check args for and varaibles for -m or --matches
    if options.multiple != None:
        if len(args) == 2:
            # Get a list of paths that contain *.jsin in the file name  
            d = dirdir(args[1])
            jsinPaths = d.paths
            for jsin in jsinPaths:
                sim = coSim(args[0], jsin)
                if float(sim.count)/float(len(sim.a)) > .65:
                    print "%s matches %s" % (args[0], jsin) 
            sys.exit()
        else:
            parser.print_help()
            sys.exit()
    # validate the each argument is an accessible object
    for file in args:
        f = 0
        try:
           with open(file) as f: pass
        except IOError as e:
            print "%s" % e
            parser.print_help()
            sys.exit()
    # validate args and compare two files             
    if len(args) == 2:
        sim = coSim(args[0], args[1])
    else:
        parser.print_help()
        sys.exit()
    # if verbose print all the matches 
    if options.verbose != None:
        for match in sim.matches:
            print match
    # validate args and compare that 65% of file1 is similar to file2
    if options.simple != None:
        if float(sim.count)/float(len(sim.a)) > .65:
            print 'yes'
            sys.exit() 
        else:
            print 'no'
            sys.exit() 
    else:
    # default print about the files 
        print "Total Function count in %s: %s" % (args[0],len(sim.a))                
        print "Total Function count in %s: %s" % (args[1], len(sim.b))
        print "Total Matches found %s" % sim.count
        print "Overall function matches %s" % "{0:.2%}".format(float(sim.count)/float(len(sim.a)))
            
