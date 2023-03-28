import setuptools
from pip._internal.req import parse_requirements

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
install_reqs = parse_requirements("requirements.txt", session="reqs")
reqs = [str(ir.requirement) for ir in install_reqs]

setuptools.setup(
    name="riet",
    version="0.0.1",
    description="data utils for queries / streams. Currently implemented is twitter",
    author='Michael Shliselberg',
    author_email='michael.shliselberg@uconn.edu',
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=install_reqs
)