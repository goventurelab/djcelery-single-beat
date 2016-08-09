import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='djcelery-single-beat',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='Ensures single celery beat instance.',
    long_description=README,
    url='https://goventurelab.com/',
    author='Ali Bozorgkhan',
    author_email='ali@goventurelab.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'pyuv >= 0.10,<1.0.0',
        'redis >= 2.9.1'
    ],
)
