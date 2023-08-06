from setuptools import setup

long_description = """
Python client for juju-core websocket api.
"""

setup(
    name="juju-deployer",
    version="0.1.0",
    description="A tool for deploying complex stacks with juju.",
    long_description=open("README").read(),
    author="Kapil Thangavelu",
    author_email="kapil.foss@gmail.com",
    url="http://juju.ubuntu.com",
    install_requires=["jujuclient >= 0.0.5"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers"],
#    test_suite="test_deployment",
    entry_points={
        "console_scripts": [
            'juju-deployer = deployer:main']},
    py_modules=["deployer"])
