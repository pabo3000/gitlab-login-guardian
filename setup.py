from setuptools import setup, find_packages

setup(
    name="gitlab_login_guardian",
    version="0.1",
    packages=find_packages(),
    install_requires=[],
    author='Pavel Bogdanovic',
    description='Block IPs from repeated GitLab login failures via NGINX',
    license='MIT',
)