Welcome! 

    XMLTransformer allows you to transform XML content to HTML using XSLT.
    The XML and XSLT content can be loaded by either an uploaded file or
    an URL specified in the configuration.

    For the transformation to be successful you need to tell the product
    which source shall be used for both documents (URL, file).

    Enabling caching may result in higher speed when displaying the web site.
    The cache time field allows you to expire the cache after a certain 
    number of seconds. The cache will be rewritten after the next hit of the
    page and the search index will be updated as well.

   Parameters allow you to pass parameters to the retrieved URL and to the
   XSLT stylesheet.
   Specifiy one key=value pair per line.
   Additionaly parameters can also be read from GET values of the current
   page as follows: key=GET_paramname. The variable key then gets assigned
   the value of the GET parameter paramname.
   Python expressions can also be used as parameter values when using the 
   following syntax: var=python:PYTHONEXPR, i.e. 
   currentyear=python:__import__('datetime').datetime.now().year

Any further questions may be adressed to 

   Dr. Christoph Hermann
   IT-Unternehmensberatung
   E-Mail: info@drhermann.de
   Web: http://drhermann.de 

