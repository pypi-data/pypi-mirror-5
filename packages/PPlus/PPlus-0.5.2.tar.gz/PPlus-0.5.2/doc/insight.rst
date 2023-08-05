.. _insight:

PPlus Insight
=============
In this section we describe some information about PPlus development
that could be useful for advanced users.

.. _file:

File Management
---------------

Remote files are managed based on `file keys`. They serve as identifiers for
accessing physical files without knowing their precise location, regardless of
the network protocols.

The following rules apply to file keys regarding experiment level:

- between different experiment directories, the same file keys may be used;
  that is, key 'BIGFILE' used in experiment A, and key 'BIGFILE' used in
  experiment B, are both referring to two different files
- within experiment directory, if the same file key is used for opening new
  remote file for writing, by default the content of the existing file will be
  overwritten without warning; otherwise, an error will be reported

As a result, **within experiment all file keys must be unique** to avoid
unwanted data corruption.

.. note::

    It is strongly advisable `not` to access any physical files in the locations
    affected by experiment code that is running: `experiment directory` on
    shared disk resource, and `local cache` directories for all participating
    worker machines. Doing so may result in data corruption.

.. note::

    (`OS Specific`) By convention, typical file keys are composed of capital
    letters, digits and underscore, for instance ``CFG``, ``PROBESET_2_GENEID``.
    However, it is possible to use, as file key, any regular file name `that is
    acceptable on the OS that handles shared disk resource`. Consult OS specific
    documentation for more details.

.. note::

    Internally, in the current implementation, the file objects are still
    stored as normal files, and file keys are used as real file names. Therefore,
    knowing the OS specific details of shared disk resource, as well as the file
    keys themselves, it is still possible to access the real file objects, in
    case of untraceable crash.


.. _logging:

Logging
-------

PPlus uses :mod:`logging` to record its activity during the execution of
experiment code.

The following logs are used:

- `experiment log`

This log is created by master code when `experiment ID` is granted. It
documents the activity of the master code regarding control of worker tasks
and interaction with Parallel Python. Also, all errors in worker tasks will be
logged here.
It is considered `private` and is `not` exposed through public :ref:`API <api>`.
When experiment is finished, it is available in the following location::

    <SHARED_DISK_PATH>/<experiment_ID>/experiment.log

- `master session log`

This log is created by master code when `experiment ID` and `session ID` are
granted.
It primarily documents the activity of the master code regarding remote file
access. It is considered `public` and is exposed through public :ref:`API <api>`.
When experiment is finished, it is available in the following location on master
machine::

    <LOCAL_CACHE_PATH>/<experiment_ID>/logs/<machine_name>.master.<session_ID>.log

- `session log`

This log is created by each single worker task, with `experiment ID` given and
`session ID` granted. It documents the activity of the worker code
regarding remote file access. It is considered `public` and is exposed through
public :ref:`API <api>`. When experiment is finished, it is available
in the following location on worker machine::

    <LOCAL_CACHE_PATH>/<experiment_ID>/logs/<machine_name>.worker.<session_ID>.log

.. note::

    Logs produced in ``<LOCAL_CACHE_PATH>`` are never transferred to shared disk
    resource after the experiment has been finished. They must be accessed
    manually on each machine.


.. _execution:

PPlus Execution modes
---------------------

Debug Mode
~~~~~~~~~~
Debug mode is intended to check the correctness of the experiment code, by
executing it as `local experiment`. Instead of distributing worker tasks to
remote machines, all of them will be executed on local machine, along with
master task.

In this mode:

1. PPlus ignores all configuration files and creates ``disk`` and ``cache``
   directories in current working directory::

     >>> import os
     >>> import pplus
     >>> cwd = os.getcwd()
     >>> pc = pplus.PPlusConnection(debug=True)
     >>> os.path.exists(os.path.join(cwd, 'disk'))
     True
     >>> os.path.exists(os.path.join(cwd, 'cache'))
     True

2. The master code is executed normally, and it 'distributes' all worker code
   pieces as usual, producing all regular files normally

