from setuptools import setup
from comic_dl.core import __version__


with open('requirements.txt') as f:
    requirements = f.readlines()


setup(
    name='comicdl',

    version=__version__,
    description='A cli comic downloader.',
    url='http://github.com/oluwafenyi/comic-dl/',
    author='oluwafenyi',
    author_email='o.enyioma@gmail.com',
    license='MIT',
    zip_safe=False,
    include_package_data=True,
    packages=['comic_dl', 'comic_dl.core', 'comic_dl.utils'],
    install_requires=requirements,
    keywords='comics comic download cli',
    python_requires='>3.5',
    entry_points={
        'console_scripts': [
            'comic-dl = comic_dl.core.commands:execute_from_command_line'
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux"
    ],
)
