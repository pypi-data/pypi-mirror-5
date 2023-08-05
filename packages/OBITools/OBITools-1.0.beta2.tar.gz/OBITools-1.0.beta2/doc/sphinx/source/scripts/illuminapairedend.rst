.. automodule:: illuminapairedend

    :py:mod:`illuminapairedend` specific options
    -------------------------------------------- 

    .. cmdoption::      -r <FILENAME>, --reverse-reads=<FILENAME>
                        
        Filename points to the file containing the reverse reads.

    .. cmdoption::      --score-min=<FLOAT>    
   
        minimum score for keeping alignment. If the alignment score is
        below this threshold both the sequences are just concatenated.
        The ``mode`` attribute is set to the value ``joined``.

    Options to specify input format
    -------------------------------
    
    .. program:: obitools

    Fastq related format
    ....................
    
    .. cmdoption::      --sanger              
    
           Input file is in :doc:`Sanger fastq nucleic format <../fastq>`  (standard
           fastq used by HiSeq/MiSeq sequencers).
    
    .. cmdoption::      --solexa              
    
           Input file is in :doc:`fastq nucleic format <../fastq>` produced by
           Solexa (Ga IIx) sequencers.

    .. include:: ../optionsSet/outputformat.txt

    .. include:: ../optionsSet/defaultoptions.txt
   
