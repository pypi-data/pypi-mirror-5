# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='django-rshop',
    version='0.0.7',
    author=u'Oscar M. Lage Guitian',
    author_email='r0sk10@gmail.com',
    #packages=['rshop'],
    packages = find_packages(),
    include_package_data = True,
    package_data = {'': ['rshop/templates', 'rshop/static','rshop/fixtures',], 'rshop-example': ['rshop-example/*']},
    url='http://bitbucket.org/r0sk/django-rshop',
    license='BSD licence, see LICENSE file',
    description='Yet another Django Flatpages App',
    zip_safe=False,
    long_description=open('README.rst').read(),
    install_requires=[
        "Django < 1.5",
        "South == 0.7.5",
        "django-tinymce >= 1.5.1b2",
        "django-filebrowser-no-grappelli == 3.1.1",
        "sorl-thumbnail == 11.12",
        "django-compressor == 1.1.2",
    ],
    keywords = "django application flatpages",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
