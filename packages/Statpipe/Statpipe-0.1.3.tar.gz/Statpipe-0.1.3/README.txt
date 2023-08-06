Statpipe
=============


Statpipe is a simple command line utility allowing stata commands to be piped into
Stata on OSX, and the output returned.

For example:

    echo "di 2^2" | statpipe
    . di 2^2
    4

You can also use in interactive mode (although state isn't saved across calculations):

	statpipe
	> Enter a stata expression (e.g. di 2*2):
	di 2*2
	> Cached output re-used
	> . di 2*2
	> 4
	

To install, download and:

	cd statpipe
	python setup.py install #you might need to sudo if installing in system python
	
or

	pip install statpipe
