VU - 0.1.1
==========

**VU** is a small service that helps you to check the health of your services on the web.
On a single web page, you can check that : 

 * All your favorite sites are alive
 * All your jenkins build are green
 * All your supervisor processes are running


This is experimental, the documentation, packing, and setup instructions are coming soon. 


Installation
============

`python setup.py install`

(It will install also tornado.)


Configuration file
==================

Simply create a file `vu.cfg` : 

    [checker:Google]
    type = url
    url = http://google.com

    [checker:My site]
    type = url
    url = http://mysupersite.com

    [checker:My private site with http auth]
    type = url
    url = http://admin.mysupersite.com
    http_user = admin
    http_password = mypassword


Then run `vu -c vu.cfg -p 8888` and check http://127.0.1.1:8888/


In progress
===========

It aims to be a personnal helper, there are 0 feature and bad performances. 
I told you.


LICENCE
-------


    The MIT License (MIT)

    Copyright (c) 2013 Martyn CLEMENT

    Permission is hereby granted, free of charge, to any person obtaining a copy of
    this software and associated documentation files (the "Software"), to deal in
    the Software without restriction, including without limitation the rights to
    use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
    the Software, and to permit persons to whom the Software is furnished to do so,
    subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
    FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
    COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
    IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
    CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

