from __future__ import print_function
#Check for cython >= 0.17 due to the use of STL containers
try:
    import Cython
except ImportError:
    raise ImportError("Cython not found")
major,minor = Cython.__version__.split('.')[0:2]
#Convert major to integer
major = int(major)
iEnd = 0
while minor[iEnd].isdigit():
    iEnd+=1
    if iEnd == len(minor):
        break

minor = int(minor[0:iEnd])
if not(major > 0 or minor >= 17):
    raise ImportError('Cython version >= 0.17 required due to the use of STL wrappers.  Please update your version of cython')

try:
    import psutil
    for proc in psutil.get_process_list():
        cmdline = proc.cmdline
        if cmdline and ''.join(cmdline).find('pycompletionserver.py') > 0:
            proc.terminate()
            print('Python completion server killed')
            break
except ImportError:
    print('psutil was not found, it is used to kill the python completion server in Eclipse which keeps CoolProp from building sometimes.  psutils can be easy_install-ed')
        
from distutils.core import setup, Extension
import subprocess,shutil,os,sys,glob
from Cython.Build import cythonize
from Cython.Distutils import build_ext
from Cython.Distutils.extension import Extension as CyExtension
from distutils.sysconfig import get_python_inc
from distutils.ccompiler import new_compiler 
from distutils.dep_util import newer_group

#This will generate HTML to show where there are still pythonic bits hiding out
Cython.Compiler.Options.annotate = True

# Two options for the location of the C++ files.  Either in the normal ../../CoolProp folder
# or they are in the CoolPropSource folder in this folder

# For PYPI purposes
if 'sdist' in sys.argv:
    CProot = '.'
    shutil.copy2(os.path.join('..','..','version.txt'),'version.txt')
    shutil.copytree(os.path.join('..','..','CoolProp'),'CoolPropSource')
else:
    CProot = os.path.join('..','..')
    
if os.path.exists('CoolPropSource'):
    CPSourceDir = 'CoolPropSource'
    CProot = '.'
else:
    CPSourceDir = os.path.join(CProot,'CoolProp')
    
version = open(os.path.join(CProot,'version.txt'),'r').read().strip()

