.. Copyright (C) 2013 Branko Majic

   This file is part of Django Conntrackt documentation.

   This work is licensed under the Creative Commons Attribution-ShareAlike 3.0
   Unported License. To view a copy of this license, visit
   http://creativecommons.org/licenses/by-sa/3.0/ or send a letter to Creative
   Commons, 444 Castro Street, Suite 900, Mountain View, California, 94041, USA.


About Django Conntrackt
=======================

Django Conntrackt is a simple application intended to provide system
administrators and integrators that deploy servers at client's premises to
easily keep track of required networ communications between different servers,
routers, client workstations, and even whole networks/sub-networks.


Why was this application created?
---------------------------------

The application was created in order to alleviate painful and error prone
tracking of IP addresses and network communications inside of spread-sheet
files. Another reason was the need to create simple iptables rules based on this
information with as little hassle as possible.

The *iptables* generation requirements for Django Conntrackt were farily simple,
and do not include any complex functionality. It all boils down to rejecting all
communication except for explicitly defined links.


Features
--------

Django Conntrackt sports a number of useful features for system administrators
and integrators:

* Managing entities through multiple projects (separating the entities
  per-project basis).
* Grouping entities inside of a project in one or more locations (which can be
  either logical or physical).
* Specifying entities that represent servers, routers, workstations, networks,
  subnets or any other networked device or abstraction within a network.
* Specifying multiplel network interfaces for each entity.
* Specifying the communication link between two entities, which includes
  information such as protocol and port.
* Generation of *iptables* rules for devices based on GNU/Linux that can be
  consumed by the *iptables-restore* utility.
* Generation of *iptables* rules on per-location/project basis (multiple
  *iptables* rule files inside of a *ZIP* file.
