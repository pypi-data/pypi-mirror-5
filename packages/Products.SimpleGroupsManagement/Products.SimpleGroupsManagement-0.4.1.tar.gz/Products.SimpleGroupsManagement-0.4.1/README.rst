Introduction
============

Have you ever feel the need to give to normal (AKA: not Manager/Site Administrator ) Plone member the power to
manage a group?

Right now in Plone you can make this playing with the (**Plone Site Setup: Users and Groups**).
Even playing with this permission is impossible to limit the group on which a member (or group)
can manage.

This products and a minimal configuration, a member of the Plone portal (or all members in a group) will be
able to manage the users of a group, overriding the basic portal security.
You only need to go to the ``portal_properties`` tool of you portal and modifiy the new
**simple_groups_management_properties**.

In the ``sgm_data`` section you need to insert a set of strings like

::

    id1|group_id1
    id2|group_id2
    ...

where *id1*, *id2* can be user or group ids. This mean that those subjects will be able to act on groups.

You can also insert a list of groups ids that will be never handled by this product in the
``sgm_never_managed_groups`` section.

The utility also react to the **Add portal members** permission. If the current user has this permission
you will be able to add new portal members (so no security break for this).

When an user is added or removed, an event is notified.

Compatibility
-------------

Tested with Plone 4.2 and 4.3. Look for older releases if you need Plone 3 compatiblity.

Be aware!
=========

This products override all normal Plone permissions noted above! This can create **security black-holes** in
your portal!

.. figure:: http://keul.it/images/Black_Hole_Milkyway.jpg
   :scale: 50

The access to the new user/group management form is still protected by the *Use Simple Groups Management*
permission (commonly given to all site Members).

Similar products
================

Maybe is a good idea to check also `collective.groupdelegation`__

__ http://pypi.python.org/pypi/collective.groupdelegation

TODO
====

* Don't force the Manager to go in ZMI, but handle configuration from Plone UI.

Credits
=======

Special thanks to Albert Pallas for beeing the locales-man.
