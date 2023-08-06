tt_streams
==========
Provides a means of creating streams of content


Usage
-----
You can use the tt_streams to collect different models from different apps into
a unified stream of models.  Streams are made up of a series of ``StreamItem``
subclasses that you write that are specific to each app that they are used in.

To skip straight ahead to simple (bordering on naive) implementation examples,
check out the `project/example/models.py`_ file.

.. _project/example/models.py: https://github.com/texastribune/tt_streams/blob/master/project/example/models.py

Each Django app that wants to expose its models to streams should do two things:

* Create a specific ``*Item`` model.  For example, ``StoryItem`` should subclass
  the ``StreamItem`` model and provide a connection via a ``ForeignKey`` to the
  model that is opting in,``Story`` in this case.
* Create a way to get associate those models with a ``Stream``.  This is most
  commonly done via an inline interface to the ``StreamItem`` sub-class.

Beyond these requirements, everything else you do with your subclass of
``StreamItem`` is up to you.  It's common to use your ``StreamItem`` class as a
cache table so you don't have to send another query to the database.

For example, the ``StoryItem`` automatically stores the title of its related
``Story`` model when it is saved, and a receiver is hooked up to the ``post_save``
signal for ``Story`` to ensure that all of its ``stream_items`` are resaved each
time it is saved.

There are a couple of things to note:

* You can name your subclass of ``StreamItem`` whatever you would like
* You can name your related field whatever you like
* It automatically has a ``pub_date`` that you *can* use for ordering, but they
  are not ordered by default


Installation & Configuration
----------------------------
You can install the latest release of ``tt_streams`` using `pip`_:

::

    pip install tt_streams

Make sure to add ``tt_streams`` to your ``INSTALLED_APPS``.  You
can add this however you like.  This works as a copy-and-paste solution:

::

	INSTALLED_APPS += ["tt_streams", ]

Once installed, you have to run either ``syncdb``, or ``migrate`` if you are
using `South`_.

.. _pip: http://www.pip-installer.org/
.. _South: http://south.aeracode.org/


Contributing
------------

* Create something awesome -- make the code better, add some functionality,
  whatever (this is the hardest part).
* `Fork it`_
* Create a topic branch to house your changes
* Get all of your commits in the new topic branch
* Submit a `pull request`_

.. _Fork it: http://help.github.com/forking/
.. _pull request: http://help.github.com/pull-requests/


License
-------
Copyright 2013 Texas Tribune

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
