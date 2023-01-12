from setuptools import setup, find_packages


with open("requirements.txt") as f:
    required = [line for line in f.read().splitlines() if not line.startswith("-")]

with open("VERSION") as f:
    version = f.read()

setup(
    name="singleton-class-decorator",
    version=version,
    description="Singleton Class Decorator",
    url="https://github.com/Jrmy-rbr/singleton-class-decorator",
    author="Jeremy Ribeiro",
    author_email="jeremy.d.ribeiro@gmail.com",
    install_requires=required,
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.9",
)
