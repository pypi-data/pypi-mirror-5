===================
infrae.maildrophost
===================

``infrae.maildrophost`` is used to configure a maildrophost server and
`MaildropHost`_ product using the same configuration, and create a
management script for the maildrophost server.

In addition to those tasks, it used to download and install
`MaildropHost`_ when it was not distributed as an egg. If you are
looking for those features, please have a look at the version 1.x of
this recipe.

Example in buildout::

  [buildout]
  parts =
      maildrophost
      instance

  [maildrophost]
  recipe = infrae.maildrophost
  smtp_host = localhost
  smtp_port = 25

  [instance]
  ...
  eggs +=
     Products.MaildropHost
  zope-conf-additional +=
  <product-config maildrophost>
    config-path-application ${maildrophost:maildrophost.cfg}
  </product-config>


This will create the configuration file ``maildrophost.cfg`` for the
daemon, and put a start/stop script in the ``bin`` directory of the
buildout tree.

Spool and PID files are put by default in the ``var/maildrop``
directory, so data is preserved when update (if there is any data).

Settings
========

You can customize some of settings of `MaildropHost`_:

``mail_dir``
  Directory to use as *home directory* for the deamon. By default it's
  ``${buildout:directory}/var/maildrop`` It will be created if it
  doesn't exists.

``spool_dir``
  Directory to use as a spool. By default it will be
  ``${mail_dir}/spool``. The directory will be created if it doesn't
  exist already.

``pid_file``
  PID file to use for the daemon. By default it will be
  ``${mail_dir}/maildrop.pid``.

``smtp_host``
  SMTP server to use. Default to localhost.

``smtp_port``
  Port to use. Default to default SMTP port, 25.

``login``
  If the SMTP server require authentication, login to use.

``password``
  If the SMTP server require authentication, password to use.

``tls``
  If 1, `MaildropHost`_ will be speaking to a TLS enabled SMTP server.

``batch``
  Set ``MAILDROP_BATCH``.

``add_messageid``
  Add a message id to the sent mail.

``pool_interval``
  Must be an integer which define the interval in seconds between two
  check for new mail in the spool directory. Default is 120 seconds.

``wait_interval``
  Must be an interger or float which say how much time the daemon
  should wait between sending two mails to the mail server.

``supervised_daemon``
  If 1, the internal maildrop script will remain running in the
  foreground.  This is mostly useful when you start the main
  maildrophost script itself on the foreground with ``bin/maildrophost
  fg``.  See the `Configuration for supervisor`_ section.

``maildrophost.cfg``
  Specify an alternative path for storing the generated
  ``maildrophost.cfg`` file.  Note that this file gets rewritten each
  time you run buildout.  The default value is
  ``${buildout:directory}/maildrophost.cfg``.


Configuration for supervisor
============================

Buildout generates a ``bin/maildrophost`` script (if you use
``maildrophost`` as the name of the buildout section).  When calling
``bin/maildrophost start`` this script does some checks and basically
calls ``python maildrop.py maildrophost.cfg`` and quits, without
waiting to for the ``maildrop.py`` script to exit properly.  The
``maildrop.py`` script creates a fork of itself and exits.

This is not helpful when you want to use maildrophost in combination
with `supervisor <http://supervisord.org>`_.  If you want to do that
you should enable the ``supervised_daemon`` option and let supervisor
start the maildrophost script on the foreground.  Sample config would
be this::

  [maildrophost]
  recipe = infrae.maildrophost
  smtp_host = localhost
  smtp_port = 25
  supervised_daemon = 1

  [supervisor]
  recipe = collective.recipe.supervisor
  ...
  programs =
      ...
      40 maildrop ${buildout:directory}/bin/maildrophost [fg] true


Latest version
==============

The latest version is available in a `Subversion repository
<https://svn.infrae.com/buildout/infrae.maildrophost/trunk>`_.

.. _MaildropHost: http://www.dataflake.org/software/maildrophost
