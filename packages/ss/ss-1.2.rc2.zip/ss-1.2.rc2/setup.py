from setuptools import setup, find_packages
description = "Command line script that automatically searches for video subtitles using OpenSubtitles.org APIs."

setup(
    name = "ss",
    version = "1.2.rc2",
    packages = [],
    scripts = ['ss.py'],
    py_modules=['calculate_hash'],
    install_requires=[x.strip() for x in file('requirements.txt')],
    entry_points = {'console_scripts' : ['ss = ss:Main']},
    
    # metadata for upload to PyPI
    author = "nicoddemus@gmail.com",
    author_email = "nicoddemus@gmail.com",
    description = description,
    license = "GPL",
    keywords = "subtitles script",
    url = "http://nicoddemus.github.io/ss/",  
    
    use_2to3=True,
)
