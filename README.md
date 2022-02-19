# toco

Playing with indented-expressions, and using them to represent c code.

input:

    include-lib "stdio.h"

    def main
        printf "hello, world\n"

output:

```c
#include <stdio.h>

void
main(void)
{
    printf("hello, world\n");
}
```

## let syntax from go :=

    include-lib "stdio.h"

    func-decl getchar(void) int

    def main
        c := getchar()
        while c != EOF
            putchar c
            c = getchar()

## go ish function declrations

    def main(argc int, argv **char) int
        a := double(10)
        return a


    def double(n int) int
        return n * 2


## print macros

    include-lib "stdio.h"

    def main(argc int, argv **char) int
        print "hello = {:hello d}, num = {10 d}, float = {3.6 2.2f}\n"
        println "goodbye = {:goodbye d}"

## lisp style keywords

unique enums

    include-lib "stdio.h"

    def main(argc int, argv **char) int
        poop := :poop
        println "{poop =d}"

## todo

### carray

    line := carray(10, char, "")

to

    char line[10] = "";

### array

    line := array(10 char, "")

to

    struct char_array {
        size_t len;
        size_t cap;
        char *data;
    };

    char_array line = {10, 10, (char[10]){}};

