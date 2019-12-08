from setuptools import setup
from comic_dl import config


with open('requirements.txt') as f:
    requirements = f.readlines()


setup(
    name='comic-dl',
    version=config.__version__,
    description='A cli comic downloader.',
    url='http://github.com/oluwafenyi/comic-dl/',
    author='oluwafenyi',
    license='MIT',
    package_name=['comic_dl'],
    zip_safe=False,
    install_requires=requirements,
    keywords='comics comic download',
    python_requires='>3.5',
    entry_points={
        'console-scripts': [
            'comic_dl = comic_dl.__main__:main'
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
