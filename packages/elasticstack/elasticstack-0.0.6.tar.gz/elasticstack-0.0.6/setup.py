import os
from setuptools import setup, find_packages


setup(
    author="Ben Lopatin",
    author_email="ben.lopatin@wellfireinteractive.com",
    name='elasticstack',
    version='0.0.6',
    description='Configurable indexing and other extras for Haystack (with ElasticSearch biases)',
    long_description=open(os.path.join(os.path.dirname(__file__),
        'README.rst')).read(),
    url='https://github.com/bennylope/elasticstack/',
    license='BSD License',
    platforms=['OS Independent'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    install_requires=[
        'Django>=1.4',
        'django-haystack>=2.0.0',
        'pyelasticsearch>=0.5',
    ],
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
)
