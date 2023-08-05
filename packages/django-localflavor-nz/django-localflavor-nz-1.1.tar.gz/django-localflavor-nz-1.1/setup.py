import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name = 'django-localflavor-nz',
    version = '1.1',
    description = 'Country-specific Django helpers for New Zealand.',
    long_description = README,
    author = 'Marek Kuziel',
    author_email = 'marek@kuziel.info',
    license='BSD',
    url = 'https://bitbucket.org/markuz/django-localflavor-nz',
    packages = ['django_localflavor_nz'],
    include_package_data = True,
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires=[
        'Django>=1.4',
    ]
)
