ifeq ($(OS),Windows_NT)     # is Windows_NT on XP, 2000, 7, Vista, 10...
    detected_OS := Windows
	PATH := $(PATH);./bin/
	mkdir := mkdir
	make := make
	rm := del
	cat := type
	EXE := .exe
	ignore := rem
else
    detected_OS := $(shell uname)  # same as "uname -s"
	PATH := $(PATH):./bin/
	mkdir := mkdir
	make := make
	rm := rm
	cat := cat
	EXE :=
	ignore := $(shell echo '#')
endif

wrun-tests:
	watchexec -cr "make run-tests"

d := tests/c11-malloc
d := tests/c01-getchar
d := tests/c12-array
d := tests/c13-pointers


l_in := $d/in.txt
l_out := $d/out.txt

ifeq ($(OS),Windows_NT)     # is Windows_NT on XP, 2000, 7, Vista, 10...
	in  := $(subst /,\,$(l_in))
	out := $(subst /,\,$(l_out))
else
	in  := $(l_in)
	out := $(l_out)
endif


run-tests:
	$(ignore) type $(in)
	$(ignore) toco $(in)
	$(ignore) tcc -run temp.c one two three
	$(ignore)
	python test-python.py
	$(ignore) type $(out)
	$(ignore)
	$(cat) $(out) | tcc -run -

