Introduction
============

This utility product contains tools to allow out-of-context navigation.

Plone provides a strongly opinionated way to navigate your contents. Everything is based on object containment.
For example navigation portlets and breadcrumbs show contents using that criterion.
Sometimes it can be useful to choose a different way to navigate your contents.

Example 1:
A certain content is intended to be just a part of a bigger content. For example an image that doesn't make sense alone, but is shown in a slideshow (redomino.tabsandslides).
In this case this product allows to redirect to the parent (for non editors).

Example 2:
You use an internal link to jump to a different part of the web site but the user should be able to get back to the previous content.
In this case, marking the link with a class, a link to the previous page would appear.

Redirect to parent
==================
This product adds a special interface "redomino.redirectparent.interface.IRedirectToParent". Objects with this interface will redirect to the parent when accessed by non editor users.
You can add the interface using the "manage_interfaces" view.

Hidden folder
=============
This is a new content type intended to be hidden. It can be useful if you don't want users to directly navigate on a certain folder containing public objects.
This folder is not searchable, navigable and will redirect to the parent when accessed directly.

Link with backreference
=======================
When the relatesToUID class is used on an internal link the target view will contain a link to the previous content.	

