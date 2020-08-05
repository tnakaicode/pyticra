
from setuptools import setup

setup(name='pyticra',
      version='0.0',
      description='Python package for Ticra Tools interfacing.',
      url='https://github.com/tnakaicode/pyticra',
      author='Taku Nakai',
      author_email='tnakaicode@gmail.com',
      license='GPL',
      packages=['pyticra'],
      package_dir={'pyticra': 'pyticra'},
      package_data={'pyticra': ['temp.*']},
      zip_safe=False)
