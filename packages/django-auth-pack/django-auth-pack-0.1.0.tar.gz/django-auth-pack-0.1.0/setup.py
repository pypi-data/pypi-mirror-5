import os
from setuptools import setup, find_packages


def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''


setup(
    name='django-auth-pack',
    version='0.1.0',
    author='Vitaliy Korobkin',
    author_email='root@digitaldemiurge.me',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/DigitalDemiurge/django-auth-pack',
    license='MIT license',
    install_requires=[
        'Django>=1.5',
        'django-crispy-forms>=1.3.2',
        'django-jsonview>=0.2.1',
        'django-templated-email>=0.4.9',
    ],
    classifiers=[
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
    ],
    long_description=read_file('README.md'),
    test_suite="runtests.runtests",
    zip_safe=False,
)
