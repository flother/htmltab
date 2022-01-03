from setuptools import find_packages, setup


setup(
    name="htmltab",
    use_scm_version=True,
    description="A command-line utility that converts an HTML table into CSV data",
    long_description=open("README.md").read(),
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
    packages=find_packages("src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": ["htmltab=htmltab.cli:main"],
    },
    install_requires=[
        "beautifulsoup4 ~= 4.10",
        "click ~= 8.0",
        "lxml ~= 4.7",
        "cssselect ~= 1.1",
        "requests ~= 2.27",
    ],
    tests_require=[
        "pytest ~= 6.2",
        "pytest-cov ~= 3.0",
        "pytest-flake8 ~= 1.0",
        "httmock ~= 1.4",
    ],
    setup_requires=["setuptools_scm", "pytest-runner"],
)
