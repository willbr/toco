#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct fat_array {
    size_t len;
    size_t cap;
    void *data;
};

struct cstring {
    size_t len;
    size_t cap;
    char *data;
};

void * alloc_array(size_t len, size_t cap, const char *data, size_t data_size, size_t elem_size);
struct cstring * alloc_cstring(const char *s);
void die(const char const * msg);


int
main(int argc, char **argv)
{
    /* Stack */
    char array_data_line1[10] = "a b c";
    struct cstring line1 = {10, 10, array_data_line1};

    puts("hi");

    printf("line1=\"%s\"\n", line1.data);

    line1.data[0] = '!';

    printf("line1=\"%s\"\n", line1.data);

    /* Heap */
    struct cstring *line2 = NULL;
    line2 = alloc_cstring("hello2");

    printf("line2=\"%s\"\n", line2->data);
    line2->data[5] = '!';
    printf("line2=\"%s\"\n", line2->data);

    puts("bye");
    return 0;
}


struct cstring *
alloc_cstring(const char *s)
{
    size_t slen = strlen(s);
    size_t cap  = slen * 2;
    struct array_char *r =
        alloc_array(slen, cap, s, slen + 1, sizeof(char));
    return r;
}


void *
alloc_array(size_t len, size_t cap, const char *data, size_t data_size, size_t elem_size)
{
    char *array_data = NULL;
    struct fat_array *array = NULL;

    if (len > cap)
        die("len > cap");

    if (data == NULL)
        die("data is NULL");

    array_data = malloc(elem_size * cap);
    if (array_data == NULL)
        die("data alloc failed");

    array = malloc(sizeof(struct fat_array));
    if (array == NULL)
        die("struct alloc failed");

    memcpy(array_data, data, data_size);

    array->len = len;
    array->cap = cap;
    array->data = array_data;

    return array;
}


void
die(const char const * msg)
{
    fprintf(stderr, "ERROR: ");
    fprintf(stderr, msg);
    fprintf(stderr, "\n");
    exit(1);
}

