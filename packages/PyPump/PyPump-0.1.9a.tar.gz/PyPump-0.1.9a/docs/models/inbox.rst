Inboxen
=======

This object represents an Inbox on pump.io 

.. note:: The pump variable is an instantiated PyPump class e.g. pump = PyPump("<webfinger>", client_name="<name>", etc...)

.. py:class:: Inbox

    This represents an Inbox, These are containers for other models e.g. Note, Image, etc...
    

    .. py:attribute:: actor

        This is the person's inbox it is

	    >>> inbox.actor
            <Person someone@example.com> 

    .. py:attribute:: author

        Synonymous with actor


Example
-------

.. note:: When you use inbox[<index>] or inbox[<start>:<end>] it will locally cache it in the inbox object.

Get the latest item from the inbox::

    >>> latest_item = my_inbox[0]
    <Note: "This is a note in my inbox">

Prehaps you want a slice::

    >>> some_items = my_inbox[10:100]
    
Now iterate over and show them::

    >>> for item in my_inbox:
    ...    print(item)

.. warning: Using a deleted comment will cause DoesNotExist to be raised

