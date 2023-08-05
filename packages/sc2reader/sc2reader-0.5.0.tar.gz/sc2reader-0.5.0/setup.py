import sys
import setuptools

setuptools.setup(
    license="MIT",
    name="sc2reader",
    version='0.5.0',
    keywords=["starcraft 2","sc2","replay","parser"],
    description="Utility for parsing Starcraft II replay files",
    long_description=open("README.rst").read(),

    author="Graylin Kim",
    author_email="graylin.kim@gmail.com",
    url="https://github.com/GraylinKim/sc2reader",
    download_url="https://github.com/GraylinKim/sc2reader/archive/v0.4.0.tar.gz",

    platforms=["any"],

    classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            "Topic :: Games/Entertainment",
            "Topic :: Games/Entertainment :: Real Time Strategy",
            "Topic :: Software Development",
            "Topic :: Software Development :: Libraries",
            "Topic :: Utilities",
        ],

    entry_points={
        'console_scripts': [
            'sc2autosave = sc2reader.scripts.sc2autosave:main',
            'sc2printer = sc2reader.scripts.sc2printer:main',
            'sc2store = sc2reader.scripts.sc2store:main',
            'sc2replayer = sc2reader.scripts.sc2replayer:main',
            'sc2boprinter = sc2reader.scripts.sc2boprinter:main',
            'sc2parse = sc2reader.scripts.sc2parse:main',
            'sc2attributes = sc2reader.scripts.sc2attributes:main',
        ]
    },

    install_requires=['mpyq>=0.2.2','argparse'] if float(sys.version[:3]) < 2.7 else ['mpyq>=0.2.2'],
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=True
)
