
=======
PyNOMAD
=======

PyNOMAD is used for accessing a locally hosted copy of The Naval 
Observatory Merged Astrometric Dataset (NOMAD).  More information on 
NOMAD is available at:
    http://www.nofs.navy.mil/nomad/

Full copies of the NOMAD catalog are large:
    92Gigs uncompressed 
        or 
    30Gigs when compressed with:  gzip --best nomad/[0-9][0-9][0-9]/m*
    
The nomad.py module works with either uncompressed or compressed copies
of the catalog.

A typical usage to fetch a region of the catalog is:

    #!/usr/bin/env python

    from nomad import fetch_nomad_box

    ra_range = [281., 281.05]  #    RA is in degrees
    dec_range = [-30.6, -30.55]  #  Dec is in degrees
    stars = fetch_nomad_box(ra_range, dec_range, epoch=2000.0)
    
A typical usage to retrieve by NOMAD catalog ID is:

    #!/usr/bin/env python

    from nomad import fetch_star_by_nomad_id

    star = fetch_star_by_nomad_id(['0594-0896798'], epoch=None)

    stars = fetch_star_by_nomad_id(['0594-0896794', '0594-0896795', 
                                    '0594-0896796', '0594-0896798'], epoch=None)

Note that in all cases the returned object is a `pandas.DataFrame`.



Some catalog data files used for testing the code are included in:
    test/data
These are grabbed directly from USNO's website serving the NOMAD database:
    http://www.nofs.navy.mil/data/fchpix/
These can be used to perform one-time tests cross-checking that the nomad 
module is working correctly with the local copy of the catalog.
These tests (and some other internal consistency checks) can be run by 
using the nomad_test.py module:
    python nomad_test.py

========

Originally written 2013-04-05 by Henry Roe (hroe@hroe.me)
