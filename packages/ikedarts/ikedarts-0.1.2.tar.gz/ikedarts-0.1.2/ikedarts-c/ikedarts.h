#ifndef IKEDARTSS_H
#define IKEDARTSS_H

#ifdef  __cplusplus
extern "C" {
#endif

typedef int (*ikedarts_advance_on_match)(int sofar, int current);
typedef int (*ikedarts_advance_on_miss)(const char *cp);

struct ikedarts {
				// decide how much to advance in the case of a match.
				// defaults to advancing by the maximal match.
	ikedarts_advance_on_match advance_on_match;
				// number of bytes to advance in case 
				// of a mismatch at that point in the text 
	ikedarts_advance_on_miss advance_on_miss;
				// private 
	void *da;
};

/* 
 * - text:   null-terminated byte string to search for matches.
 * - offset: number of bytes into text where the match occured.
 * - length: matching word length in bytes.
 * - value:  opaque value associated with the word in the dictionary.
 */
typedef int visit_t(const char* text, 
		    unsigned int offset, 
		    unsigned int length, 
		    int value, 
		    void *data);

/* mallocs when NULL is passed */
struct ikedarts *ikedarts_init(struct ikedarts *ikd);
/* returns 0 for success */
extern int ikedarts_open(struct ikedarts *ikd, const char *index_path);
extern int ikedarts_match(struct ikedarts *ikd, const char *text, visit_t, void *data);
extern int ikedarts_search(struct ikedarts *ikd, const char *text, visit_t, void *data);
extern void ikedarts_finish(struct ikedarts *ikd);
extern int ikedarts_markup(const char *index_path);
extern int ikedarts_main(int argc, char **argv) ;

#ifdef  __cplusplus
}
#endif

#endif /* IKEDARTSS_H */
