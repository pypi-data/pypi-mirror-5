====================================
 Topic Voting Plugin for OpenSlides
====================================

Version 1.0b1 (2013-06-30)

This plugin features a structured voting on topics using the
Sainte-Laguë method.


Requirements
============

OpenSlides 1.4c1 (http://openslides.org/)


Install
=======

This is only an example instruction for install Topic Voting Plugin for
OpenSlides on GNU/Linux. It can also be installed as any other python
package and on other platforms, e. g. on Windows.

1. Change to a new directory.

    $ mkdir OpenSlides

    $ cd OpenSlides

2. Setup and activate a virtual environment and install OpenSlides in it.

    $ virtualenv .venv

    $ source .venv/bin/activate

    $ pip install http://files.openslides.org/Beta/openslides-1.4c1.tar.gz

3. Download and extract sources from GitHub. Install the Topic Voting
   Plugin for OpenSlides.

    $ wget https://github.com/normanjaeckel/openslides-topicvoting/archive/1.0b1.zip

    $ unzip 1.0b1.zip

    $ pip install openslides-topicvoting-1.0b1

4. Start OpenSlides once to create its settings file if it does not exist yet.

    $ openslides

5. Stop OpenSlides.

6. Edit the settings.py file. You can find it in the directory openslides
   in your user config path given in the environment variable
   $XDG_CONFIG_HOME. Default is ``~/.config/openslides`` on GNU/Linux (and
   ``$HOME\AppData\Local\openslides`` on Windows). Insert the line
   'openslides_csv_export' into the INSTALLED_PLUGINS tuple.

     INSTALLED_PLUGINS = (
         'openslides_topicvoting',
     )

7. Synchronize the database to add the new tables:

    $ openslides --syncdb

8. Restart OpenSlides.

    $ openslides
