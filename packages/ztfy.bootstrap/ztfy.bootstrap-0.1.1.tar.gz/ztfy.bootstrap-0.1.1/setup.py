from setuptools import setup, find_packages
import os

DOCS = os.path.join(os.path.dirname(__file__),
                    'docs')

README = os.path.join(DOCS, 'README.txt')
HISTORY = os.path.join(DOCS, 'HISTORY.txt')
CONTRIBS = os.path.join(DOCS, 'CONTRIBUTORS.txt')

version = '0.1.1'
long_description = open(README).read() + '\n\n' + \
                   open(CONTRIBS).read() + '\n\n' + \
                   open(HISTORY).read()

tests_require = [
    'zope.testing',
]

setup(name='ztfy.bootstrap',
      version=version,
      description="Bootstrap based ZTFY skin",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Zope3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        "Topic :: Software Development :: User Interfaces"
        ],
      keywords='ZTFY bootstrap skin glyphicons',
      author='Thierry Florac',
      author_email='tflorac@ulthar.net',
      url='http://hg.ztfy.org/ztfy.bootstrap',
      license='zpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['ztfy'],
      include_package_data=True,
      package_data={'': ['*.zcml', '*.txt', '*.pt', '*.pot', '*.po', '*.mo', '*.png', '*.gif', '*.jpeg', '*.jpg', '*.css', '*.js']},
      zip_safe=False,
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'zope.component',
          'zope.i18nmessageid',
          'zope.interface',
          'ztfy.skin',
          'ztfy.utils',
      ],
      entry_points={
          'fanstatic.libraries': [
              'ztfy.bootstrap = ztfy.bootstrap:library',
              'ztfy.bootstrap.blog = ztfy.bootstrap.blog.skin:library'
          ]
      })
