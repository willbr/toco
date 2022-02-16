
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
	ignore := echo ignore
endif


f := src/tests/c00-hello/in.txt
f := src/tests/c01-getchar/in.txt
f := src/tests/c02-let/in.txt
f := src/tests/c03-cat/in.txt
f := src/tests/c04-wc/in.txt
f := src/tests/c05-game/in.txt
f := src/tests/c06-params/in.txt
f := src/tests/c07-let-function/in.txt
f := src/tests/c08-pause/in.txt
f := src/tests/c09-print/in.txt
f := src/tests/c10-fprint/in.txt

tempfile := $(shell mktemp)

toco:
	$(cat) $f
	toco -o $(tempfile) $f
	$(cat) $(tempfile)
	$(rm) $(tempfile)

wtoco:
	watchexec -cr "make toco"

