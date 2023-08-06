from distutils.core import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
	name='WebUI',
	version='0.1.4',
	author='Nick Johnstone',
	author_email='ncwjohnstone@gmail.com',
	packages=['webui'],
	scripts=['examples/test_app.py'],
	url='https://github.com/Widdershin/WebUI/',
	license='MIT',
	description='WebUI lets you create first class desktop applications in Python with HTML/CSS',
	long_description=open('README').read(),
	install_requires=required,
	)