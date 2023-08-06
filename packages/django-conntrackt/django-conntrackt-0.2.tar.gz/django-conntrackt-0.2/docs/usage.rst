.. Copyright (C) 2013 Branko Majic

   This file is part of Django Conntrackt documentation.

   This work is licensed under the Creative Commons Attribution-ShareAlike 3.0
   Unported License. To view a copy of this license, visit
   http://creativecommons.org/licenses/by-sa/3.0/ or send a letter to Creative
   Commons, 444 Castro Street, Suite 900, Mountain View, California, 94041, USA.


.. _usage:

Usage
=====

Django Conntrackt provides a very simple interface for reading and editing the
information about network connections across projects, as well as for obtaining
*iptables* rules.

Key concepts
------------

There is a couple of key concepts to be aware of throughout the documentation:

Project
    A project is used to group the related entities. Project usually maps to
    business projects being worked on by the organisation members.

Location
    Location is used to group the related entities within a project. Locations
    can be abstract, like *primary site*, *secondary site*, or *disaster
    site*. They can also be more specific, like *Belgrade*, or *Stockholm*. The
    layout of locations is completely up to the user of Conntrackt.

Entity
    Entity is an origin or destination of network communication. An entity can
    represent a single physical or virtual device (server, router, or some other
    network-capable device), or it can represent a subnet (therefore being
    mapped to multiple physical or virtual devices).

    Every entity must have an assigned project and location.

Interface
    Interface is used for representing a specific network interface on an
    entity. In regular case, where the entity is a physical or virtual device,
    an interface will map to a single IP address.

    An interface is also used to provide subnet information for entities that
    represent subnets.

    Entity can have more than one interface assigned to it.

Communication
    Communication is used to specify possible connections between entities. Each
    communication contains information about source interface (of a specific,
    source entity), destination interface (of a specific, target entity),
    protocol type (TCP, UDP, ICMP), and port number (or, in case of ICMP,
    package type).

    In addition to describing the various connections that happen between
    entities, communication information is also used for generating the
    *iptables* rules for servers.

Users and permissions
---------------------

Conntrackt employs standard Django permissions for object creation and
modification. This includes ability to *add*, *change*, and *delete* projects,
locations, entities, interfaces, and communications.

In addition to write-related permissions, Conntrackt also comes with a single
read permission that is used to restrict read access to Conntrackt data (**Can
view information**). This permission is required in order to allow the users to
view the projects, locations, entities, interfaces, and communications. This is
the minimal permission necessary that should be granted to all users.

Navigating the pages
--------------------

Navigation bar
~~~~~~~~~~~~~~

The navigation bar is available on every page. Navigation bar contains at least
the following elements:

* **Main Page** link will take you to Conntrackt homepage.
* **Administration** link will take you to Django's built-in administrator
  interface, which can be used both for managing the users, and for adding and
  modifying content. It is recommended to use Conntrackt's *native* user
  interface for adding and modifying content.

If you are currently logged-in, you will also be presented with the following
two elements:

* **Username**, which links to your profile page (NOT IMPLEMENTED).
* **Log-out** link.

If you are not logged-in, you will instead be presented with the following
elements:

* **Log-in** link, which will take you to the log-in page.

Main page
~~~~~~~~~

The main page gives a simple listing of the available projects and
locations.

Each row in a project listing includes:

* **Project name**, which can be clicked on in order to get to the *project
  details page*.
* **Download project iptables link** (small book icon), which can be used for
  downloading the iptables rules for an entire project.
* **Edit project link** (small pen icon), which can be used for editing basic
  information about a project.
* **Remove project link** (small cross icon), which can be used for removing a
  project.

Each row in a location listing includes:

* *Location name*.
* **Edit location link** (small pen icon), which can be used for editing basic
  information about a location.
* **Remove location link** (small cross icon), which can be used for removing a
  location.

Project details page
~~~~~~~~~~~~~~~~~~~~

The project details page provides listing of entities, as well as a diagram
showing the communications between them. The project details page also includes
links and buttons for manipulating the project information (including entities).

