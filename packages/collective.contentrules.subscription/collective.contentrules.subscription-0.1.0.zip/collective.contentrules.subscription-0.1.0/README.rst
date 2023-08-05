
This product will add to Plone a new content rule, similar to the default "Send an email" ones, but email recipients are taken from a list of addresses that are subscribed for that rule.

Use-case
========

We want to notify about some updated of the site, and we want to allows users to subscribe or not to these notifications automatically.

We can do this with a contentrule registered for some object creation, and use our new action to send emails.

.. contents::

Setting up the rule
===================

This product provides a new rule action to connect with base Plone rules. When you create a new action, you need to fill some fields:

``Subject``
    The e-mail subject. You can place inside this text some markers.
``Sender email``
    The sender of the e-mail. If empty, will be automatically used the one set in portal mail settings.

``Message``
    The body text of the e-mail that will be sent. The text is the same for all section where
    the rule is activated on.
    
    You can place inside this text some markers.

The list of markes is shown at the bottom of action's edit form.

Rule subscription
=================
As we said previously, site managers can create some rules, and users (also anonymous users) can choose which rules subscribes to.

To do this, there is a simple form created with z3c.form that shows all available rules with our custom action.

The form is available at "*http://site_url/@@notify-subscribe*"

.. image:: http://blog.redturtle.it/pypi-images/collective.contentrules.subscription/subscribe_rules.png/

If the user is authenticated and have an email address, email field is automatically filled.

There is also an anti-spam check made with `collective.z3cform.norobots <https://pypi.python.org/pypi/collective.z3cform.norobots>`_.

Subscriptions overwiew
======================

There is also an overview controlpanel for site administrators that shows all rule subscriptions and allows to remove some addresses.

This view is available from Plone controlpanel or at "*http://site_url/@@contentrules-subscription-controlpanel*"

.. image:: http://blog.redturtle.it/pypi-images/collective.contentrules.subscription/rules_controlpanel.png

To-do
=====
* Allow users to unsubscribe
* Improve subscription security using some confirm machinery

Requirements
============

This product has been tested on:

* Plone 4.0
* Plone 4.1
* Plone 4.2
* Plone 4.3

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/