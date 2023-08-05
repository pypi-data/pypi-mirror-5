README for collective.sliderfields
===================================

This product simply add a Dexterity Behavior and Archetypes SchemaExtender
components which provides these 3 fields:

* Slider Image
* Slider Title
* Slider Description

It does not do anything more than that. Purpose of this product is to aid in
development of an easy to use custom slider related addons in Plone without
having to manage separate contents for slider and its related objects.

All objects with this functionality enabled will have a marker interface
ISliderFieldsEnabled so that they can be easily queried through catalog (eg: in
ObjPathSourceBinder queries).

Enabling Behavior
------------------

Follow the normal steps for assigning behavior to a Dexterity content type

Enabling SchemaExtender
-----------------------

Mark the content type with ISliderFieldsEnabled. One method to mark existing
types is to use ZCML::

    <class class="Products.ATContentTypes.content.link.ATLink">
       <implements interface="collective.sliderfields.interfaces.ISliderFieldsEnabled"/>
    </class>


Notes
=======

This product was developed on top of inigo.templer
(http://github.com/inigoconsulting/inigo.templer) template. 
