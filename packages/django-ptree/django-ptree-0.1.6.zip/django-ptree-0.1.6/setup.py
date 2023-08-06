import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-ptree',
    version='0.1.6',
    packages=['ptree', 'ptree.models', 'ptree.mturk', 'ptree.templatetags', 'ptree.views'],
    include_package_data=True,
    license='MIT License',
    description='pTree is a Django toolset that makes it easy to create and administer social science experiments to online participants.',
    long_description=README,
    url='http://ptree.org/',
    author='Chris Wickens',
    author_email='c.wickens+ptree@googlemail.com',
    install_requires = ['boto', 'are-you-a-human', 'django-crispy-forms', 'Django >= 1.5.1', 'django-data-exports'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # replace these appropriately if you are using Python 3
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)