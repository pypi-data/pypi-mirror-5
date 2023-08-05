Introduction
============

``collective.chat.xmpp`` provides instant messaging for `Plone`_. It uses the
`XMPP`_ protocol and requires an XMPP server (such as `ejabberd`_) for the message handling.

Features
========

* Manually or automatically subscribe to other users.
* With manual roster subscriptions, you can accept or decline contact requests.
* Chat statuses (online, busy, away, offline)
* Custom status message
* Typing notifications (i.e when the contact is typing)
* Third person messages (/me )
* Multi-user chat in chatrooms
* Topics can be set for chatrooms
* Full name and profile picture support

Installation
============

XMPP integration with Plone is provided by the `collective.xmpp.core`_ package.
Please refer to its README on how to set it up.

You can use the buildout at `collective.xmpp.buildout`_.

The buildout in this egg is used for development purposes.

You'll need to have a working XMPP server and access to the
administration account on the server.

Your XMPP server will have to support the following extensions

* `XEP-0045`_ Multi-user Chat
* `XEP-0071`_ XHTML-IM.
* `XEP-0144`_ Roster Item Exchange.
* `XEP-0124`_ Bidirectional-streams Over Synchronous HTTP (BOSH)
* `XEP-0206`_ XMPP over BOSH

Configuration
=============

You'll need to have an administrator account on the Jabber server you'll be
using. Refer to the `collective.xmpp.core`_ README for information on how to
set this up.

Once you've installed ``collective.xmpp.chat``, you should go to the Plone
registry in the control panel and set the ``XMPP Domain`` as well as the ``XMPP
Admin JID`` and ``XMPP Admin Password`` values.

Additionally you have the option ``Auto-subscribe XMPP users``, which is
disabled by default.

Enable this option if you don't want your users to manually maintain their
rosters (i.e subscribing and unsubscribing to one another) and would rather
have everyone subscribe to everyone else. Be careful however, this might cause
a lot of overhead (and therefore be quite slow) on sites with large userbases.

Important details for developers
================================

Since  `a recent commit`_ this package now makes
use of a git submodule (specifically the the ./browser/resources dir).

Once you have cloned this repo, you need to run two commands:

  ::

    git submodule init
    git submodule update

If you need to make changes under the submodule (aka ./browser/resources dir)
best practice will be to fork https://github.com/jcbrand/converse.js under
your account then:

  ::

   cd ./browser/resources
   git remote set-url origin git@github.com:MYACCOUNT/converse.js.git
   git commit -a
   git push

After this you can send a pull request with your changes.
For more information on submodules and how to work with them, `refer to the git book`_.

.. _`XEP-0045`: http://xmpp.org/extensions/xep-0045.html
.. _`XEP-0071`: http://xmpp.org/extensions/xep-0071.html
.. _`XEP-0144`: http://xmpp.org/extensions/xep-0144.html
.. _`XEP-0124`: http://xmpp.org/extensions/xep-0124.html
.. _`XEP-0206`: http://xmpp.org/extensions/xep-0206.html
.. _`collective.xmpp.core`: http://github.com/collective/collective.xmpp.core
.. _`collective.xmpp.buildout`: http://github.com/collective/collective.xmpp.buildout
.. _`a recent commit`: https://github.com/collective/collective.xmpp.chat/commit/a6f41258b55709fd734d5f432d42d6f04d61d538
.. _`refer to the git book`: http://git-scm.com/book/en/Git-Tools-Submodules
.. _`Plone`: http://plone.org
.. _`XMPP`: http://xmpp.org
.. _`ejabberd`: http://ejabberd.im