if __name__=='__main__':

    def svnrev_to_file():
        """
        If a svn repo, use subversion to update the file in revision
        """
        try:
            subprocess.call(['svn','update'], shell = True)
            p = subprocess.Popen(['svn','info'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
            
            for line in str(stdout).split('\n'):
                if line.startswith('Revision'):
                    rev = line.split(':')[1].strip()
                    svnstring = 'long svnrevision = '+rev+';'
                    #Check if it is different than the current version
                    f = open(os.path.join(CPSourceDir,'svnrevision.h'),'r')
                    current_svn = f.read()
                    f.close()
                    if not current_svn.strip() == svnstring.strip():                
                        f = open(os.path.join(CPSourceDir,'svnrevision.h'),'w')
                        f.write(svnstring)
                        f.close()
                    break
        except (subprocess.CalledProcessError,OSError):
            pass
        
    svnrev_to_file()

    def version_to_file():
        string_for_file = 'char version [] ="{v:s}";'.format(v = version)
        f = open(os.path.join(CPSourceDir,'version.h'),'r')
        current_version = f.read()
        f.close()
        if not current_version.strip() == string_for_file.strip():
            f = open(os.path.join(CPSourceDir,'version.h'),'w')
            f.write(string_for_file)
            f.close()
        
    version_to_file()
    
    #This will generate HTML to show where there are still pythonic bits hiding out
    Cython.Compiler.Options.annotate = True

    ## If the file is run directly without any parameters, build and install
    if len(sys.argv)==1:
        #sys.argv += ['build_ext','--inplace']
        #sys.argv += ['build','--compiler=mingw32','install']
        sys.argv += ['clean','install']
        #sys.argv += ['install']
        
    badfiles = [os.path.join('CoolProp','__init__.pyc'),
                os.path.join('CoolProp','__init__.py')]
    for file in badfiles:
        try:
            os.remove(file)
        except:
            pass

    #########################
    ## __init__.py builder ##
    #########################

    #Unpack the __init__.py file template and add some things to the __init__ file
    lines=open('__init__.py.template','r').readlines()

    f = open(os.path.join(CPSourceDir,'svnrevision.h'),'r')
    rev = f.read().strip().split('=')[1].strip(';').strip()
    f.close()
    svnstring = '__svnrevision__ ='+rev+'\n'
    
    for i in range(len(lines)-1,-1,-1):
        if lines[i].strip().startswith('#') or len(lines[i].strip())==0: 
            lines.pop(i)
    lines=['from __future__ import absolute_import\n']+['__version__=\''+version+'\'\n']+[svnstring]+lines
    fp=open(os.path.join('CoolProp','__init__.py'),'w')
    for line in lines:
        fp.write(line)
    fp.close()

    Sources = glob.glob(os.path.join(CPSourceDir,'*.cpp'))
    
    ### Include folders for build
    include_dirs = [os.path.join(CPSourceDir),get_python_inc(False)]

    def touch(fname):
        open(fname, 'a').close()
        os.utime(fname, None)

    #If library has been updated but the cython sources haven't been,
    #force cython to build by touching the cython sources
    cython_sources = [os.path.join('CoolProp','CoolProp.pyx')]

    common_args = dict(include_dirs = include_dirs,
                        language='c++',
                        cython_c_in_temp = True)
                        
    CoolProp_module = CyExtension('CoolProp.CoolProp',
                        [os.path.join('CoolProp','CoolProp.pyx')]+Sources,
                        **common_args)
        
    param_constants_module = CyExtension('CoolProp.param_constants',
                            [os.path.join('CoolProp','param_constants.pyx')],
                            **common_args)
                            
    phase_constants_module = CyExtension('CoolProp.phase_constants',
                            [os.path.join('CoolProp','phase_constants.pyx')],
                            **common_args)
                            
    #Collect all the header files in the main folder into an include folder
    try:
        os.mkdir(os.path.join('CoolProp','include'))
    except:
        pass
        
    for header in glob.glob(os.path.join(CPSourceDir,'*.h')):
        pth,fName = os.path.split(header)
        shutil.copy2(header,os.path.join('CoolProp','include',fName))
    shutil.copy2(os.path.join(CPSourceDir,'CoolPropBibTeXLibrary.bib'),os.path.join('CoolProp','CoolPropBibTeXLibrary.bib'))
    
    setup (name = 'CoolProp',
           version = version, #look above for the definition of version variable - don't modify it here
           author = "Ian Bell",
           author_email='ian.h.bell@gmail.com',
           url='http://coolprop.sourceforge.net',
           description = """Open-source thermodynamic and transport properties database""",
           packages = ['CoolProp','CoolProp.Plots','CoolProp.tests','CoolProp.GUI'],
           ext_modules = [CoolProp_module,param_constants_module,phase_constants_module],
           package_dir = {'CoolProp':'CoolProp',},
           package_data = {'CoolProp':['State.pxd','CoolProp.pxd','param_constants.pxd','include/*.h','CoolPropBibTeXLibrary.bib']},
           cmdclass={'build_ext': build_ext},
           
           classifiers = [
            "Programming Language :: Python",
            "Development Status :: 4 - Beta",
            "Environment :: Other Environment",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Topic :: Software Development :: Libraries :: Python Modules"
            ],
           )
    
    #Clean up the include folder
    shutil.rmtree(os.path.join('CoolProp','include'), ignore_errors = True)
    os.remove(os.path.join('CoolProp','CoolPropBibTeXLibrary.bib'))
    
    for file in glob.glob(os.path.join('CoolProp','__init__.*')):
        try:
            os.remove(file)
        except:
            pass
    
    if 'sdist' in sys.argv:
        shutil.rmtree('CoolPropSource')
        os.remove('version.txt')
    touch('setup.py')
    
#    try:
#        import nose
#        import CoolProp
#        CoolProp.test()
#    except ImportError:
#        print("Could not run tests, nose not installed")
        
        
    