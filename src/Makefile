wrun-tests:
	watchexec -cr "make run-tests"

run-tests:
	python test-python.py
	type tests\c11-malloc\in.txt
	type tests\c11-malloc\out.txt
	type tests\c11-malloc\out.txt | tcc -run -

