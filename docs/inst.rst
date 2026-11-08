.. _inst:

Install and Run
===============

Install
-------

There are two ways to install ``autoremove-torrents``, but I highly recommend installing from pip. 

Install from pip
++++++++++++++++

.. code-block:: bash

   pip install autoremove-torrents

Install from GitHub
+++++++++++++++++++

.. code-block:: bash

   git clone https://github.com/jerrymakesjelly/autoremove-torrents.git
   cd autoremove-torrents
   python3 setup.py install

Install from Docker
+++++++++++++++++++

A prebuilt image is published on GHCR:

.. code-block:: bash

   docker pull ghcr.io/sysit/autoremove-torrents:1.6.1

Run it with your configuration mounted in (use ``--view`` first to preview what would be removed):

.. code-block:: bash

   docker run --rm \
     -v /path/to/config.yml:/etc/autoremove/config.yml:ro \
     -v /path/to/logs:/app/logs \
     ghcr.io/sysit/autoremove-torrents:1.6.1 \
     --view --conf /etc/autoremove/config.yml

The image also runs well as a Kubernetes CronJob. Mount the configuration from a ConfigMap; ``ENTRYPOINT`` is already ``autoremove-torrents``, so only ``args`` are needed:

.. code-block:: yaml

   apiVersion: batch/v1
   kind: CronJob
   metadata:
     name: autoremove-torrents
   spec:
     schedule: "0 * * * *"
     concurrencyPolicy: Forbid
     jobTemplate:
       spec:
         template:
           spec:
             containers:
             - name: autoremove
               image: ghcr.io/sysit/autoremove-torrents:1.6.1
               imagePullPolicy: IfNotPresent
               args: ["--conf", "/etc/autoremove/config.yml"]
               volumeMounts:
               - name: config-volume
                 mountPath: /etc/autoremove
             restartPolicy: OnFailure
             volumes:
             - name: config-volume
               configMap:
                 name: autoremove

Run
---

Just type the following command line in your terminal:

.. code-block:: bash

   autoremove-torrents

``autoremove-torrents`` will look for the ``config.yml`` in the current working directory. For more command line arguments, please see the table below.

Arguments List
++++++++++++++

.. note::

   When you are using the full name of the arguments, you need to lead the values of the arguments with a equal sign. But if you are using the abbreviation, you only need a space to lead the argument values.

.. list-table::
   :header-rows: 1

   * - Arguments
     - Argument Abbreviations
     - Description
   * - `--view`
     - `-v`
     - Run and see which torrents will be removed, but don't really remove them.
   * - `--conf`
     - `-c`
     - Specify the path of the configuration file.
   * - `--task`
     - `-t`
     - Run a specific task only. The argument value is the task name. An unknown task name is reported with the list of available tasks.
   * - `--log`
     - `-l`
     - Specify the path of the log file.
   * - `--debug`
     - `-d`
     - Enable debug mode and output more logs.

Exit Codes
++++++++++

``autoremove-torrents`` exits with ``0`` on success, ``1`` when the configuration is invalid or one or more tasks fail (e.g. login failure, connection failure), and ``255`` when the command line arguments are invalid. Schedulers such as cron can use the exit code to detect failed runs.

For example:

.. code-block:: bash

   autoremove-torrents --view --conf=/home/myserver/autoremove-torrents/config.yml

Also, it equals to:

.. code-block:: bash

   autoremove-torrents -v -c /home/myserver/autoremove-torrents/config.yml


Uninstall
---------

Uninstall from pip
++++++++++++++++++

If your autoremove-torrents was installed via pip, you can simply uninstall it by using pip:

.. code-block:: bash

    pip uninstall autoremove-torrents


Uninstall manually
++++++++++++++++++

However, if it was installed by ``setup.py``, you need to remove all the files manually.

Step1
#####

.. code-block:: bash

    cd autoremove-torrents


Step2
#####

Reinstall the program and record which files were copied:

.. code-block:: bash

    python3 setup.py install --record files.txt


Step3
#####

Use ``xargs`` to remove each file:

.. code-block:: bash

    cat files.txt | xargs rm -rf


Or if you're running Windows, use Powershell:

.. code-block:: ps1

    Get-Content files.txt | ForEach-Object {Remove-Item $_ -Recurse -Force}


Reference: `https://stackoverflow.com/questions/1550226/python-setup-py-uninstall <https://stackoverflow.com/questions/1550226/python-setup-py-uninstall>`_