import os
from setuptools import setup, find_packages
from wagtailmenus import __version__, stable_branch_name

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

base_url = "https://github.com/ababic/waddleadmin/"
dowload_url = '%starball/v%s' % (base_url, __version__)
branch_url = "%stree/stable/%s" % (base_url, stable_branch_name)

# Testing dependencies
testing_extras = [
    'django-webtest>=1.8.0',
    'beautifulsoup4>=4.4.1,<4.5.02',
    'coverage>=3.7.0',
]

setup(
    name="waddleadmin",
    version=__version__,
    author="Andy Babic",
    author_email="ababic@rkh.co.uk",
    description=("It's a playground for me to try out development ideas for "
                 "Wagtail's contrib.modeladmin app."),
    long_description=README,
    packages=find_packages(),
    license="MIT",
    keywords="wagtail cms model utility",
    download_url=dowload_url,
    url=branch_url,
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        'Topic :: Internet :: WWW/HTTP',
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    install_requires=[
        "wagtail>=1.9",
    ],
    extras_require={
        'testing': testing_extras,
    },
)
