===========
WikiUtils
===========

WikiUtils provide some utility classes to handle wiki pages.

Usage (retrieving a wiki page by title):

    #!/usr/bin/env python
    from python.turnguard.com.wikiutils import WikiUtils
    
    wu = WikiUtils()
    try:
        page = wu.getWikiPage(wikititle="Python_(programming_language)")
        for l in page.getLinks():
            print l
    except urllib2.HTTPError, e:
        if e.code == 404:
            print "WikiPage not found"
        
Usage (retrieving a wiki page by url):

    #!/usr/bin/env python
    from python.turnguard.com.wikiutils import WikiUtils

    wu = WikiUtils()
    try:
        page = wu.getWikiPage(wikiurl="http://en.wikipedia.org/wiki/Python_(programming_language)")
        for l in page.getLinks():
            print l
    except urllib2.HTTPError, e:
        if e.code == 404:
            print "WikiPage not found"


Caching
=========

WikiUtils will use .cache directory in the user's home
to create a cache of downloaded pages and retrieve 
the contents from the cache by default.
The full path of the WikiUtils cache is determined by
path = expanduser('~')+"/.cache/python/turnguard/com/wikiutils/"

If you do not want to use the caching system use
getWikiPage(caching=False,...)

