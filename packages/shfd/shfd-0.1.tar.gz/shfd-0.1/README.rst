
Shfd : Sh for dummies
=====================

My custom wrapper for subprocess inspired by `Envoy <https://github.com/kennethreitz/envoy/>`_.

Features :

* full unicode support
* pipe with python operator |
* multi platform
* Method chaining available

Python versions supported :

* 2.6
* 2.7
* 3.1
* 3.2
* 3.3

Usage
-----

Run a command ::

	>>> cmd = shfd.run('echo "hello world"')
	>>> cmd.retcode
	0
	>>> cmd.out
	u'hello world\n'
	>>> cmd.err
	u''

Example with pipe and chaining ::

	>>> cmd = (shfd.cmd('git log') | 'head -n 30').run()
	>>> cmd.command
	u'git log | head -n 30'
	>>> cmd.out
	u'...'

Tests
-----

Test one version ::
	python test_shfd.py

Test all available versions ::
	python test_multi_shfd.py
