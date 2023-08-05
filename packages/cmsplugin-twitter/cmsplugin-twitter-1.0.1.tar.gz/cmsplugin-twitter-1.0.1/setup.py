from setuptools import setup, find_packages

version = '1.0.1'

setup(
    name='cmsplugin-twitter',
    version=version,
    description='Twitter plugin to work with Django-CMS',
    author='Vinit Kumar',
    author_email='vinit.kumar@changer.nl',
    url='http://github.com:vinitcool76/cmsplugin-twitter.git',
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
    ],
)
