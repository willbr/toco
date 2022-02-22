wrun-tests:
	watchexec -cr "make run-tests"

d := tests\c11-malloc
d := tests\c13-pointers
d := tests\c01-getchar
d := tests\c12-array

run-tests:
	rem type $d\in.txt
	rem toco $d\in.txt
	rem tcc -run temp.c one two three
	python test-python.py
	rem type $d\out.txt
	rem type $d\out.txt | tcc -run -

