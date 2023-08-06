from setuptools import setup

setup(
    name="tornado_circus",
    version="0.0.1",
    long_description="A tornado application compatible with circus socket",
    author="Boris FELD",
    author_email="lothiraldan@gmail.com",
    license="BSD",
    url='https://github.com/Lothiraldan/tornado_circus',
    packages=['tornado_circus'],
    install_requires=[
        'tornado',
    ],
)
