.. automodule:: obiuniq


   
   :py:mod:`obiuniq` specific options
   ------------------------------------   

   .. cmdoption::  -m <KEY>, --merge=<KEY>   

     Attribute to merge.

     *Example:*
    
        .. code-block:: bash

            > obiuniq -m sample seq1.fasta > seq2.fasta
    
        Dereplicates sequences and keeps the value distribution of the ``sample`` attribute
        in the new attribute ``merged_sample``.

   .. cmdoption::  -i , --merge-ids
       
     Adds a ``merged`` attribute containing the list of sequence record ids merged
     within this group.
   
   .. cmdoption::  -c <KEY>, --category-attribute=<KEY>

     Adds one attribute to the list of attributes used to define sequence groups
     (this option can be used several times).

     *Example:*
    
        .. code-block:: bash

            > obiuniq -c sample seq1.fasta > seq2.fasta
    
        Dereplicates sequences within each sample.

   .. cmdoption::  -p, --prefix
        
     Dereplication is done based on prefix matching:
        
            1. The shortest sequence of each group is a prefix of any sequence of its group
            
            2. The shortest sequence of a group is the prefix of only the sequences belonging
               to its group 


   .. include:: ../optionsSet/taxonomyDB.txt

   .. include:: ../optionsSet/inputformat.txt

   .. include:: ../optionsSet/defaultoptions.txt