From top to bottom the page includes the following elements:

* Project title.
* Description of a project.
* Buttons for project-specific actions.
* Listing of end entities, grouped by locations.
* Communications diagram.

The project-specific buttons are:

* **Edit**, which can be used for editing basic information about a project.
* **Remove**, which can be used for removing a project.
* **Add entity**, which can be used for adding new entities to a project.
* **Add communication**, which can be used for adding a new communication to the
  project.
* **Get Iptables**, which can be used for downloading *iptables* rules for all
  entities in a project.

Each location-specific entity listing includes a *download location iptables*
link (small book icon), which can be used for downloading the *iptables* rules
for entities of a project in that particular location. Each entity row in the
listing includes:

* **Entity name**, which can be clicked on in order to get to the *entity
  details page*.
* **Download entity iptables link** (small list icon), which can be used for
  downloading the *iptables* rules for an entity.
* **Edit entity link** (small pen icon), which can be used for editing basic
  information about an entity.
* **Remove entity link** (small cross icon), which can be used for removing an
  entity.

A small **add entity** button is available within each location-specific
listing, which can also be used for adding entities to a project. The difference
is that if location-specific button is used, the location of new entity will be
pre-populated (saving some time).

The communications diagram displays all project entities, grouped by the
location, as well as communications between the entities. Each entity will be
represented by a distinctly-coloured square. The arrows pointing outside of the
entity represent an outgoing communication of an entity. Communications
displayed will also include information about the protocol and port being used.

The format of the diagram image is *SVG*.

Entity details page
~~~~~~~~~~~~~~~~~~~

The entity details page provides listing of entity's general information,
interfaces, incoming and outgoing communications, as well as the *iptables* rules.

From top to bottom the page includes the following elements:

* Entity name.
* Entity description.
* Buttons for entity-specific actions.
* General information about the entity.
* Listing of entity's interfaces.
* Listing of entity's incoming communications.
* Listing of entity's outgoing communications.
* *Iptables* rules for the entity.

The entity-specific buttons are:

* **Edit**, which can be used for editing basic information about an entity.
* **Remove**, which can be used for removing an entity.
* **Get Iptables**, which can be used for downloading the *iptables* rules for the
  entity.

The general information about an entity includes:

* **Project** to which the entity belongs. The project name can be clicked on in
  order to get to the project details page.
* *Location* where the entity can be found.

Each row of the interface listing includes:

* *Interface name*, with IP/netmask as well.
* **Edit interface link** (small pen icon), which can be used for editing basic
  information about an interface.
* **Remove interface link** (small pen icon), which can be used for removing an
  interface.

An **add interface** button can be found at the bottom of the interface listing,
which can be used for adding a new interface to the entity.

Each row of the incoming/outgoing communications listing includes:

* **Entity and interface name**, which can be clicked on in order to get to the
  source/destination entity.
* **Edit communication link** (small pen icon), which can be used for editing
  communication information.
* **Remove communication link** (small cross icon), which can be used for removing
  a communication.

The *iptables rules* section displays the full *iptables* rules for an
entity. It also sports a convenient **download** button for getting the *iptables*
rules.

Managing projects
-----------------

Adding a project
~~~~~~~~~~~~~~~~

New projects can be added from the *main page*. You can navigate to the *main
page* via link in the navigation bar.

Once at the *main page*, click on the **Add project** button. This will take you
to a page where some basic project information can be provided:

* *Name* (mandatory). This is the name of the project. Project name must be
  unique.
* *Description* (optional). This is the project description. This is a free-form
  field, and it can be filled-up by user as needed.

Once the mandatory fields have been filled-up, click on the **Add** button to add
the project. If no errors have been reported, and project was created
successfully, you will be taken to the *project details page*.

Removing a project
~~~~~~~~~~~~~~~~~~

Project can be removed either via the *main page* or via *project details
page*.

In order to remove a project via *main page*, navigate to it, and click on the
**remove icon** (small cross) next to the project name in the project listing.

