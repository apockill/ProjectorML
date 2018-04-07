from setuptools import setup


scripts = []

setup(
    name='projector_cv',
    scripts=scripts,
    version='0.1',
    description='This is a fun side-project for messing around with projection mapping',
    packages=['hardware'],
    install_requires=["screeninfo"],
    zip_safe=False
)