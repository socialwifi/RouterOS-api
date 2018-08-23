from setuptools import find_packages
from setuptools import setup


setup(
    name="RouterOS-api",
    version='0.15.0',
    description='Python API to RouterBoard devices produced by MikroTik.',
    author='Social WiFi',
    author_email='it@socialwifi.com',
    url='https://github.com/socialwifi/RouterOS-api',
    packages=find_packages(),
    test_suite="tests",
    license="MIT",
    install_requires=['six'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
