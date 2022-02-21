wrun-tests:
	watchexec -cr "make run-tests"

run-tests:
	python test-python.py
	type tests\c12-array\in.txt
	type tests\c12-array\out.txt
	type tests\c12-array\out.txt | tcc -run -

