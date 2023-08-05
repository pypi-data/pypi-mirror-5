.. automodule:: obiclean

   :py:mod:`obiclean` specific options
   --------------------------------------   

   .. cmdoption::  -d <INTEGER>, --distance=<INTEGER>   
   
                   Maximum numbers of differences between two variant sequences (default: 1).

   .. cmdoption::  -s <KEY>, --sample=<KEY>  
   
                   Attribute containing sample descriptions.

   .. cmdoption::  -r <FLOAT>, --ratio=<FLOAT>  
   
                   Threshold ratio between counts (rare/abundant counts) of two sequence records 
                   so that the less abundant one is a variant of the more abundant
                   (default: 1, i.e. all less abundant sequences are variants).

   .. cmdoption::  -H, --head  
   
                   Adds an attribute ``fathers`` containing the identifiers of the sequence records
                   from which this sequence record is a variant (default = False).


   .. include:: ../optionsSet/inputformat.txt
    
   .. include:: ../optionsSet/outputformat.txt
    
   .. include:: ../optionsSet/defaultoptions.txt
                   