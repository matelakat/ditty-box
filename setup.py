from setuptools import setup


setup(
    name='dittybox',
    version='0.1dev',
    description='Useful scripts',
    packages=['dittybox'],
    install_requires=['fabric', 'pysphere'],
    entry_points = {
        'console_scripts': [
            'esxi-list-vms = dittybox.scripts.esxi:list_vms',
            'esxi-toggle-disk = dittybox.scripts.esxi:toggle_disk'
        ]
    }
)
