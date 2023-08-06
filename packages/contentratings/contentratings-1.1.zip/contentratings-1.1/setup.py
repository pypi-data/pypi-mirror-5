from setuptools import setup, find_packages
import os

version = '1.1'


def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    text = unicode(text, 'utf-8').encode('ascii', 'xmlcharrefreplace')
    return text


description = read('README.txt') + '\n\n' + \
    'Detailed Documentation\n' + \
    '**********************\n\n' + \
    read('contentratings', 'README.txt') + '\n\n' + \
    read('HISTORY.txt')


setup(name='contentratings',
      version=version,
      description="A small Zope 3 package (which also works with Zope 2.10+ and Five) that allows you to attach ratings to content.",
      long_description=description,
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Framework :: Zope3',
          'Framework :: Zope2',
          'Framework :: Plone',
          'Framework :: Plone :: 4.0',
          'Framework :: Plone :: 4.1',
          'Framework :: Plone :: 4.2',
          'Framework :: Plone :: 4.3',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      keywords='ratings zope plone zope3',
      author='Alec Mitchell',
      author_email='apm13@columbia.edu',
      url='http://plone.org/products/contentratings',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.app.content',
          'zope.componentvocabulary',
          'zope.container',
      ],
      extras_require=dict(test=['zope.app.testing', ]),
      )
