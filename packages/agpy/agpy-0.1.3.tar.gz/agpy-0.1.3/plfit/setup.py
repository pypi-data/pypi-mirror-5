#from distutils.core import setup
#from distutils.extension import Extension
# removed following lines as per http://www.mail-archive.com/numpy-discussion@scipy.org/msg19932.html
# OLD from numpy.distutils.core import setup
# OLD from numpy.distutils.core import Extension
from distutils.core import setup,Extension
#from scipy_distutils.core import Extension as scipyExtension
#from scipy_distutils.core import setup as scipysetup
from numpy.distutils.core import Extension as numpyExtension
from numpy.distutils.core import setup as numpysetup
#from numpy.distutils.core import build_ext
from numpy.distutils.command import build_src
import Cython
import Cython.Compiler.Main
build_src.Pyrex = Cython
build_src.have_pyrex = True
from Cython.Distutils import build_ext
import Cython
import numpy
import os

print "To create cplfit.so (for importing), call command: "
print "python setup.py build_ext --inplace"
print "If this fails, make sure c_numpy.pxd is in the path somewhere (e.g. this directory)"

try:
    from numpy.distutils.misc_util import get_numpy_include_dirs
    numpy_include_dirs = get_numpy_include_dirs()
except AttributeError:
    numpy_include_dirs = numpy.get_include()


dirs = list(numpy_include_dirs)
dirs.extend(Cython.__path__)
dirs.append('.')

ext_cplfit = Extension(
		"cplfit", 
		["cplfit.pyx"], 
		include_dirs = dirs, 
		extra_compile_args=['-O3'])

#ext_fplfit = numpyExtension(name="fplfit",
#                    sources=["fplfit.f"])

if __name__=="__main__":

    # can't specify fcompiler if numpysetup is included 
    # therefore, run this command separately
    # gfortran = OK.  g77, g95 NOT ok
    fortran_compile_command = "f2py -c fplfit.f -m fplfit --fcompiler=gfortran"
    os.system(fortran_compile_command)
    # do this first so it gets copied (in principle...)

    setup(
        name = "plfit",
        version = "1.0",
        description = "Python implementation of Aaron Clauset's power-law distribution fitter",
        author = "Adam Ginsburg",
        author_email = "adam.ginsburg@colorado.edu",
        url="http://code.google.com/p/agpy/wiki/PowerLaw",
        download_url="http://code.google.com/p/agpy/source/browse/#svn/trunk/plfit",
        license = "MIT",
        platforms = ["Linux","MacOS X"],
        packages = ['plfit'],
        package_dir={'plfit':'.'},
        install_requires = ["numpy","cython"],
        ext_modules = [ ext_cplfit ],
        cmdclass = {'build_ext': build_ext}
    )

    #numpysetup(name = 'fplfit',
    #      ext_modules = [ext_fplfit]
    #      )



#print "I can't get numpy.distutils to compile the fortran.  To do it yourself, run some variant of:"
#print 'f2py -c fplfit.f -m fplfit'
# keep an eye on this: http://stackoverflow.com/questions/7932028/setup-py-for-packages-that-depend-on-both-cython-and-f2py

# try:
#     os.system('f2py -c fplfit.f -m fplfit')
# except:
#     print "Could not build fplfit"

