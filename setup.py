from setuptools import setup


setup(
    name='aiotraversal',
    version='0.7.0',
    description='Traversal based asyncronious web framework',
    # long_description=README,
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Internet :: WWW/HTTP",
    ],
    author='Alexander Zelenyak',
    author_email='zzz.sochi@gmail.com',
    url='',
    keywords=['asyncio', 'aiohttp', 'traversal', 'pyramid'],
    packages=['aiotraversal'],
    install_requires=[
        'aiohttp',
        'aiohttp_traversal>=0.8',
        'aiohttp_exc_handlers',
        'resolver-deco',
        'includer',
    ],
    tests_require=['pytest'],
)
