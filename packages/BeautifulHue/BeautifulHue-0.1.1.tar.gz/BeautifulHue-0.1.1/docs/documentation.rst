Documentation
=============

Requirements
------------

* Python 2.6+

Installation
------------

Via pip::

    pip install beautifulhue

or via easy_install::

   easy_install beautifulhue

or via source::

   python setup.py install


Bridge
------
(`official bridge reference <http://developers.meethue.com/1_lightsapi.html>`_)

Instantiation::
	
	from beautifulhue.api import Bridge

	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	# Replace the ip address above with the ip address of your hue bridge.


Lights
------
(`official lights reference <http://developers.meethue.com/1_lightsapi.html>`_)

Methods:
^^^^^^^^

get
^^^

**Get a single light**::

	# Get light number 3.
	from beautifulhue.api import Bridge

	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	resource = {'which':3}
	bridge.light.get(resource)


**Get new lights.**::

	# Get new lights as discovered by the lights.find() method.
	from beautifulhue.api import Bridge

	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	resource = {'which':'new'}
	bridge.light.get(resource)


**Get all lights**::

	# Get all lights (as defined by Philips Hue documentation).
	from beautifulhue.api import Bridge
	
	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	resource = {'which':'all'}
	bridge.light.get(resource)


Example Response::

	{'resource': [
				     {u'name': u'Hue Lamp 1', 'id': 1},
					 {u'name': u'Hue Lamp 2', 'id': 2},
					 {u'name': u'Hue Lamp 3', 'id': 3}
				 ]
	}


Example Usage::

	from beautifulhue.api import Bridge
	
	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	lights = bridge.light.get({'which':'all'})
	for light in lights['resource']:
	    bridge.light.get({'which':light['id']})


**Verbose Mode**::

	Verbose mode returns a list of expanded, individual light information; the
	same level of deail as when requesting individual lights, as defined in the
	Philips hue documentation.


**Get all lights with verbose light detail**:

	# Get all lights with verbose light output.
	from beautifulhue.api import Bridge
	
	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	resource = {'which':'all', 'verbose':True}
	bridge.light.get(resource)


find
^^^^

**Discover new lights**::

	# Find new lights associated with the active bridge.
	from beautifulhue.api import Bridge
	
	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	resource = {'which':'new'}
	bridge.light.find(resource)


update
^^^^^^

**Update a light's attributes**::

	# Update light #3's name.
	from beautifulhue.api import Bridge
	
	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	resource = {
	    'which':3,
	    'data':{
	        'attr':{'name':'My Hue Light 3'}
	    }
	}
	bridge.light.update(resource)


** Update a light's state**::

	# Update light #3's state.
	from beautifulhue.api import Bridge
	
	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	resource = {
	    'which':3,
	    'data':{
	        'state':{'on':True, 'ct':222}
	    }
	}
	bridge.light.update(resource)


Groups
------
(`official groups reference <http://developers.meethue.com/2_groupsapi.html>`_)

Methods:
^^^^^^^^

get
^^^

**Get a bridge group**::

	# Get bridge group 0.
	from beautifulhue.api import Bridge
	
	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	resource = {'which':0}
	bridge.group.get(resource)


**Get all bridge groups**::

	# Get all groups.
	from beautifulhue.api import Bridge
	
	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	resource = {'which':'all'}
	bridge.group.get(resource)


**Verbose Mode**::

	Verbose mode returns a list of expanded, individual group information; the
	same level of deail as when requesting individual groups, as defined in the
	Philips hue documentation.


**Get all groups with verbose group detail**::

	# Get all groups with verbose group output.
	from beautifulhue.api import Bridge
	
	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	resource = {'which':'all', 'verbose':True}
	bridge.group.get(resource)


update
^^^^^^

**Update a bridge group**::

	# Update group 0.
	from beautifulhue.api import Bridge
	
	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	resource = {
			       'which':0,
			       'data':{
			           'action':{
			               'on':True,
			               'ct':166,
			               'bri':170
			           }
			       }
			   }
	bridge.group.update(resource)


Schedules
---------
(`official schedules reference <http://developers.meethue.com/3_schedulesapi.html>`_)

Methods:
^^^^^^^^

get
^^^

**Get a bridge schedule**::

	# Get schedule 1.
	from beautifulhue.api import Bridge
	
	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	resource = {'which':1}
	bridge.schedule.get(resource)


**Get all bridge schedules**::

	# Get all schedules.
	from beautifulhue.api import Bridge
	
	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	resource = {'which':'all'}
	bridge.schedule.get(resource)


**Verbose Mode:**

	Verbose mode returns a list of expanded, individual schedule information; the
	same level of deail as when requesting individual schedules, as defined in the
	Philips hue documentation.


**Get all schedules with verbose schedule detail**::

	# Get all schedules with verbose schedule output.
	from beautifulhue.api import Bridge
	
	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	resource = {'which':'all', 'verbose':True}
	bridge.schedule.get(resource)


create
^^^^^^

**Create a bridge schedule**::

	# Create a new schedule.
	from beautifulhue.api import Bridge
	
	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	data =  {
	    "description": "My wake up alarm!",
	    "command": {
	        "address": "/api/0/groups/1/action",
	        "method": "PUT",
	        "body": {
	            "on": True
	        }
	    },
	    "time": "2013-06-09T06:30:00"
	}
	resource = {'which':'my schedule', 'data':data}
	bridge.schedule.create(resource)


update
^^^^^^

**Update a bridge schedule**::

	# Update schedule 1's description and time.
	from beautifulhue.api import Bridge
	
	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	data =  {
	    "description": "My updated alarm!",
	    "time": "2013-06-09T05:30:00"
	}
	resource = {'which':1, 'data':data}
	bridge.schedule.update(resource)


delete
^^^^^^

**Delete a bridge schedule**::

	# Delete schedule 1.
	from beautifulhue.api import Bridge
	
	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	resource = {'which':1}
	bridge.schedule.delete(resource)


Configuration
-------------
(`official configuration reference <http://developers.meethue.com/4_configurationapi.html>`_)

Methods:
^^^^^^^^

get
^^^

**Get bridge configuration**::

	# Get bridge config.
	from beautifulhue.api import Bridge
	
	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	resource = {'which':'bridge'}
	bridge.config.get(resource)


**Get system configuration**::

	# Get system config.
	from beautifulhue.api import Bridge
	
	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	resource = {'which':'system'}
	bridge.config.get(resource)


create
^^^^^^

**Create a bridge configuration object.**

	# Create a new bridge user.
	from beautifulhue.api import Bridge
	
	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	resource = {'user':{"devicetype": "beautifulhue", "name": "1234567890"}}
	bridge.config.create(resource)


update
^^^^^^

**Update bridge configuration attributes**::

	resource = {
	    'data':{
	        'attr':{
	            'name':'My Bridge Name'
	        }
	    }
	}
	bridge.config.update(resource)


delete
^^^^^^

**Delete a bridge configuration object**::

	# Delete a bridge user.
	from beautifulhue.api import Bridge
	
	bridge = Bridge(device={'ip':'192.168.1.14'}, user={'name':'newdeveloper'})
	resource = {'user':{"name": "1234567890"}}
	bridge.config.delete(resource)


Portal
------
(`official portal reference <http://developers.meethue.com/5_portalapi.html>`_)

Instantiation::

	from beautifulhue.api import Portal


Methods:
^^^^^^^^

get
^^^

**Get hue portal data**:

	from beautifulhue.api import Portal
	
	portal = Portal()
	portal.get()

