# toco

input:

    def main
        printf "hello, world\n"

output:

    #include <stdio.h>

    int
    main(int argc, char **argv)
    {
        printf("hello, world\n");
        return 0;
    }

