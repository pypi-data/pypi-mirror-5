from setuptools import setup

def readme():
    with open('README') as f:
        return f.read()


setup(
    name='bibos_utils',
    version='0.0.2.1',
    description='Utilities for the BibOS system',
    long_description=readme(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
    ],
    url='https://github.com/magenta-aps/',
    author='Magenta ApS',
    author_email='info@magenta-aps.dk',
    license='GPLv3',
    packages=['bibos_utils'],
    install_requires=['PyYAML',],
    scripts=['bin/get_bibos_config', 'bin/set_bibos_config'],
    zip_safe=False
)