In order to remove a project via *project details page*, navigate to the *main
page*, click on the project name in order to be taken to the *project details
page*, and then click on the **Remove** button towards the top of the page.

In both cases you will be prompted to confirm the removal of project. Keep in
mind that removing a project will also remove any entities that are associated
with it, interfaces of those entities, as well as communications involving those
entities.

Updating a project
~~~~~~~~~~~~~~~~~~

Basic project information can be updated either via *main page* or via *project
details page*.

In order to update a project via *main page*, navigate to it, and click on the
**edit icon** (small pen) next to the project name in the project listing.

In order to update a project via *project details page*, navigate to the *main
page*, click on the project name in order to be taken to the *project details
page*, and then click on the **Edit** button towards the top of the page.

Both actions will take you to the update page for a project where you can edit
the *name* and *description* of an existing project. In order to apply the
changes you made, click on the **Update** button.

Managing locations
------------------

Adding a location
~~~~~~~~~~~~~~~~~

New locations can be added from the *main page*. You can navigate to the *main
page* via link in the navigation bar.

Once at the *main page*, click on the **Add location** button. This will take
you to a page where some basic location information can be provided:

* *Name* (mandatory). This is the name of the location. Location name must be
  unique.
* *Description* (optional). This is the location description. This is a
  free-form field, and it can be filled-up by user as needed.

Once the mandatory fields have been filled-up, click on the **Add** button to
add the location.

Removing a location
~~~~~~~~~~~~~~~~~~~

Location can be removed via the *main page*.

Navigate to the *main page*, and click on the **remove icon** (small cross) next
to the location name in the location listing.

You will be prompted to confirm the removal of location. Keep in mind that
removing a location will also remove any entities that are associated with it,
as well as interfaces and communications associated with those entities.

Updating a location
~~~~~~~~~~~~~~~~~~~

Basic location information can be updated via *main page*.

In order to update a location navigate to *main page*, and click on the **edit
icon** (small pen) next to the location name in the location listing.

This will take you to the update page for a location where you can edit the
*name* and *description* of an existing location. In order to apply the changes
you made, click on the **Update** button.

Managing entities
-----------------

Adding an entity
~~~~~~~~~~~~~~~~

New entities can be added to a project via *project details page*. The page can
be reached by going to the *main page*, and then clicking on specific project
name in project list.

Once at the *project details page*, click on the **Add entity** button, either
on the one towards the top of the page, or location-specific one. This will take
you to a page where some basic entity information can be provided:

* *Name* (mandatory). This is the name of an entity. Entity name must be unique
  in a project. Same name can be used by multiple entities as long as they
  belong to separate projects.
* *Description* (optional). This is the entity description. This is a free-form
  field, and it can be filled-up by user as needed.
* *Project* (mandatory). This is the project that the entity will belong to. The
  project will have a fixed value.
* *Location* (mandatory). This is the location where the entity is located. If
  location-specific **Add entity** button was used, this field will have a fixed
  value.

Once the mandatory fields have been filled-up, click on the **Add** button to
add the entity.

.. tip::
   Using location-specific **Add entity** can be a great time-saver if you need
   to add a lot of entities to a single location. Use it sparingly.

Removing an entity
~~~~~~~~~~~~~~~~~~

Entity can be removed either via the *project details page* or via *entity
details page*.

In order to remove an entity via *project details page*, navigate to it, and
click on the **remove icon** (small cross) next to the entity name.

In order to remove an entity via *entity details page*, navigate to the *project
details page*, click on the entity name in order to be taken to the *entity
details page*, and then click on the **Remove** button towards the top of the
page.

In both cases you will be prompted to confirm the removal of entity. Keep in
mind that removing an entity will also remove any interfaces that are associated
with it, as well as related communications.

Updating an entity
~~~~~~~~~~~~~~~~~~

Basic entity information can be updated either via *project details page* or via
*entity details page*.

In order to update an entity via *project details page*, navigate to it, and
click on the **edit icon** (small pen) next to the entity.

