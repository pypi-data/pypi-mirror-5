# encoding: utf-8
import os
from setuptools import setup, find_packages


version = __import__('achilles').get_version()

def dump(filename):
    return open(os.path.join(os.path.dirname(__file__), filename))

setup(
    name='django-achilles',
    version=version,
    url='http://github.com/exekias/django-achilles/',
    author='Carlos Pérez-Aradros Herce',
    author_email='exekias@gmail.com',
    description='Django AJAX Framework',
    long_description=dump('README').read(),
    packages=find_packages(exclude=['example', '*.tests', '*.tests.*']),
    include_package_data=True,
    install_requires=[r.strip() for r in dump('requirements.txt')],
    tests_require=[r.strip() for r in dump('requirements-dev.txt')],
    zip_safe=False,
    license='Apache License (2.0)',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
