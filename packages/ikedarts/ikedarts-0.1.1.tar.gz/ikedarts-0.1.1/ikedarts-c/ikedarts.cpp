/* based on darts.cpp by Taku Kudo
*/
#include <darts.h>
#include <iostream>
#include <string>

////////////////

extern "C" {
#include "ikedarts.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>
}

static Darts::DoubleArray *da(struct ikedarts *ikd) {
	return (Darts::DoubleArray *)ikd->da;
}

/*****
  todo: generalize ikedarts_advance_on_* to ful skip/advance api:
        class Hopper:
	    init(text):   init the state to look at text.
            match(word):  examine a match at the point.
	    advance_by(): number of bytes to advance.

        configure the scanner with an instance of a hopper.
*****/
static int default_advance_on_match(int sofar, int current) {
	return current>sofar ? current : sofar;
}

/* 
 * how many bytes to advance in the case of mismatch at the text.
 * this implementation is for ascii.
 * todo: implement a proper skip function for utf8.
 */
static int default_advance_on_miss(const char *cp) {
	return 1;
}

struct ikedarts *ikedarts_init(struct ikedarts *ikd) 
{
	if (!ikd) {
		ikd=(struct ikedarts *)malloc(sizeof(struct ikedarts));
	}
	assert(ikd);
	ikd->da=new Darts::DoubleArray();
	assert(da(ikd));

	// set defaults. caller can set public fields to configure the instance.
	ikd->advance_on_match=default_advance_on_match;
	ikd->advance_on_miss=default_advance_on_miss;

	return ikd;
}

int ikedarts_open(struct ikedarts *ikd, const char *index_path) 
{
	assert(ikd);
	return da(ikd)->open(index_path);
}

int ikedarts_match(struct ikedarts *ikd, const char *text, visit_t visit, void *data) 
{
	assert(ikd);
	assert(da(ikd));

	Darts::DoubleArray::result_pair_type  result_pair[1024]; // xx

	size_t nmatches = da(ikd)->commonPrefixSearch(text, result_pair, sizeof(result_pair));
	if (nmatches>0) {
		for (size_t i = 0; i < nmatches; ++i) {
			visit(text, 0, result_pair[i].length, result_pair[i].value, data);
		}
	}
	return nmatches;
}

int ikedarts_search(struct ikedarts *ikd, const char *text, visit_t visit, void *data) 
{
	assert(ikd);
	assert(da(ikd));

	Darts::DoubleArray::result_pair_type result_pair[1024]; // xx

	const char *cp=text;
	int total_matches=0;

	while (*cp) {

		size_t nmatches = da(ikd)->commonPrefixSearch(cp, result_pair, sizeof(result_pair));
		if (nmatches>0) {
			int advance_by=-1;
			for (size_t i = 0; i < nmatches; ++i) {
				Darts::DoubleArray::result_pair_type &r=result_pair[i];
				assert(r.length>0); // don't let empty string get into the dict.
				visit(cp, cp-text, r.length, r.value, data);
				if (advance_by<0) { // first time
					advance_by=r.length;
				} else {
					advance_by=ikd->advance_on_match(advance_by, r.length);
				}
			}
			total_matches+=nmatches;
			cp+=advance_by;
		} else {
			cp+=ikd->advance_on_miss(cp);
		}
	}

	return total_matches;
}

void ikedarts_finish(struct ikedarts *ikd) 
{
	assert(ikd);
	delete da(ikd);
}
