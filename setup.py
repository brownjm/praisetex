from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE.md') as f:
    license = f.read()

classifiers=[
    'Development Status :: 4 - Beta'
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Religion',
    'Topic :: Religion',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3'
    ]

keywords = 'music chords slides praise religion'

package_data = {'': ['latex/slides.tex', 'latex/chords.tex', 'songs/*.txt']}
    

setup(name = 'praisetex',
      version = '0.1',
      description = 'Simple tool for creating chord sheets and slides for praise music',
      long_description = readme,
      author = 'Jeffrey M Brown',
      author_email = 'brown.jeffreym@gmail.com',
      url = 'https://github.com/brownjm/praisetex',
      license = license,
      packages = find_packages(exclude=('songs','latex')),
      include_package_data = True)
