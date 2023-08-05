A data-processing pipeline that guarantees that tasks exit the pipeline in the same order they came in, but
uses multiprocessing to parallelise them in the middle. You put callables and their arguments into the queue with
``put(task, *args, **kwargs)``. Each call to ``get()`` will return the result of executing a task, in the order the
tasks were added, but the ``task`` calls themselves run concurrently across multiple processes.

What would you use that for?
----------------------------

The use case that made me write this is logging completion of a large batch operation that contains many parallelisable
components; in our case, indexing a large number of documents. It's a multi-threaded system that (substantially
simplified) looks something like this::

    class BatchDone(int): pass  # marker for completion of an indexing batch

    def producer(queue):
        while True:
            doc_count = 0
            for document in get_document_batch():
                queue.put(indexing_func, document)  # callables get executed on the arguments you supply
                doc_count += 1
            queue.put(BatchDone(doc_count))  # non-callables get passed through, but still in FIFO order

    def consumer(queue):
        while True:
            result_or_batch_done = queue.get()  # either the return value of an indexing_func call, or the marker
            if isinstance(result_or_batch_done, BatchDone):
                log_progress(result_or_batch_done)

    queue = ParallelQueue()

    Thread(target=producer, args=(queue,)).start()
    Thread(target=consumer, args=(queue,)).start()

The advantage compared to the naive solution (execute each batch in parallel but wait until all have finished before
starting the next batch) is that a single slow document in a batch doesn't prevent the next batch from starting: it
only holds up the pipeline as a whole if the internal buffers fill up (by default these can accumulate ten times as
many out-of-order tasks as there are available CPUs).

Quick start guide
-----------------

Make a queue object::

    from parallel_queue import ParallelQueue
    queue = ParallelQueue(daemon=True) # there are a bunch of optionals for internal queue and buffer sizes

Put tasks and their data into the queue (not everything is allowed here, because of limitations on what can be passed
to the worker processes; see below for details)::

    queue.put(task_function, "data", timeout=5)  # NOT THREADSAFE! Only do this from one thread!

And get them out (usually on a different thread to the ``put()`` calls)::

    queue.get(timeout=1)

Clean up the queue when you're done with it (this is also NOT THREADSAFE: ``stop()`` should only be called from the
same thread as the ``put()`` calls)::

    queue.stop()  # send a "stop" signal through the pipes, but return immediately
    queue.join(timeout=2)  # join all worker and consumer processes (i.e. wait for queue to clear)

If you forget to do this and you didn't make your queue with ``daemon=True``, if it gets garbage-collected you may
see junk like this on stderr::

    Exception AssertionError: AssertionError() in <Finalize object, dead> ignored

I'm not certain how serious this is, but something is clearly not right so I suggest you avoid it if possible.

Finally, you can confirm that the shutdown is complete::

    if queue.is_alive():
        raise Exception("join() must have timed out!")

Limitations on what you can pass through the pipes
--------------------------------------------------

Behind the scenes the callable task and arguments that you ``put()`` is being sent to a worker process by
the ``multiprocessing`` standard library package. Most importantly, this means they have all to be picklable.
All the builtin types are picklable, but only classes and functions defined at the top level of a module can be pickled.
That means constructions like this are not going to work::

    def make_me_a_task_function(first):
        def task_function(second):
            return ' '.join((first, second))
        return task_function

    queue.put(make_me_a_task_function("curried"), "eggs")  # fails

Also, annoyingly, functions and classes defined by hand in a running interpreter session are *not* picklable, so if
you're playing around you'll have to use builtins or imported functions.

There's another limitation that you're not likely to run into, but which I include for completeness: various
cross-process synchronisation primitives are not allowed to be shared between processes by pickling.

The partial solution to both these problems is to use the slightly lower-level ``ParallelSingleTaskQueue`` instead of
``ParallelQueue``. It bakes in a single task function (so is less flexible) but shares it between processes by
inheritance rather than pickling (so non-top-level functions and multiprocess synchronisation primitives are fine).
See the test using the ``PermutationTask`` class for an example of this technique (and its disadvantages in terms of
readability).

Algorithm
---------

The basic algorithm is for the parallelisation is::

    ===================================
    Shared multiprocess-safe resources
    - (shared) Queue "worker_input" (fed from producer)
    - (shared) Queue "worker_output" (from worker to consumer)
    - (shared) Value "max_packet_id" (highest packet id consumer is willing to accept from any worker)

    Consumer private resources
      - next_packet_id (next packet id consumer wants to send on)
      - PriorityQueue "consumer_output_buffer" (buffer for packets that arrive at consumer out of order)

    Worker processes loop on:
    1. packet = worker_input.get()
    2. result = user_supplied_task(packet)
    3. while max_packet_id.value < packet.id: take a short nap
    4. worker_output.put(result-with-packet-id)

    Consumer process:
    1. next_packet_id = 0
    2. while True:
    3.     max_packet_id.value = next_packet_id + consumer_output_buffer.maxsize - 1
           # e.g. suppose buffer fits 5; waiting for 0 we can safely accept 1,2,3,4
    4.     while consumer_output_buffer.peek().packet_id != next_packet_id:
    5.         consumer_output_buffer.add(worker_output.get())
    6.     output(consumer_output_buffer.pop())
    7.     next_packet_id += 1
    ===================================

There are some complications (see `the code`_ for what they give rise to):

.. _`the code`: https://bitbucket.org/tikitu/parallel_queue/src/tip/parallel_queue/__init__.py

- ``PriorityQueue`` has no ``peek()``
- instead of "take a short nap", workers wait on an ``Event`` from the consumer (set whenever it progresses)
- packet ids should not be allowed to increase without limit: they wrap around and comparisons use modular arithmetic
- we need to be able to gracefully shut everything down when requested
- exception handling needs to expose stack traces from the worker processes
- reliable testing needs a tiny bit of information about internal progress of the algorithm

Installing
----------

It's on PyPI::

    $ pip install parallel-queue

Installing for hackery
----------------------

YMMV, but here's how I do it (you will need virtualenv_ installed, and pip_ to install ``nose`` to run the tests)::

    $ hg clone https://bitbucket.org/tikitu/parallel_queue
    $ cd parallel_queue
    $ virtualenv --no-site-packages .

.. _pip: http://www.pip-installer.org/en/latest/installing.html
.. _virtualenv: https://pypi.python.org/pypi/virtualenv

Running the tests::

    $ bin/pip install nose
    $ bin/nosetests
