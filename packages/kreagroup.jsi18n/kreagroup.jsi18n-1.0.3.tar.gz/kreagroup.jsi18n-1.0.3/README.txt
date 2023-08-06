Introduction
============

This packages makes it possible to have i18n in JavaScript via the
locales-directory. It is based on jarn.jsi18n and extends jarn.jsi18n (so it
needs jarn.jsi18n to work).


Usage
=====

This package is used in exactly the same manner as jarn.jsi18n, so if
you want to know how to use kreagroup.jsi18n, visit
http://pypi.python.org/pypi/jarn.jsi18n


Why this package?
=================

jarn.jsi18n and kreagroup.jsi18n do differ... You can use the packages in
the same way, but the result will differ in one particular case...

Suppose we run the following code in a browser, for the first time:

    > jarn.i18n.loadCatalog('plone', 'es');

    > _es = jarn.i18n.MessageFactory('plone', 'es');

    > _es('Contributor');

    "Contribuyente"

In line 1, jarn.jsi18n will download the i18n catalog in an ASYNCHRONOUS
way. While the i18n catalog is loading, it will run line 2 and 3, so
'Contributor' will be translated while the i18n catalog is not loaded. Because
the i18n catalog is not loaded, _es('Contributor') will not be translated and
just return the input. Here, the result will be 'Contributor', not "Contribuyente".
The next time we run the same code, chances are big that the download of the
i18n catalog is completed, so it will be in browser cache (no need to download
now), and the translation will executed correctly.

On the other hand...
In line 1, kreagroup.jsi18n loads the i18n catalog SYNCHRONOUS, so it waits
until the i18n catalog is loaded. When this is finished, it starts executing
line 2 and 3 and will translate correctly, because the i18n catalog is
already downloaded.


jarn.jsi18n vs kreagroup.jsi18n, a matter of taste...
=====================================================

jarn.jsi18n is more responsive, by only using asynchronous ajax calls. This comes 
with a penalty of no translation the first time the code is run...

kreagroup.jsi18n does always translate correctly. This comes with a penalty of a 
synchronous ajax call, which means you have to wait a little longer before the 
page loads the first time, which is less responsive...


Bonus
=====

jarn.jsi18n-1.0 does not work with Internet Explorer 8. kreagroup.jsi18n
contains a fix so translation do work in Internet Explorer 8. Probably,
jarn.jsi18n-1.1 will also contain this fix :-)


