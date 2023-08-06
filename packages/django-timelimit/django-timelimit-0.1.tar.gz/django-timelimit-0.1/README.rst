Django Timelimit
================

Django-timelimit allows you to wrap sections of Django templates with a
timeout to enforce an upper bound on render time. When the templates exceeds
this time, an alternative fragment is rendered instead::

    {% load timelimit %}

    {% timelimit 0.05 %}
      {# perform a potentially very slow operation #}
      <p>No timeout occurred</p>
      {% sleep 0.5 %}
    {% else %}
      <p>Sorry, couldn't render the fragment in time.</p>
    {% endtimelimit %}


Installation
------------
::

    $ pip install django-timelimit


Reentrant
---------

Django-timelimit is fully reentrant, which means that you can have nested
timeouts::

    {% load timelimit %}

    {% timelimit 0.10 %}
      {# perform a potentially very slow operation #}

        {% timelimit 0.05 %}
          {# perform another potentially slow operation #}
        {% else %}
          <p>Sorry, couldn't render the nested fragment in time.</p>
        {% endtimelimit %}

      <p>No timeout occurred</p>
    {% else %}
      <p>Sorry, couldn't render the fragment in time.</p>
    {% endtimelimit %}

Nested timeouts allow a large outer timeout to contain smaller timeouts. If the
inner timeout is larger than the outer timeout, it is treated as a no-op.


Quotas
------

Interruptingcow quotas (introduced in interruptingcow 0.7) are supported too,
allowing you to share a single allocation of time between different timelimit
tags::

    {% load timelimit %}

    {% for foo in bar %}
      {% timelimit quota_var %}
        ...
      {% else %}
        ...
      {% endtimelimit %}
    {% endif %}

This is useful in loops where you do not want the total render time to go up
with the number of iterations of the loop.


Caveats
-------

Django-timelimit is based on interruptingcow and so it shares its limitations.
Interruptingcow uses ``signal(SIGALRM)`` to let the operating system interrupt
program execution, meaning:

1. Python signal handlers only apply to the main thread, so you cannot use this
   from other threads (this also means you cannot use this in a multithreaded
   webserver, or even ones that use a background thread for request handling
   (Gunicorn works great).
2. You must not use this in a program that uses ``SIGALRM`` itself (this
   includes certain profilers)
