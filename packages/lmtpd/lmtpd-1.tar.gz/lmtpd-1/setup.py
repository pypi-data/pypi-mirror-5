try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'A LMTP server class',
    'long_description': 'A LMTP counterpart to smtpd in the Python standard library',
    'author': 'Matt Molyneaux',
    'url': 'https://github.com/moggers87/lmtpd',
    'download_url': 'https://github.com/moggers87/lmtpd',
    'author_email': 'moggers87+git@moggers87.co.uk',
    'version': '1',
    'license': 'MIT', # apparently nothing searches classifiers :(
    'packages': ['lmtpd'],
    'name': 'lmtpd',
    'classifiers': [
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2',
        'Intended Audience :: Developers',
        'Topic :: Communications :: Email']
}

setup(**config)
