from setuptools import setup


setup(
    name='dittybox',
    version='0.1dev',
    description='Useful scripts',
    packages=['dittybox'],
    install_requires=['fabric', 'pysphere'],
    entry_points = {
        'console_scripts': []
    }
)
