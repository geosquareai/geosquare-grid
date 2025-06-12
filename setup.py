from setuptools import setup, find_packages

setup(
    name='geosquare-grid',
    version='1.0.0',
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
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'shapely',
    ],
    include_package_data=True,
)
