
go: red_black_set_mod.py red_black_dict_mod.py
	./this-pylint \
		--ignore-message '^.*Similar lines in .* files.*$$' \
		--ignore-message '^.*Too many lines in module.*$$' \
		--to-pylint test-red_black_tree_mod red_black_set_mod.py
	python3 ./test-red_black_tree_mod
	python ./test-red_black_tree_mod
	/usr/local/pypy-2.1/bin/pypy test-red_black_tree_mod
	/usr/local/jython-2.7b1/bin/jython test-red_black_tree_mod
	./print-tree

red_black_set_mod.py: red_black_tree_mod.m4
	m4 -Dm4set=1 -Dm4key=1 red_black_tree_mod.m4 > red_black_set_mod.py

red_black_dict_mod.py: red_black_tree_mod.m4
	m4 -Dm4set=1 -Dm4keyvalue=1 red_black_tree_mod.m4 > red_black_dict_mod.py

clean:
	rm -rf *.pyc __pycache__ *.class red_black_set_mod.py red_black_dict_mod.py MANIFEST dist

publish: red_black_set_mod.py red_black_dict_mod.py
	python setup.py sdist upload
	./prepare-tarballs

