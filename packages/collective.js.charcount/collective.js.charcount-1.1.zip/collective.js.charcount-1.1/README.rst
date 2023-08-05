*************************
collective.js.charcount
*************************

.. contents:: Table of Contents


Overview
=========

jQuery plugin Simplest Twitterlike dynamic character count for textareas and
input fields.


About charCount
================

The first thing that this plugin do is create a sibling element (it adds is
immediately AFTER the form element), the "counter", where the remaining
character info is stored. On each key up event or text field value change the
counting function is triggered and the contents of this "counter" element is
changed accordingly. If the remaining character count reaches the "warning"
zone (gets close to zero) the CSS class is added. We use this class to change
the color of the character count info. If the count reaches zero and goes beyond
it another class is added so we can use another style for exceeding the limit.

Just so you can find your way around it, this is the code that the plugin generates
by default::

    <span class="counter">140</span>


Plugin Options (and default values)
=====================================

limit: 140
------------
The character limit you wish to set for your text area or input field. It must be
a number.

warning: 25
------------
When remaining characters reach the number set with this option the "warning" css
class name will be applied to the counter element.

counterElement: 'span'
----------------------- 
The type of element you wish to choose as your "counter" element. By default it is
a SPAN element, but you can use paragraphs, divs, strongs, ems…

css: 'counter'
---------------
Class name added to the counter element. Use this class name as a css selector to
describe element’s appearance.

cssWarning: 'warning'
----------------------
Class name added to the counter element once the character count reaches the "warning"
number.

cssExceeded: 'exceeded'
------------------------
Class name added to the counter element once the character count reaches zero.

counterText: ''
---------------
If you wish to add some text before the remaining character number, you can do so by
using this option. It is empty by default.

Here’s what default usage code looks like::

    $("#message1").charCount();

…and this is the plugin usage with some customized options::

    $("#message2").charCount({
        allowed: 50,        
        warning: 20,
        counterText: 'Characters left: '    
    });


Also take a look at the CSS I used for my demos::

    form .counter{
        position:absolute;
        right:0;
        top:0;
        font-size:20px;
        font-weight:bold;
        color:#ccc;
    }
    form .warning{color:#600;}  
    form .exceeded{color:#e00;}

How to install
==============

This addon can be installed as any other Plone addon. Please follow official
documentation_.


After installing the package on your portal you can access the demo in:
http://youportal.com/++resource++collective.js.charcount.demo.html


.. _documentation: http://plone.org/documentation/kb/installing-add-ons-quick-how-to

Have an idea? Found a bug? Let us know by `opening a support ticket`_.

.. _`opening a support ticket`: https://github.com/collective/collective.js.charcount/issues


Mostly Harmless
---------------

.. image:: https://secure.travis-ci.org/collective/collective.js.charcount.png
    :target: http://travis-ci.org/collective/collective.js.charcount