3. When any exception is thrown during the execution of master code, the
   experiment code flow is interrupted, and the error is reported

4. When any exception is thrown during the execution of any worker task, the
   task is **not** resubmitted for another execution, the experiment code flow
   is interrupted, and the error is reported


Normal Mode
~~~~~~~~~~~
Normal mode is intended to run the experiment code over fully configured
parallel environment.

In this mode:

1. The master code is executed; during the initial phase, the following specific
   activities occur:

   - the master :class:`~pplus.PPlusConnection` instance is created,
     that reads properly specified configuration file (see :ref:`configuration`),
     obtaining, among others, ``DISK_PATH`` and
     ``CACHE_PATH`` locations `for that particular machine`

   - the experiment ID is granted, in the form of :mod:`uuid`

   - the session ID is granted, in the form of :mod:`uuid`

   - the `experiment directory` is created::

        <DISK_PATH>/<experiment_ID>

     all remote files produced by the whole experiment code will be stored there

   - the `local cache` for the experiment is created on that machine::

        <CACHE_PATH>/<experiment_ID>

     all temporary copies of remote files accessed by master code will be stored
     there

3. The master code continues its execution, eventually worker code pieces are
   distributed over worker machines.
   The master code keeps track of all distributed worker tasks, as well as of
   all completed worker tasks.

4. When some worker piece of code is distributed, together with experiment ID,
   to worker machine, then reconstructed according to Parallel Python rules, and
   started, the following specific activities occur:

   - from within worker code, the worker :class:`~pplus.PPlusConnection` instance
     is created that reads properly specified configuration file, obtaining,
     among others, ``DISK_PATH`` and ``CACHE_PATH`` locations
     `for that particular machine`

   - the experiment ID is re-used to access shared `experiment directory` in::

        <DISK_PATH>/<experiment_ID>

   - the worker session ID is granted, in the form of :mod:`uuid`

   - if does not exists, the `local cache` for the experiment is created for
     that machine::

        <CACHE_PATH>/<experiment_ID>

     all temporary copies of remote files, accessed by any worker code running
     on that machine within the experiment, will be stored there

   - the worker code piece continues its execution until the formal end (i.e.
     when the last statement has been processed, and/or function end has been
     reached)

     .. note::

        When any exception is thrown inside worker task, it is considered an
        `error` and the task is considered as `not completed`. Therefore, all
        worker tasks must be self-contained; deliberate exception propagation
        will lead to error.

     when the execution passes without errors, the worker task is considered
     `completed`

5. Master code, in the meanwhile, controls execution status of all distributed
   worker tasks periodically ('collects' them).

   When some worker task is marked as `not completed`, it is `resubmitted` for
   another execution, until it is marked as `completed`.

   .. note::

        The maximum number of re-submissions is controlled by
        ``JOB_MAX_RESUBMISSION`` parameter, specified for master machine
        (see :ref:`configuration`). Note that by default, the failed worker
        tasks are **not** resubmitted.

   .. note::

        Although the limit of re-submissions is available, the unnecessary
        overhead of computation time is still present for particular long tasks
        (that is, when task is failing constantly because of programming error).
        Therefore, it is advisable to design parallel code with caution using
        `Debug Mode`_, before trying it with `Normal Mode`_.

6. When any exception is thrown during the execution of master code, the
   experiment code flow is interrupted, and the error is reported

7. When master code has collected all distributed worker tasks, it finishes its
   execution until the formal end (i.e. when the last statement has been
   processed, and/or function end has been reached)

8. The experiment code has finished; assuming all configuration files pointed to
   the same shared disk resource, all the shared data are available in one
   `experiment directory`::

         <DISK_PATH>/<experiment_ID>


.. _submission:

PPlus job submission
--------------------

Starting with PPlus 0.5.2, jobs can be submitted in two ways.

Direct Mode
~~~~~~~~~~~

In direct mode, one passes `function object` to :meth:`~pplus.PPlusConnection.submit`.

This way, while convenient, has some limitations regarding scope of function in
Python code.

