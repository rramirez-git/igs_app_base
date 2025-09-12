from setuptools import setup, find_packages

setup(
    name='igs_app_base',
    version='1.0.0',
    packages=find_packages(),
    author='RRamirez / IMAGILEX',
    author_email='rramirez@rramirez.com',
    description='Base package for django apps',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/imagilex/igs_app_base',
    license='MIT',
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
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
