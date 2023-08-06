=================
dolmen.app.layout
=================

`dolmen.app.layout` provides ready-to-use components to get a fully
functional and extensively pluggable User Interface for a Dolmen
application (see `dolmen.app.site`).


About Dolmen
============

Dolmen is an application development framework based on Grok and ZTK
which also provides a CMS (Content Management System) out of the
box. Dolmen is being made with four main objectives in mind: easily
pluggable, rock solid and fast content type development, readability
and speed.


Getting started
===============

We import all the needed dependencies of the tests::

  >>> from dolmen import content
  >>> from grokcore.component import testing
  >>> from zope.site.hooks import getSite
  >>> from zope.component import getMultiAdapter 
  >>> from zope.publisher.browser import TestRequest
   
We import everything needed for the API verification::

  >>> from zope.interface import verify
  >>> from dolmen.app.layout import interfaces as API
 
We define and intanciate a Context object and a request for our tests
to come::

  >>> class Mammoth(content.Content):
  ...    content.name(u'Furry Mammoth')

  >>> testing.grok_component('mammoth', Mammoth)
  True

  >>> root = getSite()
  >>> root['manfred'] = Mammoth()
  >>> manfred = root['manfred']

  >>> request = TestRequest()


Global interface
================
  
  >>> from dolmen.app.layout import master

  >>> API.IGlobalUI.extends(API.IContentProviders)
  True

  >>> API.IGlobalUI.providedBy(master)
  True
  >>> verify.verifyObject(API.IGlobalUI, master)
  True


Content providers
-----------------
 
Description
~~~~~~~~~~~

  >>> for name, attr in API.IContentProviders.namesAndDescriptions():
  ...   print "%s: %s" % (name, attr.getDoc())
  Footer: Viewlet manager for the bottom part of the body.
  AboveBody: Viewlet manager located above the main content.
  BelowBody: Viewlet manager located below the main content.
  Header: Viewlet manager involved in rendering the HTML head.
  Top: Viewlet manager for the top part of the body.
  Resources: Viewlet manager including resources.


Layout
------

Description
~~~~~~~~~~~

  >>> interfaceDescription(API.IGlobalUI)
  Master: Base layout using all the `IContentProviders` components to build a coherent yet overridable rendering.


Contextual UI
=============

  >>> from dolmen.app.layout import viewlets

  >>> API.IContextualUI.providedBy(viewlets)
  True
  >>> verify.verifyObject(API.IContextualUI, viewlets)
  True

Description
-----------

  >>> interfaceDescription(API.IContextualUI)
  ContextualActions: Viewlet rendering contextual actions.
  FlashMessages: Viewlet displaying site-wide messages.


View components
===============

  >>> from dolmen.app.layout import models

Models
------

Models are base classes to be used in your own
classes. `dolmen.app.layout` provides a collections of ready-to-use
models::

  >>> API.IModels.providedBy(models)
  True
  >>> verify.verifyObject(API.IModels, models)
  True

Description
~~~~~~~~~~~

  >>> interfaceDescription(API.IModels)
  Index: Page showing as default view on an object.
  Form: Generic page form.
  Page: Page embedded in a layout.

Default views
-------------

`dolmen.app.layout` registers some views, out-of-the-box, to allow you
to interact with your `dolmen.content` objects and your application::

  >>> API.IBaseViews.providedBy(models)
  True
  >>> verify.verifyObject(API.IBaseViews, models)
  True

Description
~~~~~~~~~~~

  >>> interfaceDescription(API.IBaseViews)
  Edit: Default edit form.
  Add: Default add form.
  DefaultView: Display form used as index.
  Delete: Default delete form.

Query
~~~~~

We can now test to see if our default views are retrieved::

  >>> view = getMultiAdapter((manfred, request), name="index")
  >>> view
  <dolmen.app.layout.models.DefaultView object at ...>

  >>> edit = getMultiAdapter((manfred, request), name="edit")
  >>> edit
  <dolmen.app.layout.models.Edit object at ...>

The add form is a bit different, as it relies on an adding view (see
`dolmen.forms.crud` and `dolmen.content` for more information)::

  >>> from dolmen.forms.crud import Adder

  >>> adding = Adder(root, request)
  >>> adding
  <dolmen.forms.crud.addview.Adder object at ...>

  >>> adding.traverse("dolmen.app.layout.Mammoth", None)
  <dolmen.app.layout.models.Add object at ...>


Skins
=====

`dolmen.app.layout` provides a browser layer and a skin, to serve as a
base component for your own skins::

  >>> from dolmen.app.layout import skin

  >>> API.ISkin.providedBy(skin)
  True
  >>> verify.verifyObject(API.ISkin, skin)
  True

Description
-----------

  >>> interfaceDescription(API.ISkin)
  IBaseSkin: Skin providing the IBaseLayer. Can be applied directly or inherited.
  IBaseLayer: Layer used to register all the Dolmen centric view components.
  Resource: Viewlet component used to include resources


Menus
=====

  >>> from dolmen.app.layout import menus

  >>> API.IMenus.providedBy(menus)
  True
  >>> verify.verifyObject(API.IMenus, menus)
  True

Description
-----------

  >>> interfaceDescription(API.IMenus)
  ContextualMenu: Menu defining contextual actions.
  MenuViewlet: Generic viewlet rendering a `IBrowserMenu`.

Contextual menu
---------------

  >>> manager = master.Top(manfred, request, view)
  >>> manager
  <dolmen.app.layout.master.Top object at ...>

  >>> manager.update()
  >>> print manager.render()
  <dl id="contextual-actions" class="menu">
    <dt>Contextual actions</dt>
    <dd>
      <ul>
        <li class="selected entry">
  	  <a title="View">View</a>
        </li>
        <li class="entry">
    	  <a href="http://127.0.0.1/manfred/edit" title="Edit">Edit</a>
        </li>
        <li class="entry">
    	  <a href="http://127.0.0.1/manfred/delete" title="Delete">Delete</a>
        </li>
      </ul>
    </dd>
  </dl>


Credits
=======

All Dolmen packages are sponsorised by NPAI (http://www.npai.fr)
