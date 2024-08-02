# coding: utf-8


from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django-decorators",
    version="1.0",
    description='django decorators、django annotation',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="liangalien",
    author_email="lsq54264@vip.qq.com",
    url='https://github.com/liangalien/django-decorators',
    packages=find_packages(),
    install_requires=['django'],
    python_requires=">=3.6",
    keywords=['django decorators', 'django annotation', 'django request annotation'],
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
