from setuptools import setup, find_packages


tests_require = [
    'Django>=1.4,<1.5',
    'South',
]

install_requires = [
    'requests>=1.2.2',
]

setup(name='django-shawty',
      version='0.0.3',
      description='Shawty URL shortener server integration for Django.',
      author='John Nadratowski',
      author_email='john@unifiedsocial.com',
      url='https://github.com/Unified/django_shawty',
      packages=find_packages(),
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={'test': tests_require},
      include_package_data=True,
      zip_safe=False,
      classifiers=[
          'Framework :: Django',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Operating System :: OS Independent',
          'Topic :: Software Development'
      ],
)