Technically, function object must be `unpicklable` by local/remote Parallel
Python worker. In case of unpickling error, the exception may vary;
see :mod:`pickle` for details on how `function objects` are pickled/unpickled.

This also means that function must be essentially `importable` on remote worker
machine(s), as well as for local worker(s). Most frequently this means proper
installation of module/package the function is defined in. See :mod:`distutils`
for more information about installing Python modules/packages.

.. note::

    If job function is in properly installed module/package, direct mode should be
    sufficient and less troublesome to use. For example, if job functions are
    from **numpy/scipy** packages, most likely those packages will be installed
    anyway on all involved PPlus machines.

Indirect Mode
~~~~~~~~~~~~~

In indirect mode, essentially ANY Python function can be submitted as job to
be executed by Parallel Python, bypassing the limitations of direct mode.

Here, the function object is NOT passed directly into
:meth:`~pplus.PPlusConnection.submit`. Instead, the following procedure is applied:

1. Full scope of function object (i.e. the module it is defined in) `must be`
   accessible through :data:`sys.path`; if not, it may be dynamically added.

   For example, if function is defined as "function1" in package "a.b.c", then
   "a.b.c" must be accessible through :data:`sys.path`.

2. Function object is added as one of the `depfuncs` (i.e. function object is
   added to `depfuncs` argument iterable).

3. `Function name` is passed as "function" argument to :meth:`~pplus.PPlusConnection.submit`.

Technically, the job function itself is then transported by Parallel Python as
`any other depfunc`, and then is recovered in proper scope on proper machine by
its name.

The indirect mode allows circumventing scope problems e.g. with submission of
functions from deep submodules.

.. note::

    The indirect mode is important in the following cases:

    - PPlus is used with Python module/package that is **not installed**, either
      on remote worker machine(s) or on local machine, or even both
    - PPlus user is **not in full control** of what could, or could not, be
      installed on involved machines

Example
~~~~~~~

.. note::

    In this example, we assume that module/package **mysoftware** is `not`
    installed, i.e. it is not accessible through `sys.path`.


