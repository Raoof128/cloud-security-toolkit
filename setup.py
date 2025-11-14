#!/usr/bin/env python
"""
Setup script for Cloud Security Toolkit
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = (this_directory / "requirements.txt").read_text(encoding='utf-8').splitlines()
requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name='cloud-security-toolkit',
    version='2.0.0',
    description='Automated cloud security auditing and hardening toolkit for AWS, Azure, and GCP',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Cloud Security Toolkit Contributors',
    author_email='',
    url='https://github.com/Raoof128/cloud-security-toolkit',
    project_urls={
        'Documentation': 'https://github.com/Raoof128/cloud-security-toolkit/blob/main/README.md',
        'Source': 'https://github.com/Raoof128/cloud-security-toolkit',
        'Tracker': 'https://github.com/Raoof128/cloud-security-toolkit/issues',
        'Changelog': 'https://github.com/Raoof128/cloud-security-toolkit/blob/main/CHANGELOG.md',
    },
    license='MIT',
    packages=find_packages(exclude=['tests', 'tests.*', 'examples', 'examples.*']),
    include_package_data=True,
    package_data={
        'reporting': ['templates/*.html'],
        'config': ['*.yaml', '.env.template'],
    },
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=8.0.0',
            'pytest-cov>=4.1.0',
            'moto>=5.0.0',
            'black>=24.0.0',
            'flake8>=7.0.0',
            'mypy>=1.8.0',
            'bandit>=1.7.0',
            'pre-commit>=3.0.0',
        ],
        'docs': [
            'sphinx>=7.0.0',
            'sphinx-rtd-theme>=2.0.0',
        ],
    },
    python_requires='>=3.10',
    entry_points={
        'console_scripts': [
            'cloud-security-audit=cloud_security_audit:main',
            'cloud-security-demo=demo_mode:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Security',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
        'Environment :: Console',
        'Natural Language :: English',
    ],
    keywords=[
        'aws',
        'security',
        'audit',
        'compliance',
        'cloud',
        'scanner',
        'cis',
        'remediation',
        'devsecops',
        'security-tools',
        'aws-security',
        'cloud-security',
        'security-audit',
        'vulnerability-scanner',
    ],
    zip_safe=False,
)
