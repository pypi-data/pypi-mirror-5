Use of PloneboardNotify
=======================

We need to setup something before this file can became a real and working browser test for Plone.

>>> from Products.Five.testbrowser import Browser
>>> browser = Browser()
>>> portal_url = self.portal.absolute_url()
>>> self.portal.error_log._ignored_exceptions = ()
>>> browser.handleErrors = False
>>> from Products.PloneTestCase.setup import portal_owner, default_password

Configuration
-------------

To test later e-mail system, we put the notification in *debug mode*, so no real mail will be sent
but only printed to standard output.

>>> self.portal.portal_properties.ploneboard_notify_properties.debug_mode = True

Now we are ready to load the Plone site where the product is installed.
We need to login before beeing able to start with creation of a forum.

>>> browser.open(portal_url+'/login_form')
>>> browser.getControl('Login Name').value = 'root'
>>> browser.getControl('Password').value = 'secret'
>>> browser.getControl('Log in').click()
>>> 'You are now logged in' in browser.contents
True

Let's create our first forum area.

>>> browser.open(portal_url)
>>> browser.getLink('Message Board').click()
>>> browser.getControl('Title').value = 'Our forums'
>>> browser.getControl('Save').click()
>>> browser.url == portal_url+'/our-forums'
True

Inside the *Message Board* we can add multiple forums. We start with one for now.

>>> browser.getLink('Add new…').click()
>>> browser.getControl('Forum').click()
>>> browser.getControl('Add').click()
>>> browser.getControl('Title').value = 'Cool Music'
>>> browser.getControl('Save').click()
>>> portal_url+'/our-forums/cool-music' in browser.url
True

Now we can go to the "*Ploneboard notification system*".

>>> browser.open(portal_url+'/@@ploneboard_notification')
>>> 'Ploneboard notifications' in browser.contents
True

To begin our tests we set a couple of e-mail address in the "Recipients" section. We can use here
the "*|bcc*" decoration after every value, to add the message to this recipients in *BCC*. 

>>> browser.getControl('Recipients').value = """usera@mysite.org
... userb@mysite.org
... userc@mysite.org|bcc"""
>>> browser.getControl('Save').click()

We used the "*General notify configuration*" section, so an e-mail will be delivered to all address
at every new message or discussion everywhere in the site. The last address is used for *BCC* section.

Using Ploneboard
----------------

Now we can go back to our forum and begin a new discussion.

>>> browser.open(portal_url+'/our-forums/cool-music')
>>> browser.getControl('Start a new Conversation').click()
>>> browser.getControl('Title').value = 'Discussion 1'
>>> browser.getControl('Body text').value = '<p>The <strong>cat</strong> is on the table</p>'

As soon as we confirm the post, an e-mail will be generated.

>>> browser.getControl(name='form.button.Post').click()
Message subject: New comment added on the forum: Cool Music
Message text:
<html>
<body>
<p>Message added by: The Admin</p>
<BLANKLINE>
<p>Argument is: Discussion 1</p>
<p>The new message is:</p>
<p>The <strong>cat</strong> is on the table</p>
<BLANKLINE>
<hr/>
<p><a href="http://nohost/plone/our-forums/cool-music/...">http://nohost/plone/our-forums/cool-music/...</a></p>
</body>
</html>
<BLANKLINE>
Message sent to userb@mysite.org, usera@mysite.org (and to userc@mysite.org in bcc)

A similar message will be delivered also if the user add a response to an existing discussion.
First we need to go to the discussion itself, after that we can use the "Reply to this" command.

>>> browser.getLink('Discussion 1').click()
>>> browser.getControl('Reply to this', index=0).click()

Ploneabord quote text inserted before when replying, so we keep the text and add a new comment.

>>> browser.getControl('Body text').value = browser.getControl('Body text').value + \
...                                         "\n<p>I don't think so. He is <em>under</em> it</p>"

Now posting this will generate a new e-mail.

>>> browser.getControl('Post comment').click()
Message subject: New comment added on the forum: Cool Music
Message text:
<html>
<body>
<p>Message added by: The Admin</p>
<BLANKLINE>
<p>Argument is: Discussion 1</p>
<p>The new message is:</p>
...
<p>I don't think so. He is <em>under</em> it</p>
<BLANKLINE>
<hr/>
<p><a href="http://nohost/plone/our-forums/cool-music/...">http://nohost/plone/our-forums/cool-music/...</a></p>
</body>
</html>
<BLANKLINE>
Message sent to userb@mysite.org, usera@mysite.org (and to userc@mysite.org in bcc)

The e-mail structure is the same (the quoted text is optional as the commenter can remove it).

Use properties to customize strings in notification messages 
------------------------------------------------------------
You can put your own message strings in portal_properties/ploneboard_notify_properties to customize the strings. 
If one of this fields is not empty it will be used to override the default string.

We put some custom strings in the properties.

