from setuptools import find_packages
from setuptools import setup


def get_long_description():
    with open('README.md') as readme_file:
        return readme_file.read()


setup(
    name="RouterOS-api",
    version='0.20.0',
    description='Python API to RouterBoard devices produced by MikroTik.',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='Social WiFi',
    author_email='it@socialwifi.com',
    url='https://github.com/socialwifi/RouterOS-api',
    packages=find_packages(),
    test_suite="tests",
    license="MIT",
    install_requires=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
