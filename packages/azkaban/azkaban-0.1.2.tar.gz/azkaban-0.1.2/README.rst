Azkaban
=======

Lightweight command line interface (CLI) for Azkaban_:

* Define jobs from a single python file
* Build projects and upload to Azkaban from the command line

Integration is meant to be as transparent as possible:

* No additional folders and files
* No imposed project structure


Installation
------------

Using pip_:

.. code:: bash

  $ pip install azkaban


Quickstart
----------

We first create a file to define our project. Let's call it :code:`jobs.py`, 
although any name would work.

In this example, we add a single job and file:

.. code:: python

  from azkaban import Job, Project

  project = Project('foo')

  project.add_file('/path/to/bar.txt', 'bar.txt')
  project.add_job('bar', Job({'type': 'command', 'command': 'cat bar.txt'}))

  if __name__ == '__main__':
    project.main()

From the command line we can now run :code:`python jobs.py --help` to view the 
list of all available options (:code:`build`, :code:`upload`, etc.). E.g. the 
following command will create the archive :code:`foo.zip` containing all the 
project's jobs and dependency files:

.. code:: bash

  $ python jobs.py build foo.zip


More
----

Aliases
*******

To avoid having to enter the server's URL on every upload (or hard-coding it 
into our project's configuration file, ugh), we can define aliases in 
:code:`~/.azkabanrc`:

.. code:: cfg

  [foo]
  url = http://url.to.foo.server:port
  [bar]
  url = http://url.to.bar.server:port

We can now upload directly to each of these URLs with the shorthand:

.. code:: bash

  $ python jobs.py upload -a foo

This has the added benefit that we won't have to authenticate on every upload. 
The session ID is cached and reused for later connections.


Job options
***********

There often are options which are common across multiple jobs. For this 
reason, the :code:`Job` constructor takes in multiple options dictionaries. 
The first definition of an option (i.e. earlier in the arguments) will take 
precedence over later ones.

We can use this to efficiently share default options among jobs, for example:

.. code:: python

  defaults = {'user.to.proxy': 'boo', 'retries': 0}
  jobs = [
    Job({'type': 'noop'}),
    Job({'type': 'noop'}, defaults),
    Job({'type': 'command', 'command': 'ls'}, defaults),
    Job({'type': 'command', 'command': 'ls -l', 'retries': 1}, defaults),
  ]

All jobs except the first one will have their :code:`user.to.proxy` property 
set. Note also that the last job overrides the :code:`retries` property.

Finally, nested dictionaries can be used to group options efficiently:

.. code:: python

  # e.g. this job
  Job({
    'proxy.user': 'boo',
    'proxy.keytab.location': '/path',
    'param.input': 'foo',
    'param.output': 'bar',
  })
  # is equivalent to this one
  Job({
    'proxy': {'user': 'boo', 'keytab.location': '/path'},
    'param': {'input': 'foo', 'output': 'bar'}
  })


Pig jobs
********

Because pig jobs are so common, a :code:`PigJob` class is provided which 
accepts a file path (to the pig script) as first constructor argument, 
optionally followed by job options. It then automatically sets the job type 
and adds the corresponding script file to the project.

.. code:: python

  from azkaban import PigJob

  project.add_job('baz', PigJob('/.../baz.pig', {'dependencies': 'bar'}))


Next steps
**********

Any valid python code can go inside the jobs configuration file. This includes 
using loops to add jobs, subclassing the base :code:`Job` class to better suit 
a project's needs (e.g. by implementing the :code:`on_add` and 
:code:`on_build` handlers), ...


.. _Azkaban: http://data.linkedin.com/opensource/azkaban
.. _pip: http://www.pip-installer.org/en/latest/
