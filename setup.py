from setuptools import setup, find_packages

with open('README') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(name='praisetex',
      version='0.1',
      description='Simple tool for creating chord sheets and slides for praise music',
      long_description=readme,
      author='Jeffrey M Brown',
      author_email='brown.jeffreym@gmail.com',
      url='https://github.com/brownjm/praisetex',
      license=license,
      packages=find_packages(exclude=('songs','latex')))
