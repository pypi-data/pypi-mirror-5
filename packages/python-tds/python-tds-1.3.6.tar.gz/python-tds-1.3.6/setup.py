from distutils.core import setup

setup(name='python-tds',
      version='1.3.6',
      description='Python DBAPI driver for MSSQL using pure Python TDS (Tabular Data Stream) protocol implementation',
      author='Mikhail Denisenko',
      author_email='denisenkom@gmail.com',
      url='https://github.com/denisenkom/pytds',
      packages=['pytds'],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
      ],
      zip_safe=True,
      install_requires=['python-dateutil'],
      )