>>> self.portal.portal_properties.ploneboard_notify_properties.msg_subject = 'CUSTOM:New comment added on the forum: '
>>> self.portal.portal_properties.ploneboard_notify_properties.msg_from = 'CUSTOM:Message added by: '
>>> self.portal.portal_properties.ploneboard_notify_properties.msg_argument = 'CUSTOM:Argument is: '
>>> self.portal.portal_properties.ploneboard_notify_properties.msg_mess = 'CUSTOM:The new message is:'

Now we can use the "Reply to this" command to test these change.
     
>>> browser.getControl('Reply to this', index=0).click()    
    
We add a new comment.
    
>>> browser.getControl('Body text').value = browser.getControl('Body text').value + \
...                                         "\n<p>We have custom strings in notifications.</p>"

Now posting this will generate a new e-mail.

>>> browser.getControl('Post comment').click()
Message subject: CUSTOM:New comment added on the forum: Cool Music
Message text:
<html>
<body>
<p>CUSTOM:Message added by: The Admin</p>
<BLANKLINE>
<p>CUSTOM:Argument is: Discussion 1</p>
<p>CUSTOM:The new message is:</p>
...
<p>We have custom strings in notifications.</p>
<BLANKLINE>
<hr/>
<p><a href="http://nohost/plone/our-forums/cool-music/...">http://nohost/plone/our-forums/cool-music/...</a></p>
</body>
</html>
<BLANKLINE>
Message sent to userb@mysite.org, usera@mysite.org (and to userc@mysite.org in bcc)

Here we have the same structure as befor but different message strings.

We can now restore the old format.

>>> self.portal.portal_properties.ploneboard_notify_properties.msg_subject = 'New comment added on the forum: '
>>> self.portal.portal_properties.ploneboard_notify_properties.msg_from = 'Message added by: '
>>> self.portal.portal_properties.ploneboard_notify_properties.msg_argument = 'Argument is: '
>>> self.portal.portal_properties.ploneboard_notify_properties.msg_mess = 'The new message is:'

Play with users (or groups) of the portal
-----------------------------------------

PloneboardNotify can also use e-mail address taken from the portal users. Use of e-mail address or user ids
can be combined, also with the *BCC* feature.

Let's we change something in the configuration.

>>> browser.open(portal_url+'/@@ploneboard_notification')
>>> browser.getControl('Recipients').value = """usera@mysite.org
... root|bcc
... member"""
>>> browser.getControl('Save').click()

We added the *root* user in *BCC* and also another simple member (called *member*). To test this we can
go back to our forum and add another conversation.

>>> browser.open(portal_url+'/our-forums/cool-music')
>>> browser.getControl('Start a new Conversation').click()
>>> browser.getControl('Title').value = 'Discussion 2'
>>> browser.getControl('Body text').value = '<p>I will not fear</p>'

Let's see what result will be generated.

>>> browser.getControl(name='form.button.Post').click()
Message subject: New comment added on the forum: Cool Music
Message text:
<html>
<body>
<p>Message added by: The Admin</p>
<BLANKLINE>
<p>Argument is: Discussion 2</p>
<p>The new message is:</p>
<p>I will not fear</p>
<BLANKLINE>
<hr/>
<p><a href="http://nohost/plone/our-forums/cool-music/...">http://nohost/plone/our-forums/cool-music/...</a></p>
</body>
</html>
<BLANKLINE>
Message sent to user@mysite.org, usera@mysite.org (and to admin@mysite.org in bcc)

If you use groups in your Plone site you can also use group ids there, and the notification will be sent
to all users inside that group (and you can also user "*|bcc*" after the group name).

Another option available in the configuration panel is a control to send notification to *all* users of
the site. This can be very helpful if the site is mainly a forum resource (but can also became a nasty
spam source!).

For privacy reason, when using this feature all e-mail will be delivered using *BCC*.

>>> browser.open(portal_url+'/@@ploneboard_notification')
>>> browser.getControl('Send to all?').click()
>>> browser.getControl('Save').click()

To test what is changed right now we will add a response to the discussion above.

>>> browser.open(portal_url+'/our-forums/cool-music')
>>> browser.getLink('Discussion 2').click()
>>> browser.getControl('Reply to this', index=0).click()
>>> browser.getControl('Body text').value = "Fear is the mind-killer"
>>> browser.getControl('Post comment').click()
Message subject: New comment added on the forum: Cool Music
Message text:
<html>
<body>
<p>Message added by: The Admin</p>
<BLANKLINE>
<p>Argument is: Discussion 2</p>
<p>The new message is:</p>
Fear is the mind-killer
<BLANKLINE>
<hr/>
<p><a href="http://nohost/plone/our-forums/cool-music/...">http://nohost/plone/our-forums/cool-music/...</a></p>
</body>
</html>
<BLANKLINE>
Message sent to usera@mysite.org (and to admin@mysite.org, user@mysite.org, another@mysite.org in bcc)

Please note that the e-mail "*usera@mysite.org*" is still included as before.

Manage notification for a single forum
--------------------------------------

If our Plone site keep a lot of message boards and/or a lot of forums (even if inside the same board),
the global notification preference can be difficult to be managed.

