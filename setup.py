from setuptools import find_packages, setup

setup(
    name='PhoenixGUI',
    packages=find_packages(include=['PhoenixGUI', 'pygame']),
    version='0.1.0',
    description='My first Python library',
    author='Me',
    install_requires=[],
    setup_requires=['pytest-runner', 'pygame'],
    tests_require=['pytest'],
    test_suite='tests',
)