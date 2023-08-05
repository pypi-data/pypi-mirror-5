from setuptools import setup, find_packages

version = '0.4.4'

setup(
    name='sorl-thumbnail-async',
    version=version,
    description='Asynchronous thumbnailing app in django with remote storages like S3',
    author='Nar Kumar Chhantyal',
    author_email='neokya@gmail.com',
    url='https://github.com/neokya/sorl-thumbnail-async',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'Django>=1.3',
    ],
)