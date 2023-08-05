.. contents:: **Table of contents**

Introduction
============

Add some configuration to your Plone site for sending e-mail notifications when
new discussions or replies are added to `Ploneboard`__ forums.

__ http://pypi.python.org/pypi/Products.Ploneboard

This product can be useful in a Plone site where you have a lot of forums or forums are
one of the main content.

How to use
==========

After installation, go the "*Plone Configuration*" panel and access the new
"*Ploneboard notification system*" section.

.. image:: http://keul.it/images/plone/Products.PloneboardNotify-0.5.0-01.png
   :alt: Ploneboard notifications section

General settings
----------------

When configured, general setting are applied to all forums inside every message board (this
is also applied to forums outside any message board, a configuration you can manually obtain
from Ploneboard).

Follow a list of available options

**Send to all?**
    If you check this, a mail will be sent to every user of the site.
**Recipients**
    A list of recipients. Recipients can be **site members**, **groups** (so an e-mail will
    be sent to users inside those groups) or e-mail address.
    
    For every entry in this list, you can add a ``|bcc`` suffix to **send messages using BCC** to
    one or more user/group/address.

Local configuration for forums
------------------------------

From the form above you can quick access any other forum inside the site, from the
"*Local configuration for forums*" section.

.. image:: http://keul.it/images/plone/Products.PloneboardNotify-0.5.0-02.png
   :alt: Ploneboard notifications section

From there you can apply the same configurations above to a single forum.

The general rule is: "General settings" are applied to any forum, excluded forums where you
add a local configuration.

Hidden features
---------------

Accessing ZMI, you can go to a ``ploneboard_notify_properties`` inside the ``portal_properties``
tool. **Note**: this mess will probably change in future releases.

``msg_subject``
    Mail subject. If empty, "*New comment added on the forum:*" plus the forum name will be used.
``msg_from``
    Part of the mail message that identify who sent the message.
    If empty "*Message added by:*" plus the user name will be used.
``msg_argument``
    Suffix for the forum argument (the main discussion title). If empty, "*Argument is:*" plus
    the title will be used.
``msg_mess``
    Introduction to the new comment text. If empty, "*The new message is:*" plus the whole
    comment text will be used.

TODO
====

* Provide a way to manipulate the notification message format
* No more ZMI needs or ``|bcc`` suffix: switch to Plone registry
* Make the sender configurable globally, for single forum, etc
* Notification messages to local roles (see `#1`__)
* Current version support global configuration and forum specific ones; the long-term
  plan wanna reach also forum area configurations
* A complete, clean uninstall procedure that remove all unwanted stuff

__ http://plone.org/products/ploneboardnotify/issues/1

Requirements
============

* Plone 4.2 (Ploneboard 3.3)
* Plone 4.3 (Ploneboard 3.4)

Other older Plone 4 should works also.

Contributors
============

* Nicolas Laurance
* Alison Taylder
* `RedTurtle Technology`__
* `Makina Corpus`__

__ http://www.redturtle.it/
__ http://www.makina-corpus.com/

