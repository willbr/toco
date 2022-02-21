wrun-tests:
	watchexec -cr "make run-tests"

d := tests\c13-pointers

run-tests:
	python test-python.py
	type $d\in.txt
	type $d\out.txt
	type $d\out.txt | tcc -run -

