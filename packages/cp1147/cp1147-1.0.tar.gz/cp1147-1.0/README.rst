==================================
IBM1147 french EBCDIC (euro) codec
==================================        
**This package contains cp1147 EBCDIC french codec.**
  
About cp1147
============
 I have files coded IBM1147 (EBCDIC french + euro sign), I was forced to write my own codec ``cp1147``, very close  to the ``cp500`` (Canada, Belgium), it diverges on the characters "@\°{}§ùµ£à[€`¨#]~éè¦ç" :

 ::

    import cp1147
    print "euro sign ?",chr(159).decode('cp1147')
    print ''.join([ chr(i).decode('cp1147') + " <=> " + chr(i).decode('cp500') + "\n" for i in range(0,256)
              if chr(i).decode('cp1147') != chr(i).decode('cp500')])

Changelog
=========
 1.0 - (2012-11-12) 
 Initial release.
         
  - cp1147_search_function now return "codecs.CodecInfo" object





