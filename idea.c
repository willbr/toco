#include <stdio.h>

struct char_array {
    size_t len;
    size_t cap;
    char *data;
};


int
main(int argc, char **argv)
{
    char array_data_line[10] = "hi";
    struct char_array line = {10, 10, array_data_line};
    puts(line.data);
    puts("bye");
    return 0;
}

