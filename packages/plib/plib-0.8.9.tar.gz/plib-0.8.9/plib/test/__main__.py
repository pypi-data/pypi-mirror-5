#!/usr/bin/env python
"""
Module MAIN
Sub-Package TEST of Package PLIB
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This is the overall test-running script for the PLIB test suite.
"""


if __name__ == '__main__':
    import os
    from plib.test.support import run_tests
    
    testdir = os.path.dirname(__file__)
    
    modules_with_doctests = [
        'plib.stdlib.classtools',
        'plib.stdlib.coll._typed_namedtuple',
        'plib.stdlib.decotools',
        'plib.stdlib.iters',
        'plib.stdlib.localize'
    ]
    
    # TODO: set module_relative and verbosity from command line options
    module_relative = False
    verbosity = 0
    
    run_tests(testdir, modules_with_doctests, module_relative, verbosity)
