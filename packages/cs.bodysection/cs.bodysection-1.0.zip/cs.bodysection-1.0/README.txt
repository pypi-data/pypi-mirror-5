Introduction
============

After the INavigationRoot fixes in previous versions of Plone, if you install
LinguaPlone 4.x in Plone 4.x you will end having section-es, section-en, and so
on in your site.

That's because LinguaPlone 4.x adds root folder for each language in your site 
and sets them INavigationRoot interface.

In some projects you need content-based section identifiers for your body to get 
them styled property by your designer.

That's what you get with this small products. It just have a browser view with 
one method. Add it to your main_template in this way::

<body tal:define="isRTL portal_state/is_rtl;
                  sl python:plone_view.have_portlets('plone.leftcolumn', view);
                  sr python:plone_view.have_portlets('plone.rightcolumn', view);
                  root_content context/@@navigation_root_content;
                  body_content_class root_content/section_content_body_class;
                  body_class python:plone_view.bodyClass(template, view) + ' ' + body_content_class;
                  sunburst_view python:context.restrictedTraverse('@@sunburstview')"

In this way your body tag will have an extra content-section-your-items-id class
and yet preserve the section-es (or the one for your language).

Useful? It is useful for us :)

Use 
----

Add it to your buildout::

 eggs = 
      ...
      cs.bodysection
      
And run buildout. No need to install it. 
