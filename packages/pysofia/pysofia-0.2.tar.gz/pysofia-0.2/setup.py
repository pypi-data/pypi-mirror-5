from distutils.core import setup, Extension
from Cython.Distutils import build_ext
import glob
import numpy as np

sources =['pysofia/_sofia_ml.pyx'] + glob.glob('pysofia/src/*.cc')

setup(name='pysofia',
    version='0.2',
    description='Python bindings for sofia-ml',
    author='Fabian Pedregosa',
    author_email='fabian@fseoane.net',
    url='',
    packages=['pysofia'],
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension('pysofia._sofia_ml',
        sources=sources,
        language='c++', include_dirs=[np.get_include()])],
)
