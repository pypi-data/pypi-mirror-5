from setuptools import setup, find_packages

version = '0.5.0rc1'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(
    name='plonesocial.microblog',
    version=version,
    description="Simple microblogging in Plone",
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python"],
    keywords='plone socbiz social microblog',
    author='Guido Stevens',
    author_email='guido.stevens@cosent.net',
    url='http://github.com/cosent/plonesocial.microblog',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['plonesocial'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'plone.app.uuid',
        'Plone'],
    extras_require={'test':
                    ['plone.app.testing',
                     'Acquisition',
                     'ExtensionClass']},
    entry_points="""
      # -*- Entry points: -*-
          [z3c.autoinclude.plugin]
          target = plone
      """,)