In order to update an entity via *entity details page*, navigate to the *project
details page*, click on the entity name in order to be taken to the *entity
details page*, and then click on the **Edit** button towards the top of the
page.

Both actions will take you to the update page for an entity where you can edit
the *name*, *description*, *project*, or *location* of an existing entity. In
order to apply the changes you made, click on the **Update** button.

.. warning::
   Project to which an entity belongs can only be changed if there's no defined
   communications involving the entity in its current project.

Managing interfaces
-------------------

Adding an interface
~~~~~~~~~~~~~~~~~~~

New interface can be added to an entity via *entity details page*. The page can
be reached by going to the *project details page*, and then clicking on specific
entity name in the list.

Once at the *entity details page*, click on the **Add interface** button. This
will take you to a page where some basic entity information can be provided:

* *Name* (mandatory). This is the name of an interface. Interface name must be
  unique in an entity. Same name can be used by multiple interfaces as long as
  they belong to separate entities.
* *Description* (optional). This is the interface description. This is a
  free-form field, and it can be filled-up by user as needed.
* *Entity* (mandatory). This is the entity that the interface will belong
  to. The entity will have a fixed value.
* *Address* (mandatory). This is the IP address of an interface.
* *Netmask* (mandatory). This is the netmask associated with the interface IP
  address. If the entity address is not a subnet (i.e. it's supposed to be a
  single IP address), netmask should be set to `255.255.255.255`. Conntrackt
  takes into account the difference between single IP address and subnet,
  producing slightly different *iptables* rules based on this (for single IP
  addresses, the netmask of *255.255.255.255* is omitted).

Once the mandatory fields have been filled-up, click on the **Add** button to
add the interface. This will take you back to the *entity details page*.

Removing an interface
~~~~~~~~~~~~~~~~~~~~~

Location can be removed via the *entity details page*.

Navigate to the *entity details page*, and click on the **remove icon** (small cross) next
to the interface name in the interface listing.

You will be prompted to confirm the removal of interface. Keep in mind that
removing an interface will also remove any communications associated with that
interface.

Updating an interface
~~~~~~~~~~~~~~~~~~~~~

Basic interface information can be updated via *entity details page*.

In order to update an interface, navigate to *entity details page*, and click on
the **edit icon** (small pen) next to the interface name in the interface
listing.

This will take you to the update page for an interface where you can edit the
*name*, *description*, *entity*, *address*, and *netmask* of an existing
interface. In order to apply the changes you made, click on the **Update**
button.

Managing communications
-----------------------

Adding a communication
~~~~~~~~~~~~~~~~~~~~~~

New communications can be added to a project via *project details page* or via
*entity details page*.

In order to add a communication via *project details page*, navigate to it, and
click on the **Add communication** button.

In order to add a communication via *entity details page*, navigate to it, and
click on one of the **Add communication** buttons located in incoming/outgoing
communication listings.

In both cases this will take you to a page where communication information can
be provided:

* *Source* (mandatory). This is the source interface from which the
  communication originates.
* *Destination* (mandatory). This is the destination interface at which the
  communication terminates.
* *Protocol* (mandatory). This is the protocol used for the communication (*TCP*,
  *UDP*, or *ICMP*).
* *Port* (mandatory). This is the port used for communication (in case of
  TCP/ICMP), or packet type (in case of ICMP).
* *Description* (optional). This is the communication description. This is a
  free-form field, and it can be filled-up by user as needed. The communication
  description will be visible in the generated *iptables* rules as well (just
  above the rule).

Once the mandatory fields have been filled-up, click on the **Add** button to
add the communication.

.. tip::
   Using the **Add communication** buttons from the *entity details page* means
   that the form will have pre-selected the source or destination to be the
   first interface of the entity at hand. This can be quite useful when adding a
   lot of communications that affect a specific entity (for example, database
   server).

Removing a communication
~~~~~~~~~~~~~~~~~~~~~~~~

Location can be removed via the *entity details page*.

Navigate to the *entity details page*, and click on the **remove icon** (small cross) next
to the communcation in the incoming/outgoing communication listing.

