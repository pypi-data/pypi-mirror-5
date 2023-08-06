from setuptools import setup, find_packages

setup(
    name='blimp',
    version='0.0.2',
    author='Jose Padilla',
    author_email='jpadilla@getblimp.com',
    packages=find_packages(),
    url='https://github.com/getblimp/blimp-python/',
    download_url='https://github.com/GetBlimp/blimp-python/tarball/master',
    license='MIT License',
    description='Blimp library for Python',
    long_description='Blimp library for Python',
    test_suite="tests.test_blimp",
    install_requires=[
        'requests'
    ],
)
