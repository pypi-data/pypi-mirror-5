pysiriproxy
===========

About
-----

pysiriproxy is a port of [SiriProxy](https://github.com/plamoni/SiriProxy) (by
@plamoni) from Ruby to Python developed.


Installing pysiriproxy
----------------------

The following page contains step by step instructions for installing
pysiriproxy on an Ubuntu system. These instructions have been tested on
the following Ubuntu versions: 10.04, 11.10, and 12.04.

Installing and configuring dnsmasq
++++++++++++++++++++++++++++++++++

In order to intercept the commands being sent from the iPhone to Apple’s
server you must install a program called *dnsmasq* onto a machine that
will be connected to the same network as the iPhone. The following
provides instructions on properly installing dnsmasq.

Run the following commands::

    $ sudo apt-get install dnsmasq

Now, open the file **/etc/dnsmasq.conf** with the editor of your choice.

Search for **#address=/double-click.net/127.0.0.1** (this should be
roughly the 62nd line). Once the line is found, replace that line with
the following two lines::

    address=/guzzoni.apple.com/(your_machine's_ip_address).
    address=/kryten.apple.com/(your_machine's_ip_address).

Be sure to replace your machine’s IP address and then save the file.
This will allow the pysiriproxy server accept connections from devices
using either iOS 5 or iOS 6.

Finally, restart dnsmasq for the new IP address to take effect::

    $ sudo /etc/init.d/dnsmasq restart

The above installation sequence was taken from `How to install Siri
Proxy <http://www.iphonestuffs4u.com/how-to-install-siri-proxy/>`_.

Once pysiriproxy has been installed and configured you can follow the
instructions on `*changing the dnsmasq IP
address* <configuration.html#changingdnsmasqip-label>`_ to easily change
the IP address used by dnsmasq.

Current maintainer
++++++++++++++++++

Andreas Jung <andreas@andreas-jung.com>

