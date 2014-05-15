OpenDayLight API
================

Opendaylight API wrapped in Python.

Current usable functions
------------------------

-   ``login (host, username='admin', password='admin') : bool``

-   ``get_topo () : dict``

-   ``get_flow ( [ node_id ], [ flow_name ] ) : list or dict``

-   ``add_flow (node_id, flow_name, constrains, actions, priority=500, active=True)``

-   ``toggle_flow (node_id, flow_name)``

-   ``remove_flow (node_id, flow_name)``

Detailed function descriptions
------------------------------

-   ``login (host, username='admin', password='admin') : bool``

    -   Login to a controller.
    
    -   ``host`` can be an IP address and port string like ``'192.168.179.129:8080'``.

    -   If login successed, the return value will be ``True``, otherwise further operations related to ``host`` will fail.

-   ``get_topo () : dict``

    -   Get network topology.

    -   Return value is a hierarchical dictionary

        -   First layer is switch's id

        -   Second layer is host's IP address or the other switch's id

        -   Third layer records MAC address and forward port

        -   For example, given topology as following:

            ::

                {   '00:00:00:00:00:00:00:01':
                        {   '00:00:00:00:00:00:00:02': { 'port': 's1-eth4'},
                            '00:00:00:00:00:00:00:03': { 'port': 's1-eth5'},
                            '10.0.0.1': { 'mac': u'12:26:b7:85:41:6d',
                                          'port': u's1-eth1'}}}

            -   Switch ``00:00:00:00:00:00:00:01`` connect host ``10.0.0.1`` through port ``s1-eth1``

            -   Host ``10.0.0.1``'s mac address is ``12:26:b7:85:41:6d``

-   ``get_flow ( [ node_id ], [ flow_name ] ) : list or dict``

    -   Get static flow according to ``node_id`` or ``flow_name`` or both

    -   If both ``node_id`` and ``flow_name`` are not given, the result will be a ``list`` of all static flows on the controller

    -   If ``node_id`` given, the result will be a ``list`` of all static flow on the node

    -   If ``flow_name`` given, the result will be a ``dict`` describing that flow

    -   If both ``node_id`` and ``flow_name`` are given, the result will be a ``dict`` describing that flow

-   ``add_flow (node_id, flow_name, constrains, actions, priority=500, active=True)``

    -   Add a flow to switch ``node_id``, if ``flow_name`` exists, new flow will override the old one
    -   ``constrains`` is a ``dict``, when override happens, old constrains, which is not in new constrains, will be kept.

-   ``toggle_flow (node_id, flow_name)``

    -   Toggles the ``installInHw`` property of the flow

-   ``remove_flow (node_id, flow_name)``

    -   Remove the flow ``flow_name`` on switch ``node_id``