You will be prompted to confirm the removal of communication.

Updating a communication
~~~~~~~~~~~~~~~~~~~~~~~~

Communication can be updated via *entity details page*.

In order to update a location navigate to *entity details page*, and click on
the **edit icon** (small pen) next to the communication in the incoming/outgoing
communication listing.

This will take you to the update page for a communication where you can edit the
*source*, *destination*, *protocol*, *port*, and *description* of an existing
communication. In order to apply the changes you made, click on the **Update**
button.

Generating and downloading *iptables* rules
-------------------------------------------

In addition to tracking the communications across a project, one of the main
features of Conntrackt is its ability to generate the *iptables* rules for all
entities in a project based on provided communications data.

These *iptables* rules can then be easily applied to *GNU/Linux* entities. The
rules are generated with the following restrictions in mind:

* Default target for *INPUT* chain is *DROP*.
* Default target for *FORWARD* chain is *DROP*.
* Default target for *OUTPUT* chain is *ALLOW*.
* No limits are imposed on the *OUTPUT* chain.
* Rules for the *INPUT* chain are applied using a whitelist. Only explicitly
  defined communications in the *iptables* will be used to generate the *ACCEPT*
  rules. The matching is performed based on *source*, *protocol*, and
  destination *port*.
* The *INPUT* chain will contain the following default rules as well::

    -A INPUT -i lo -j ACCEPT
    -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT

  This will allow all incoming connections from the localhost itself, as well as
  any incoming packages of previously-established connections.

Rules can be downloaded either induvidually, for a specific entity, or in
bulk. If downloaded in bulk, the *iptables* rules can be downloaded either for
an entire project, or for a specific location of a project.

The bulk download results in a ZIP archive which contains the *iptables* rules
for each entity in a separate file.

The *iptables* rules for a specific entity can be downloaded both from a
`Project details page`_ (the **download entity iptables link** that looks like a
small list icon, right next to the entity name), or via `Entity details page`_
(the **get iptables** button at top, and **download** button just below the
iptables listing).

Project *iptables* rules can be downloaded either via the *Main page* (**download
project iptables link** that looks like a small book next to the project), or
through the project details page (**download iptables** button at top).

Project *iptables* rules for a specific location can be downloaded from `Project
details page`_, via the small **download location iptables link** (small book
icon), located right next to the location name.

Managaing data through django.contrib.admin
-------------------------------------------

Although the preferred interface for managing data in Conntrackt is through its
own pages, it is possible to make modifications to the data through Django's
built-in administration interface (*django.contrib.admin*). It is possible to
both add new data, as well as modify the existing information.

The admin interface for Conntrackt behaves the same as for every Django
application, except for some convenience functionality that helps speed-up
adding or modification of some data.

The interfaces, entities, and communications pages allow editing most of the
data inline, which can speed-up the process quite a bit. In addition, all three
pages provide filters that allow you to easily view data specific to a
particular project and/or location. The filters are available on the right side.

While interfaces can be managed separately, you may find it much easier to
manage them from within the entity pages. When adding or modifying an entity,
you will have some inline forms for specifying entity's interfaces. This is the
recommended way to add and modify the interfaces for entities.

Wherever possible, inline fields are used in order to allow easier updates to
existing information. This is particularly useful in case of communications, and
to lesser effect entities and interfaces.

When editing communications you may find it particularly useful to add them
through the communications list page by first specifying a filter (by project
and/or location), and then clicking on the **Add communication** link. This way
the filter will be applied to *source* and *destination* fields.

For example, if you choose project **Test**, and location **Main site**, and
then click on the **Add communication** button, the *source* and *destination*
fields will be limited to entity interfaces that specificaly belong to the
**Test** project and location **Main site**.

You can also easily modify existing communications using the communication
listing page. From there you can easily modify source, destination, protocol,
and port. Similarly to adding a new communication, you can apply a filter that
will narrow-down the selection for source and destination. It is highly
recommended to apply the filter in this way.

