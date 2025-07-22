from setuptools import setup

setup(
    name='gitlab-login-guardian',
    version='0.1',
    py_modules=['ban_gitlab_logins'],
    entry_points={
        'console_scripts': [
            'gitlab-login-guardian=ban_gitlab_logins:main',
        ],
    },
    author='Pavel Bogdanovic',
    description='Block IPs from repeated GitLab login failures via NGINX',
    license='MIT',
)