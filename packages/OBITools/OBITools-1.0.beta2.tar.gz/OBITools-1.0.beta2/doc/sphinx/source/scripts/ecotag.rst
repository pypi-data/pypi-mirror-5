.. automodule:: ecotag
   
   :py:mod:`ecotag` specific options
   ------------------------------------   

   .. cmdoption::  -R <FILENAME>, --ref-database=<FILENAME>   
   
        <FILENAME> is the fasta file containing the reference sequences

   .. cmdoption::  -m FLOAT, --minimum-identity=FLOAT
   
        When sequence identity is less than FLOAT, the taxonomic 
        assignment for the sequence record is not indicated in ``ecotag``'s 
        output. FLOAT is included in a [0,1] interval.
        (This option doesn't seem to work).

   .. cmdoption::  -x RANK, --explain=RANK
   
   .. cmdoption::  -u, --uniq
   
        When this option is specified, the program first dereplicates the sequence 
        records to work on unique sequences only. This option greatly improves 
        the program's speed, especially for highly redundant datasets.

   .. cmdoption::  --sort=ATTRIBUTE
   
        The output is sorted based on the values of the attribute called ``ATTRIBUTE``.

   .. cmdoption::  -r, --reverse
   
        The output is sorted in reverse order (should be used with the --sort option).
        (Works even if the --sort option is not set, but couldn't find on what 
        the output is sorted).

   .. cmdoption::  -E FLOAT, --errors=FLOAT
   
        FLOAT is the fraction of reference sequences that will 
        be ignored when looking for the most recent common ancestor. This 
        option is useful when a non-negligible proportion of reference sequences 
        is expected to be assigned to the wrong taxon, for example because of 
        taxonomic misidentification. FLOAT is included in a [0,1] interval.

   .. include:: ../optionsSet/taxonomyDB.txt
   
   .. include:: ../optionsSet/defaultoptions.txt
   
   