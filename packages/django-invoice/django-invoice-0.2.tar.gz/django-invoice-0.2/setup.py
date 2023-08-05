from distutils.core import setup

# Dynamically calculate the version
version_tuple = __import__('invoice').VERSION
if version_tuple[2] is not None:
    version = "%d.%d_%s" % version_tuple
else:
    version = "%d.%d" % version_tuple[:2]

setup(
    author = 'Simon Luijk',
    author_email = 'simon@simonluijk.com',
    name = 'django-invoice',
    version = version,
    description = 'Django invoicing app',
    url = 'https://github.com/simonluijk/django-invoice/',
    packages = [
        'invoice',
        'invoice.management',
        'invoice.management.commands',
        'invoice.utils',
        'invoice.conf',
    ],
    include_package_data = True,
    zip_safe = False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
