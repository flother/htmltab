from setuptools import setup

from htmltab import __version__


setup(name="htmltab",
      version=__version__,
      description="A command-line utility that converts an HTML table into "
                  "CSV data",
      long_description=open("README.rst").read(),
      url="https://github.com/flother/htmltab",
      license="MIT",
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Natural Language :: English",
          "Programming Language :: Python :: 3",
          "Topic :: Utilities",
      ],
      packages=["htmltab"],
      entry_points={
          "console_scripts": ["htmltab=htmltab.cli:main"],
      },
      install_requires=[
          "beautifulsoup4>=4.3.2",
          "click>=6.0",
          "lxml>=3.2.0",
          "cssselect>=0.9.1",
          "requests>=2.4.0",
      ],
      tests_require=[
        "pytest>=2.6.0",
        "pytest-cov>=2.0.0",
        "pytest-pep8>=1.0",
        "httmock>=1.2.3",
      ],
      setup_requires=["pytest-runner"])
