# http://ipython.org/ipython-doc/dev/interactive/qtconsole.html#display
from IPython.display import display


# set images to inline by default
c = c = get_ipython().config
c.IPKernelApp.pylab = 'inline'


ip = get_ipython()

def magic_publish(self, args):
    '''magic function to publish a python file in ipython

    This is some wicked hackery. You cannot directly call the publish module
    more than once because of namespace pollution. We cannot directly
    call publish.py with subprocess because it does not recognize it as an executable,
    even though you can call it from a shell.

    so we find the location of of the publish.py script and execute it
    in its own process, with a new namespace each time.

    this is not pretty, but it works for now.
    '''
    ## import os, subprocess
    ## import pycse
    ## path, init = os.path.split(pycse.__file__)
    ## cmd = ['python',
    ##        os.path.join(path,'publish.py')]
    ## cmd += [str(x) for x in args.split()]
    
    ## status = subprocess.check_call(cmd)
    ## if status != 0:
    ##     print 'Something went wrong in publishing.'
    
    # this is some new code inspired by some magic methods in Ipython. 
    # It seems to be a cleaner approach.
    from subprocess import Popen, PIPE
    code = '''from pycse.publish import publish
publish(u'{0}')'''.format(args)
    
    p = Popen('python', stdout=PIPE, stderr=PIPE, stdin=PIPE)
    out, err = p.communicate(code)
    print out, err
ip.define_magic('publish', magic_publish)

###########################################################################
from setuptools.command import easy_install

def magic_easy_install(self, package):
    easy_install.main( ["-U", package] )
    
ip.define_magic('easy_install', magic_easy_install)
    
import pip

def magic_pip(self, package):
    pip.main(['install','--upgrade', package]) 

ip.define_magic('pip', magic_pip)

def magic_upgrade(self, *args):
    print args
    for package in ['quantities',
                    'uncertainties',
                    'https://github.com/jkitchin/pycse/archive/master.zip',
                    'https://github.com/jkitchin/pyreport/archive/master.zip']:
        pip.main(['install','--upgrade', package]) 

ip.define_magic('pycse_upgrade', magic_upgrade)

##################################################################
## pycse_test magic

def magic_pycse_test(self, args):
    print 'Your installation of pycse looks ok.'

ip.define_magic('pycse_test', magic_pycse_test)
###########################################################################    
import numpy as np
import matplotlib.pyplot as plt

import quantities as u
import uncertainties as unc

print 'pycse-magic loaded.'
