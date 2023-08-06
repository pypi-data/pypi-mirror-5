#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________

#
# Test the coopr.gdp transformations
#

import new
import os
import sys
import unittest
from os.path import abspath, dirname, normpath, join

currdir = dirname(abspath(__file__))
exdir = normpath(join(currdir,'..','..','..','examples'))

from coopr.pyomo import *
import pyutilib.services
import pyutilib.subprocess
import pyutilib.common
import pyutilib.th as unittest
import coopr.pyomo.scripting.pyomo as main
import StringIO
from pyutilib.misc import setup_redirect, reset_redirect
import re
try:
    import yaml
    yaml_available=True
except ImportError:
    yaml_available=False

import coopr.gdp.bigm
coopr.gdp.bigm.transform.deactivate()
import coopr.gdp.chull
coopr.gdp.chull.transform.deactivate()

cplex_available = False
try:
    cplex = coopr.plugins.solvers.CPLEX(keepfiles=True)
    cplex_available = (not cplex.executable() is None) and cplex.available(False)
except pyutilib.common.ApplicationError:
    cplex_available=False

glpk_available = False
try:
    glpk = coopr.plugins.solvers.GLPK(keepfiles=True)
    glpk_available = (not glpk.executable() is None) and glpk.available(False)
except pyutilib.common.ApplicationError:
    glpk_available=False


if os.path.exists(sys.exec_prefix+os.sep+'bin'+os.sep+'coverage'):
    executable=sys.exec_prefix+os.sep+'bin'+os.sep+'coverage -x '
else:
    executable=sys.executable

def copyfunc(func):
    return new.function(func.__code__, func.func_globals, func.func_name,
                        func.func_defaults, func.func_closure)
class Labeler(type):
    def __new__(meta, name, bases, attrs):
        for key in attrs.keys():
            if key.startswith('test_'):
                for base in bases:
                    original = getattr(base, key, None)
                    if original is not None:
                        copy = copyfunc(original)
                        copy.__doc__ = attrs[key].__doc__ + " (%s)" % copy.__name__
                        attrs[key] = copy
                        break
        for base in bases:
            for key in dir(base):
                if key.startswith('test_') and key not in attrs:
                    original = getattr(base, key)
                    copy = copyfunc(original)
                    copy.__doc__ = original.__doc__ + " (%s)" % name
                    attrs[key] = copy
        return type.__new__(meta, name, bases, attrs)

class CommonTests:
    #__metaclass__ = Labeler
    def pyomo(self, *args, **kwds):
        args=list(args)
        args.append('-c')
        if 'solver' in kwds:
            args.append('--solver='+kwds['solver'])
        pproc = None
        if 'preprocess' in kwds:
            pp = kwds['preprocess']
            if pp == 'bigm':
                pproc = coopr.gdp.bigm.transform
            elif pp == 'chull':
                pproc = coopr.gdp.chull.transform
        args.append('--symbolic-solver-labels')
        args.append('--save-results=result.yml')
        os.chdir(currdir)

        print('***')
        if pproc is not None:
            pproc.activate()
            print("Activating " + kwds['preprocess'])
        print(' '.join(args))
        output = main.run(args)
        if pproc is not None:
            pproc.deactivate()
        print('***')
        return output

    def check(self, problem, solver):
        pass

    def referenceFile(self, problem, solver):
        return join(currdir, problem+'.txt')

    def getObjective(self, fname):
        FILE = open(fname)
        data = yaml.load(FILE)
        FILE.close()
        solutions = data.get('Solution', [])
        ans = []
        for x in solutions:
            ans.append(x.get('Objective', {}))
        return ans

    def  updateDocStrings(self):
        for key in dir(self):
            if key.startswith('test'):
                getattr(self,key).__doc__ = " (%s)" % getattr(self,key).__name__

    def test_bigm_jobshop_small(self):
        # Run the small jobshop example using the BigM transformation
        self.pyomo( join(exdir,'jobshop.py'), join(exdir,'jobshop-small.dat'),
                    preprocess='bigm' )
        self.check( 'jobshop_small', 'bigm' )

    def test_bigm_jobshop_large(self):
        # Run the large jobshop example using the BigM transformation
        self.pyomo( join(exdir,'jobshop.py'), join(exdir,'jobshop.dat'),
                    preprocess='bigm')
        self.check( 'jobshop_large', 'bigm' )

    def test_chull_jobshop_small(self):
        # Run the small jobshop example using the CHull transformation
        self.pyomo( join(exdir,'jobshop.py'), join(exdir,'jobshop-small.dat'),
                    preprocess='chull')
        self.check( 'jobshop_small', 'chull' )

    def test_chull_jobshop_large(self):
        # Run the large jobshop example using the CHull transformation
        self.pyomo( join(exdir,'jobshop.py'), join(exdir,'jobshop.dat'),
                    preprocess='chull')
        self.check( 'jobshop_large', 'chull' )


class Reformulate(unittest.TestCase, CommonTests):
    def pyomo(self,  *args, **kwds):
        args = list(args)
        args.append('--save-model=result.lp')
        CommonTests.pyomo(self, *args, **kwds)

    def referenceFile(self, problem, solver):
        return join(currdir, problem+"_"+solver+'.lp')

    def check(self, problem, solver):
        self.assertFileEqualsBaseline( join(currdir,'result.lp'),
                                           self.referenceFile(problem,solver) )

class Solver(unittest.TestCase):
    def check(self, problem, solver):
        refObj = self.getObjective(self.referenceFile(problem,solver))
        ansObj = self.getObjective(join(currdir,'result.yml'))
        self.assertEqual(len(refObj), len(ansObj))
        for i in range(len(refObj)):
            self.assertEqual(len(refObj[i]), len(ansObj[i]))
            for key,val in refObj[i].iteritems():
                self.assertEqual(val, ansObj[i].get(key,None))

@unittest.skipIf(not yaml_available, "YAML is not available")
@unittest.skipIf(not glpk_available, "The 'glpk' executable is not available")
class Solve_GLPK(Solver, CommonTests):
    def pyomo(self,  *args, **kwds):
        kwds['solver'] = 'glpk'
        CommonTests.pyomo(self, *args, **kwds)

@unittest.skipIf(not yaml_available, "YAML is not available")
@unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
class Solve_CPLEX(Solver, CommonTests):
    def pyomo(self,  *args, **kwds):
        kwds['solver'] = 'cplex'
        CommonTests.pyomo(self, *args, **kwds)

if __name__ == "__main__":
    unittest.main()
