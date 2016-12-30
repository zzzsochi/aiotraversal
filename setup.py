from setuptools import setup


setup(
    name='aiotraversal',
    version='0.9.2',
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
    url='https://github.com/zzzsochi/aiotraversal',
    keywords=['asyncio', 'aiohttp', 'traversal', 'pyramid'],
    packages=['aiotraversal'],
    install_requires=[
        'aiohttp>=0.21',
        'aiohttp_traversal>=0.8.1',
        'aiohttp_exc_handlers',
        'resolver-deco',
        'includer',
        'zini>=1.0.2',
    ],
    tests_require=['pytest'],
)
