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

### c array

    line := carray(10, char, "")

to

    char line[10] = "";

### fat array

    sprites := array(40, sprite)

to

```c
struct fat_array {
    size_t len;
    size_t cap;
    void *data;
};

void * alloc_array(size_t len, size_t cap, const char *data, size_t data_size, size_t elem_size);

sprites = alloc_array(40, 40, NULL, 0, sizeof(struct sprite))
```


### fat cstring
    line := "hello, world!"

to

```
struct cstring {
    size_t len;
    size_t cap;
    char *data;
};

void * alloc_array(size_t len, size_t cap, const char *data, size_t data_size, size_t elem_size);
struct cstring * alloc_cstring(const char *s);

struct cstring *line = alloc_cstring("");
printf("%s\n", line->data);
```

