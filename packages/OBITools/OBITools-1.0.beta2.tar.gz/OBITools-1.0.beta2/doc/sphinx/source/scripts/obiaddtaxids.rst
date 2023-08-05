.. automodule:: obiaddtaxids 

    :py:mod:`obiaddtaxids` specific options
    --------------------------------------- 

    .. cmdoption::  -f <FORMAT>, --format=<FORMAT>

                        Format of the sequence file. Possible formats are: 
                        
                            - ``raw``: for regular or :doc:`OBITools extended fasta <../fasta>` files (default value).
                            
                            - ``UNITE``: for fasta files downloaded from the `UNITE web site <http://unite.ut.ee/>`_.
                             
                            - ``SILVA``: for fasta files downloaded from the `SILVA web site <http://www.arb-silva.de/>`_.
                                                    
    .. cmdoption::  -k <KEYNAME>, --key-name=<KEYNAME>

                        Key of the attribute containing the taxon name in sequence files in 
                        :doc:`OBITools extended fasta <../fasta>` format. 
                      

    .. cmdoption::  -a <ANCESTOR>, --restricting_ancestor=<ANCESTOR>

                        Enables to restrict the search of taxids under a specified ancestor.
                        
                        ``<ANCESTOR>`` can be a taxid (integer) or a key (string). 
                        
                            - If it is a taxid, this taxid is used to restrict the search for all the sequence
                              records.
                        
                            - If it is a key, :py:mod:`obiaddtaxids`: looks for the ancestor taxid in the
                              corresponding attribute. This allows having a different ancestor restriction
                              for each sequence record.
                               
                            

    .. cmdoption::  -g <FILENAME>, --genus_found=<FILENAME>

                        File used to store sequences with a match found for the genus.
                        
                        .. CAUTION:: this option is not valid with the UNITE format.
                        

    .. cmdoption::  -u <FILENAME>, --unidentified=<FILENAME>

                        File used to store sequences with no taxonomic match found.

    .. include:: ../optionsSet/taxonomyDB.txt

    .. include:: ../optionsSet/defaultoptions.txt
    
    Example
    -------
    
        .. code-block:: bash
    
                > obiaddtaxids -T species_name -g genus_identified.fasta \
                               -u unidentified.fasta -d my_ecopcr_database \
                               my_sequences.fasta > identified.fasta

        Tries to match the value associated with the ``species_name`` key of each sequence record 
        from the ``my_sequences.fasta`` file with a taxon name from the ecopcr database ``my_ecopcr_database``. 
        
            - If there is an exact match, the sequence record is stored in the ``identified.fasta`` file. 
        
            - If not and the ``species_name`` value is composed of two words, :py:mod:`obiaddtaxids`: 
              considers the first word as a genus name and tries to find it into the taxonomic database. 
        
                - If a genus is found, the sequence record is stored in the ``genus_identified.fasta``
                  file. 
                  
                - Otherwise the sequence record is stored in the ``unidentified.fasta`` file.
    