The following function is defined in module **mysoftware.mod1.impl.Job**. The function
has no arguments and no dependencies (in sense of Parallel Python's depfuncs)::

    # module mysoftware.mod1.impl.Job
    # file Job.py

    # ...

    # job function
    def jobFunc():
        # job code here
        return result

    # ...

To submit it in direct mode, it is necessary to call :meth:`~pplus.PPlusConnection.submit`
within the scope of **mysoftware.mod1.impl.Job**, so the function object is pickled
and unpickled properly::

    # module mysoftware.mod1.impl.Job
    # file Job.py

    import pplus

    # ...

    # job function
    def jobFunc():
        # job code here
        return result

    # ...

    if __name__ == '__main__':
        # ...
        # create PPlus connection, here in debug mode
        pc = pplus.PPlusConnection(debug=True)
        # submit in direct mode
        pc.submit(jobFunc)
        pc.collect()

This works since current directory is always added to :data:`sys.path`.

If we have our submission code implemented in **mysoftware.main.job.Job**, submission
in direct mode is no longer possible, since the enclosing module (mysoftware.mod1.impl.Job)
is not visible and import is not sufficient::

    # module mysoftware.main.job.Job
    # file Job.py

    import pplus
    ##### -----> fails with import error
    from mysoftware.mod1.impl import jobFunc

    if __name__ == '__main__':
        # ...
        # create PPlus connection, here in debug mode
        pc = pplus.PPlusConnection(debug=True)
        # submit in direct mode
        pc.submit(jobFunc)
        pc.collect()

One can add `mysoftware.mod1.impl` to :data:`sys.path`, and dynamically import 'Job'
(see :func:`__import__` for more details), but this will cause different trouble::

    # module mysoftware.main.job.Job
    # file Job.py

    import pplus

    if __name__ == '__main__':
        # ...
        # create PPlus connection, here in debug mode
        pc = pplus.PPlusConnection(debug=True)
        # path to 'mysoftware' package
        MYSOFTWARE_ROOT_PATH = ...
        # add it to sys.path
        if MYSOFTWARE_ROOT_PATH not in sys.path:
            sys.path.append(MYSOFTWARE_ROOT_PATH)
        # dynamically import 'mysoftware.mod1.impl.Job' and obtain it
        jmod = __import__('mysoftware.mod1.impl', fromlist=['Job'])
        jmod = getattr(jmod, 'Job')
        # obtain job function
        jobFunc = jmod.jobFunc
        # submit in direct mode
        pc.submit(jobFunc)
        ##### -----> fails during job execution, most likely with ImportError
        pc.collect()

This time, function object is visible and properly submitted, but local/remote
worker(s) cannot `unpickle` it properly, and (most likely) result will be
ImportError thrown from within PP worker.

To submit such function successfully from within **mysoftware.main.job**, we need
indirect mode. Note that we still need to modify :data:`sys.path`::

    # module mysoftware.main.job.Job
    # file Job.py

    import pplus
    import sys
    import os
    from mysoftware.mod1.impl import jobFunc

    if __name__ == '__main__':
        # ...
        # create PPlus connection, here in debug mode
        pc = pplus.PPlusConnection(debug=True)
        # path to 'mysoftware' package
        MYSOFTWARE_ROOT_PATH = ...
        # add it to sys.path
        if MYSOFTWARE_ROOT_PATH not in sys.path:
            sys.path.append(MYSOFTWARE_ROOT_PATH)
        # dynamically import 'mysoftware.mod1.impl.Job' and obtain it
        jmod = __import__('mysoftware.mod1.impl', fromlist=['Job'])
        jmod = getattr(jmod, 'Job')
        # obtain job function
        jobFunc = jmod.jobFunc
        # INDIRECT MODE SUBMISSION
        depfuncs = list()
        # jobFunc is passed as Parallel Python depfunc
        depfuncs.append(jobFunc)
        # submit in indirect mode
        pc.submit(jobFunc.func_name, depfuncs=depfuncs)
        pc.collect()

Here, :attr:`func_name` is a string that contains function name. See :ref:`datamodel`
for more details.

Essentially, any Python function located anywhere can be submitted indirectly,
providing that it is accessible through :data:`sys.path` in the moment of
submission. Note that after submission, any dynamic entries added to
:data:`sys.path` may be removed if not needed anymore.

Indirect mode on PPlus earlier than 0.5.2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is still possible to use indirect mode on PPlus with version earlier than
0.5.2, since indirect mode is inherent feature of Parallel Python, and PPlus
0.5.2 offers only `support` for it. In such case, PPlus will very likely throw
exception similar to this one (as seen on Windows, Python 2.6)::

    Traceback (most recent call last):
      <...>
      <...>
      File "C:\Python26\lib\site-packages\pplus\_connection.py", line 480, in submit
        self._submit_task(function, args, depfuncs, modules)
      File "C:\Python26\lib\site-packages\pplus\_connection.py", line 597, in _submit_task
        tid=task_id)
      File "C:\Python26\lib\site-packages\pplus\core\pp.py", line 441, in submit
        (tid, args[0].func_name))
    AttributeError: 'str' object has no attribute 'func_name'


.. _depfuncs_name_clash:

Name clash with dependent functions
-----------------------------------

As a rule of thumb, **avoid using the same name for any depfunc and job function
at the same time**.

For example, if **mysoftware.main.jobs.func** depends on **mysoftware.impl.deps.func**,
in indirect mode `both` functions must be passed as depfuncs, and `both` will be
resolvable on target machine by Parallel Python only by their name `func`.
At the end, since both functions are instantiated in the same scope, only one
of them can be pickup by name, and second one is simply discarded and never
executed.

In such cases, what exactly happens during job execution, depends on may
independent factors, among them: how many arguments dependance function has,
the relative order of presence of both functions in "depfuncs" argument, etc.
The end result is unpredictable.

To avoid this, simply use different names whenever possible, e.g.
"**mysoftware.impl.deps.func**" and "**mysoftware.main.jobs.job_func**".
