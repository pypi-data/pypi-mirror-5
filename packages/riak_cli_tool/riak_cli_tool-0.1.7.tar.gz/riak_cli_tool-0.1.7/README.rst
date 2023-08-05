es-riak
=======

This is a helper script for interacting with Riak.

Before you begin using this utility, you should know that it was written to
interact not just with Riak, but with a specific instantiaion of Riak used to
support the Enstratius cloud management software suite. 

There are methods available here, such as ``--elevate-api-key`` that have no
meaning outside of the context of an installation of Riak to support the
Enstratius cloud management software suite.

While this script was written to interact with Riak supporting Enstratius, the
script itself is in no way endorsed or supported by Enstratius or Dell
Software. 

Word of warning
---------------

By using this script you are violating the datamunging warning set by John Vincent in his
Riak overview. Proceed at your own risk.

Requirements
------------

1. Python
2. [Requests Library](http://docs.python-requests.org/en/latest/user/install/#install)

Helpful: http://docs.python-requests.org/en/latest/user/quickstart

Installation
------------

.. code-block:: bash

   sudo easy_install riak-cli-tool

or

.. code-block:: bash

   sudo pip install riak-cli-tool


Secondary Indices
-----------------

Enstratius makes heavy use of secondary indices. This scrip is supposed to
find, save, and utilize existing secondary indices when updating bucket
contents that have them in place.

This is not well tested.

Configuration Files
-------------------

None. You'll want to add an export statement to your profile:


.. code-block:: bash

   export riak_host='127.0.0.1'

and make sure it is sourced before attempting to use the utility.

The port is set to 8098.

Commands
--------

List all buckets 
~~~~~~~~~~~~~~~~

THIS IS A BAD IDEA, USUALLY.  

.. code-block:: bash

   es-riak --list-buckets
   
   {
       "buckets": [
           "content_template", 
           "configuration_management_system", 
           "frontend_configuration"
       ]
   }

List all keys in a bucket
~~~~~~~~~~~~~~~~~~~~~~~~~

THIS IS A BAD IDEA, USUALLY.  

.. code-block:: bash

   es-riak --list-keys -b content_template
   
   {
       "keys": [
           "passwordChangeSubject", 
           "optimusEngineEmail", 
           "changeAccountData_en"
       ]
   }

Show the contents of a bucket
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   es-riak --show -b frontend_configuration -k 1
   
   {
       "SCHEMA_VERSION": "0", 
       "autoProvisionUsers": "true", 
       "defaultAuthenticationMethod": "NATIVE", 
       "defaultGroupIds": [], 
       "forceDefaultAuthentication": "true", 
       "forceDeny": [], 
       "masterNetworkId": 999, 
       "systemName": "Enstratius"
   }

Save the contents of a bucket/key to a file:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   es-riak --save save_file.json -b frontend_configuration -k 1
   
   Saved contents of: 
   
     http://172.16.243.131:8098/buckets/frontend_configuration/keys/1 
   
   to 
   
     save_file.json
   
Checking the contents of the save file:

.. code-block:: bash

   cat save_file.json  | python -mjson.tool
   
   {
       "SCHEMA_VERSION": "0", 
       "autoProvisionUsers": "true", 
       "defaultAuthenticationMethod": "NATIVE", 
       "defaultGroupIds": [], 
       "forceDefaultAuthentication": "true", 
       "forceDeny": [], 
       "masterNetworkId": 1, 
       "systemName": "Enstratius"
   }

Update the contents of a bucket/key by passing in a json file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   es-riak --update -b frontend_configuration -k 1 -i input.json
   Valid JSON
   updating!
   
   Saved contents of: 
   
     http://172.16.243.131:8098/buckets/frontend_configuration/keys/1 
   
   to 
   
     input.json.original
   
   
    Done.
   
    To view your changes, call:
   
   es-riak --show -b frontend_configuration -k 1

where the file ``input.json`` has contents:

.. code-block:: bash

   cat input.json | python -mjson.tool
   
   {
       "SCHEMA_VERSION": "0", 
       "autoProvisionUsers": "true", 
       "defaultAuthenticationMethod": "NATIVE", 
       "defaultGroupIds": [], 
       "forceDefaultAuthentication": "true", 
       "forceDeny": [], 
       "masterNetworkId": 999, 
       "systemName": "Enstratius"
   }

bucket contents post-update:

.. code-block:: bash

   es-riak --show -b frontend_configuration -k 1
   
   {
       "SCHEMA_VERSION": "0", 
       "autoProvisionUsers": "true", 
       "defaultAuthenticationMethod": "NATIVE", 
       "defaultGroupIds": [], 
       "forceDefaultAuthentication": "true", 
       "forceDeny": [], 
       "masterNetworkId": 999, 
       "systemName": "Enstratius"
   }

Doing a "PUT" to a bucket/key
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A plain old "PUT" differs from an update in that there is no step of saving the
current contents of a bucket/key (as there may be none) prior to putting the
contents of the passed file to the bucket/key.

Futhermore, if there happen to be existing contents of a given bucket/key such
as -b frontend_configuration -k 1 and a put is made to that combination, the
existing contents will be immediately overwritten. 

To put the contents of a file to a bucket/key, execute a call like this:

.. code-block:: bash

   es-riak --put -b frontend_configuration -k 1 -i input.json

where the contents of input.json might be:

.. code-block:: json

   {
       "SCHEMA_VERSION": "0",
       "autoProvisionUsers": "true",
       "defaultAuthenticationMethod": "NATIVE",
       "forceDefaultAuthentication": "true",
       "masterNetworkId": 1,
       "systemName": "Enstratius Hosted",
       "systemReplyEmail": "systemreplyemail@enstratius.com",
       "systemSupportEmail": "systemsupportemail@enstratius.com",
       "systemSupportUrl": "http://system.support.url.com",
       "systemUserConsoleUrl": "https://system.user.console.url/test"
   }

The ``--put`` flag will trigger the following checks before attempting to put
the file contents to the bucket/key:

#. Does the file exist?
#. Is the file valid JSON?

.. code-block:: bash

   So be it.
   
   Valid JSON
   
   Putting the contents of
   
   input.json
   
   to
   
   http://127.0.0.1:8098/buckets/frontend_configuration/keys/1
   
   
    Done.
   
     To view the results of this action, call:
   
     es-riak --show -b frontend_configuration -k 1


Validating an input JSON file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Valid JSON:
^^^^^^^^^^^

.. code-block:: bash

   es-riak --validate -i input.json
   
   Valid JSON

Invalid JSON:
^^^^^^^^^^^^^

.. code-block:: bash

   es-riak --validate -i invalid.txt 
   
   Invalid JSON

Where the contents of invalid.txt are:

.. code-block:: bash

   {
       "SCHEMA_VERSION": "0", 
       "autoProvisionUsers": "true", 
       "defaultAuthenticationMethod": "NATIVE", 
       "defaultGroupIds": [], 
       "forceDefaultAuthentication": "true", 
       "forceDeny": [], 
       "masterNetworkId": 999, 
       "systemName": 
   }


Elevating an API key
~~~~~~~~~~~~~~~~~~~~

You can use this utility to elevate an API key to a "system" key.

.. code-block:: bash

   es-riak --elevate-api-key -b api_key -k <your_api_access_key>

An example of this type of interaction is shown here:

.. code-block:: bash

   es-riak --show -b api_key -k DJFLPQSDJAUHLMLPDJIO
   
   {
       "SCHEMA_VERSION": "0",
       "accessKey": "DJFLPQSDJAUHLMLPDJIO",
       "activationTimestamp": 1368202730181,
       "billingAccount": 52901,
       "customer": 51400,
       "description": "test key",
       "encryption": "TWO",
       "name": "Test",
       "network": 50069,
       "secretKey": "ee235a772d0def0b069d6364cda6a34e8d6d9eca6afcd94d37770e12c6d6d735df9a75fb64bd0a1cb18911a7ed4744fb"
   }

There is no need to issue the show command first, I'm just doing it to highlight the differences.

With this information issue the command:

.. code-block:: bash

   es-riak --elevate-api-key -b api_key -k DJFLPQSDJAUHLMLPDJIO
   
There will be no output from this command.

bucket contents post-elevate:

.. code-block:: bash

   es-riak --show -b api_key -k DJFLPQSDJAUHLMLPDJIO
   
   {
       "SCHEMA_VERSION": "0",
       "accessKey": "DJFLPQSDJAUHLMLPDJIO",
       "activationTimestamp": 1368202730181,
       "billingAccount": 52901,
       "customer": 51400,
       "customerManagementKey": true,
       "description": "test key",
       "encryption": "TWO",
       "name": "Test",
       "network": 50069,
       "secretKey": "ee235a772d0def0b069d6364cda6a34e8d6d9eca6afcd94d37770e12c6d6d735df9a75fb64bd0a1cb18911a7ed4744fb",
       "systemManagementKey": true
   }
