from distutils.core import setup, Extension
# from Cython.Distutils import build_ext

c_ext = Extension("brake", ["brake.cpp"])


module1 = Extension('brake',
                    include_dirs=[
                        "C:/Program Files (x86)/Ingenia/MCLIB/includes"],
                    libraries=['MCLIB', 'python36'],
                    library_dirs=["C:/Program Files (x86)/Ingenia/MCLIB/lib-win32-msvc-10.0"],
                    # runtime_library_dirs=["C:/Program Files (x86)/Ingenia/MCLIB/lib-win32-msvc-10.0"],

                    sources=['brake.cpp'])

setup(name='Nebula Brake Interface',
      version='0.1',
      description='C++ Wrapper to use Nebula Controller',
      author='Drevin B. Galentine',
      author_email='dgalenti@alumni.cmu.edu',
      # cmdclass={'build_ext': build_ext},

      ext_modules=[module1])
