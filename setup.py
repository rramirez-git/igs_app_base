import os
from setuptools import setup, find_packages

# Read README.md for long description
def read_file(filename):
    """Read file contents"""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

setup(
    name='igs-app-base',
    version='1.0.0',
    packages=find_packages(exclude=['tests', '*.tests', '*.tests.*']),
    include_package_data=True,
    author='RRamirez / IMAGILEX',
    author_email='rramirez@rramirez.com',
    description='Base Django app providing core functionality for iGrowSoft applications',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/imagilex/igs_app_base',
    project_urls={
        'Bug Tracker': 'https://github.com/imagilex/igs_app_base/issues',
        'Documentation': 'https://github.com/imagilex/igs_app_base',
        'Source Code': 'https://github.com/imagilex/igs_app_base',
    },
    license='MIT',
    python_requires='>=3.8',
    install_requires=[
        'Django>=5.1.2',
        'crispy-bootstrap5>=2024.10',
        'django-crispy-forms>=2.3',
        'django-extensions>=3.2.3',
        'django-weasyprint>=2.4.0',
        'PyMySQL>=1.1.1',
        'PyYAML>=6.0.2',
        'uritools>=5.0.0',
        'urllib3>=2.4.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0',
            'pytest-django>=4.5',
            'pytest-cov>=4.0',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 5.0',
        'Framework :: Django :: 5.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='django app igrowsoft base',
    zip_safe=False,
)