Maybe we need to notify all users of the portal for a single (public) forum, but notify only some special
members for one or more private forums, and different forum may need different notification address
group...

All those needs can be reached configuring the notification also for a forum instead of using the global
notification setting we used.
In facts the global notification settings can be ignored and never used.

We can manage the per-forum configuration going back to the "Ploneboard notification" panel.

>>> browser.open(portal_url+'/@@ploneboard_notification')

There, we will see all message boards and all forums inside them. Forum that have already a local settings
are marked with a special image.

Let's change the notification settings adding a local preference for our "*Cool Music*" forum.

>>> browser.getLink('Cool Music').click()
>>> 'Ploneboard notifications - Cool Music' in browser.contents
True

The options there are the same used in global configuration. We can here change (and this time, only for
the "*Cool Music*" forum the notification settings.

Let's make this forum send notification only to a webmaster address.

>>> browser.getControl('Recipients').value = 'webmaster@mysite.org'
>>> browser.getControl('Save').click()
>>> browser.url == portal_url+"/our-forums/cool-music/@@ploneboard_notification"
True
>>> browser.getControl('Recipients').value
'webmaster@mysite.org'

Now we simply need to see what is changed, starting a new discussion inside our forum.

>>> browser.open(portal_url+'/our-forums/cool-music')
>>> browser.getControl('Start a new Conversation').click()
>>> browser.getControl('Title').value = "Talking to webmaster"
>>> browser.getControl('Body text').value = "<p>This will be sent only to Webmaster!</p>"
>>> browser.getControl(name='form.button.Post').click()
Message subject: New comment added on the forum: Cool Music
Message text:
<html>
<body>
<p>Message added by: The Admin</p>
<BLANKLINE>
<p>Argument is: Talking to webmaster</p>
<p>The new message is:</p>
<p>This will be sent only to Webmaster!</p>
<BLANKLINE>
<hr/>
<p><a href="http://nohost/plone/our-forums/cool-music/...">http://nohost/plone/our-forums/cool-music/...</a></p>
</body>
</html>
<BLANKLINE>
Message sent to webmaster@mysite.org (and to no-one in bcc)

We can see that no global setting has been taken there. This forum now lives on his own.

Handle Kupu/TinyMCE internal links
----------------------------------

When adding comments the forum users could take benefit from using a WYSIWYG editor like *Kupu* or
*TinyMCE*. When using Ploneboard the toolbar available is reduced, but the feature of making internal
link is there.

The problem: when sending the e-mail to the recipients the URL of links generated will be broken because
we will find *relative links*, working perfectly when you visit the discussion from the Plone site itself.

PloneboardNotify will manage this, changing the internal links inside the message. This will be done only
for HTML *<a>* elements using the CSS class "*internal-link*".

Let's test this adding a new discussion.

>>> browser.open(portal_url+'/our-forums/cool-music')
>>> browser.getControl('Start a new Conversation').click()
>>> browser.getControl('Title').value = "Please visit this link!"
>>> browser.getControl('Body text').value = """Please, visit <a title="News" class="internal-link" href="../our-forums/cool-music/news">this</a>."""
>>> browser.getControl(name='form.button.Post').click()
Message subject: New comment added on the forum: Cool Music
Message text:
<html>
<body>
<p>Message added by: The Admin</p>
<BLANKLINE>
<p>Argument is: Please visit this link!</p>
<p>The new message is:</p>
Please, visit <a title="News" class="internal-link" href="http://nohost/plone/our-forums/cool-music/.../../our-forums/cool-music/news">this</a>.
<BLANKLINE>
<hr/>
<p><a href="http://nohost/plone/our-forums/cool-music/...">http://nohost/plone/our-forums/cool-music/...</a></p>
</body>
</html>
<BLANKLINE>
Message sent to webmaster@mysite.org (and to no-one in bcc)

As we can see, the relative link is keepd but the absolute portal url is added before it.

Forums not inside message board
-------------------------------

Another not very popular Ploneboard feature is that is possible to enable the forum use also outside
message boards, making it addable globally where we want.

Commonly this behaviour must be enabled through ZMI access, using the *portal_types* tools.

>>> browser.open(portal_url)
>>> browser.getLink("Forum")
Traceback (most recent call last):
...
LinkNotFoundError
>>> self.enableForumGlobally()
>>> browser.open(portal_url)
>>> browser.getLink("Forum").click()
>>> browser.getControl('Title').value = 'Lonely messages'
>>> browser.getControl('Save').click()
>>> portal_url+'/lonely-messages' in browser.url
True

Now that we have a forum inside the portal root, let's go to see how this is handled by the configuration
area.

>>> browser.open(portal_url+'/@@ploneboard_notification')
>>> 'Orphan forums' in browser.contents
True
>>> browser.getLink("Lonely messages", url='@@ploneboard_notification').click()
>>> 'Ploneboard notifications - Lonely messages' in browser.contents
True

So those forums are put under the *Orphan forums* section at the end of the list. After this they are
usable and configurable like all other forums.
