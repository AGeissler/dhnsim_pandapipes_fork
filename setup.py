from setuptools import find_packages
from setuptools import setup

setup(
    name='dh_network_simulator',
    version='0.1.2',
    url='https://github.com/AGeissler/dhnsim_pandapipes_fork.git',
    license='BSD 3-Clause License',
    author='Christopher W. Wild',
    author_email='cww@plan.aau.dk',
    description='A pipeflow simulation tool that complements pandapipes and enables static and dynamic heat transfer simulation in district heating systems.',
    install_requires=["pandapipes>=0.3.0", "numpy", "pandas", "dataclasses", "simple_pid"],
    extras_require={"docs": ["numpydoc", "sphinx", "sphinxcontrib.bibtex"],
                    "plotting": ["matplotlib"],
                    "test": ["pytest"]},
    python_requires='>=3, <4',
    packages=find_packages(),
)
