from setuptools import setup, find_packages
import os

# The version of the wrapped library is the starting point for the version number of the python package.
# In bugfix releases of the python package, add a '-' suffix and an incrementing integer.
# For example, a packaging bugfix release version 1.4.4 of the js.jquery package would be version 1.4.4-1 .

version = '1.5.2'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (read('README.txt')
                    + '\n' +
                    read('js', 'underscore', 'test_underscore.js.txt')
                    + '\n' +
                    read('CHANGES.txt'))

setup(name='js.underscore',
      version=version,
      description="Fanstatic packaging of underscore.js",
      long_description=long_description,
      classifiers=[],
      keywords='',
      author='Andreas Kaiser',
      author_email='disko@binary-punks.com',
      url="https://github.com/disko/js.underscore",
      license='BSD',
      packages=find_packages(),namespace_packages=['js'],
      include_package_data=True,
      zip_safe=False,
      setup_requires=['hgtools'],
      install_requires=['fanstatic',
                        'setuptools',],
      entry_points={'fanstatic.libraries': ['underscore.js = js.underscore:library',],},)
