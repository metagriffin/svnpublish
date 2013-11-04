test:
	nosetests --verbose

upload:
	python setup.py sdist upload

cheesecake:
        cheesecake_index --name=svnpublish

clean:
	find svnpublish -iname '*.pyc' -exec rm -f {} \;

tag:
	git tag -a "v`cat VERSION.txt`" -m "released v`cat VERSION.txt`"

