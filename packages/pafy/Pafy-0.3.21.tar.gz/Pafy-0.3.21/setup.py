#!/usr/bin/python


from distutils.core import setup

setup(
    name='Pafy',
    py_modules=['pafy'],
    version='0.3.21',
    description="Python API for YouTube, query and download YouTube content",
    keywords=["Pafy", "API", "YouTube", "youtube", "download", "video"],
    author="nagev",
    author_email="np1nagev@gmail.com",
    url="http://np1.github.io/pafy/",
    download_url="https://github.com/np1/pafy/tarball/master",
    scripts=['ytdl'],
    package_data={"": ["LICENSE", "README", "CHANGELOG"]},
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Topic :: Multimedia :: Sound/Audio :: Capture/Recording",
        "Topic :: Utilities",
        "Topic :: Multimedia :: Video",
        "Topic :: Internet :: WWW/HTTP"],
    long_description=open("README").read()
)
