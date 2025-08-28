from setuptools import setup, find_packages

setup(
    name='geosquare-grid',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    author='Geosquare Team',
    author_email='admin@geosquare.ai',
    description='A library for converting geographic coordinates to grid identifiers and performing spatial operations.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/geosquareai/geosquare-grid',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'shapely>=2.0.1',
    ],
    include_package_data=True,
)
