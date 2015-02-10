# inspire-riq
Compute the riq-index for an author on InspireHep.net

The Research Impact Quotient (riq) is the ratio of the square-root of the Total
Research Impact (tori) to the number of years since the date of the first
publication of the author. (See arxiv:1209.2124 for more details.) This script
presents the "riq index", taken to be 1000 times the riq, based on the data
available on inspirehep.net. Thus, it is intended for people in high energy
physics and related fields.

Note that in computing the tori, self-citations are removed only in the cases
that the author for whom we are computing the riq index is an author of the
citing article. I.e. if paper A by X and Y is cited by paper B by Y alone, we do
not consider paper B a self-cite when computing the tori of X. (However, it
would be excluded for the tori of Y.)

The main speed limitation is the way in which bibliography lengths must be
determined. On InspireHep, there is (as far as I know) no way to query the
number of references of a record directly. This script works by obtaining the
MARCXML of *every* citing article, then counting the number of bibliography
entries. An alternate strategy might be to download the XHTML output and parsing
out the number cached by InspireHep. (I'll see how much faster it is and update
if it's worth it.)


