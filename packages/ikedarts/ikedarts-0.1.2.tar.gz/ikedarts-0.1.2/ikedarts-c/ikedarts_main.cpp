#include "ikedarts.h"
#include <iostream>
extern "C" {
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>
}

/*
 * present the matched word.
 */
int dump_match(const char* text, unsigned int offset, unsigned int length, int value, void *data) 
{
	int i;
	char *tok=strndup(text, length);

	assert(tok);
	//printf("\t%s\tl=%d, v=%d\n", tok, length, value);
	for (i=0; i<offset; i++)
		printf(" ");
	printf("%s\n", tok);
	free(tok);
	return 0;
}

int ikedarts_markup(const char *index_path)
{
	struct ikedarts ikd;

	ikedarts_init(&ikd);

	if (ikedarts_open(&ikd, index_path)!=0) {
		fprintf(stderr, "failed to open %s\n", index_path);
		return -1;
	}

	char line[1024];
	while (std::cin.getline(line, sizeof(line))) {
		printf("%s\n", line);
		ikedarts_search(&ikd, line, dump_match, line);
		printf("\n");
	}

	ikedarts_finish(&ikd);

	return 0;
}

int main(int argc, char **argv) 
{
	if (argc < 2) {
		fprintf(stderr, "usage %s foo.da\n", argv[0]);
		return -1;
	}
	ikedarts_markup(argv[argc-1]);
	return 0;
}
