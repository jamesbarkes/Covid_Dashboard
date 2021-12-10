import setuptools

with open("README.md", "r") as readme:
   user_manual = readme.read()

setuptools.setup(
    name="Covid19_Dashboard_Jamesbarkes",
    version="1",
    author="James Barkes",
    author_email="jb1382@exeter.ac.uk",
    description="This is a program that displays local and national coronavirus statistics, and top news.",
    long_description=user_manual,
    long_description_content_type="text/markdown",
    url="https://github.com/jamesbarkes/covid_dashboard",
    packages=setuptools.find_packages(),
    classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
],
python_requires='>=3.6',
)
