#Erebus - a web dashboard for Tor relays
### Introduction

Erebus is a web dashboard for monitoring your Tor relay, providing a clean user interface to visualize information about your relay, such as bandwidth, logs, etc. Erebus consists of two parts: a server and a client. The server
is written in Python on top of [Stem](https://stem.torproject.org) and the
client is written using [AngularJS](https://angularjs.org).

* [Code](https://github.com/erebus/erebus)
* [Online UI demo](https://erebus.github.io)

### Getting started

First of all, you should know that erebus consists of two parts:

* **Erebus server**

This part is intented to be run on the same machine where your tor relay instance is running. Erebus server will connect to your relay through a tor control connection and fetch useful information, which will be made available for erebus client to request it.

* **Erebus client**

This part is intended to be run on a different machine (or the same, if you prefer it). Erebus client will connect to erebus server and get all the necessary information to display it on a nice dashboard.

### Running erebus

Before you run erebus, you should check the following Python dependencies:

* stem >= 1.4.0
* cyclone

You can install them by running pip install package.

Then you should be able to download and run erebus:

```
$ git clone https://github.com/erebus/erebus.git
$ cd erebus
$ python run_erebus.py
```

### Usage

The following options are available in erebus:

* ```--m or --mode [S|C|D]```
Indicates the mode in which erebus will run. **S** stands for server mode, **C** for client mode and **D** for dual mode, which means erebus will run both as server and client, integrating both functionalities in the current instance.

* ```--s or --server```
Indicates a valid interface ([server:]port) where the current erebus instance will try to connect for fetching information (if the current mode is client) or where the current instance will listen for clients (if the current mode is server).

* ```--p or --port```
Indicates a valid port where erebus will run. If the current mode is client, this port indicates where you will be able to open the client dashboard (e.g. localhost:8889), and if the current mode is server, this port indicates where erebus will listen for clients to connect.

* ```--i or --interface```
Indicates a valid interface ([server:]port) where erebus will try to connect for establishing a connection tor control. Ideally, this should be localhost on port 9051 (connectint to a relay on the same machine).

* ```--S or --socket```
Indicates a Unix socket path where erebus will try to connect for establishing a connection to tor control.

* ```-d or --debug```
Indicates a path where erebus will write a debug file with erebus logs.

* ```-l or --log```
Indicates which (tor or erebus) event types will be logged. See help for further details.

* ```-v or --version```
Provides information about current erebus version.

* ```-h or --help```
Provides help for running erebus.

### Repository Details [![Build Status](https://travis-ci.org/Jesse-V/OnioNS-client.svg)](https://travis-ci.org/Jesse-V/OnioNS-client)

This repository provides the client-side functionality and the integration with the Tor Browser.

### Supported Systems

**Debian 7 and 8, Ubuntu 14.04 - 15.10, Mint 17 - 17.2, Fedora 21 - 23**

Please see the [OnioNS-common README](https://github.com/Jesse-V/OnioNS-common#supported-systems) for more information.

### Installation

There are several methods to install the OnioNS software. The method of choice depends on your system. If you are on Ubuntu or an Ubuntu-based system (Lubuntu, Kubuntu, Mint) please use the PPA method. If you are running Debian Wheezy, please use the .deb method. Otherwise, for all other distributions, please install from source.

* **Install from PPA**

> 1. **sudo add-apt-repository ppa:jvictors/tor-dev**
> 2. **sudo apt-get update**
> 3. **sudo apt-get install tor-onions-client**

This is the recommended method as it's very easy to stay up-to-date with my releases.

* **Install from .deb file**

I provide builds for Debian Wheezy in the [Releases section](https://github.com/Jesse-V/OnioNS-client/releases) for several architectures. For other architectures, you may download from [my PPA](https://launchpad.net/~jvictors/+archive/tor-dev/+packages).

* **Install from source**

> 1. Install tor-onions-common by following [these instructions](https://github.com/Jesse-V/OnioNS-common#installation).
> 2. Download and extract the latest release from the [Releases page](https://github.com/Jesse-V/OnioNS-client/releases).
> 3. **(mkdir build; cd build; cmake ../src; make; sudo make install)**

If you are actively developing OnioNS, I have actively prepared two scripts, devBuild.sh and checkBuild.sh. Please see them for more information.

You can cleanup your build with **rm -rf build**

### Initialization

I strongly recommend that you follow the below procedures to integrate the software into the Tor Browser. This will make it extremely easy to access .tor domains, and I have made the software with the Tor Browser in mind. It is usually not necessary to do this process more than once.

> 1. Open a terminal and navigate to where you have extracted the Tor Browser. For example, on my machine this is *~/tor-browser_en-US* but you may have placed it somewhere else. You should see a "Tor Browser" executable and a directory named "Browser".
> 2. **mv Browser/TorBrowser/Tor/tor Browser/TorBrowser/Tor/torbin**
> 3. **ln -s /usr/bin/onions-tbb Browser/TorBrowser/Tor/tor**
> 4. **mkdir -p Browser/TorBrowser/OnioNS**

This replaces the normal Tor binary with a executable that launches the original Tor binary and then the OnioNS software as child processes, allowing the OnioNS software to start when the Tor Browser starts. This initialization is locale-independent, so all locales of the Tor Browser are supported.

### Usage

The Tor Browser operates as before, but the OnioNS software running in the background allows the Tor Browser to load hidden services under a .tor domain name.

> 1. Open the Tor Browser. OnioNS is compatible with any method of connecting to the Tor network.
> 2. Wait a few seconds for the background software to be ready.
> 3. Visit "example.tor" or any other .tor name that you know to be registered.
> 4. In a moment, the Tor Browser should load a hidden service.

OnioNS simply adds compatibility for .tor domains and lets all other domains go through, so you can browse the web as normal.

### Troubleshooting

If at startup the Tor Browser immediately throws a message saying "Something Went Wrong! Tor is not working in this browser." or if you get a message saying that Tor exited unexpectedly, it most likely means that the OnioNS software was unable to connect to its network. This is a fatal situation, so the software aborts and the Tor Browser throws this message. Please contact me (see below) for assistance.

If you are unable to load "example.tor", it's possible that either the hidden service is down or that the OnioNS software is not running properly on your end. Wait a few seconds, then try again. If it's still down, visit "onions55e7yam27n.onion". If the site loads, you could try closing and reopening the Tor Browser, which may clear the issue. If the site still does not load, please contact me for further assistance.

### Getting Help

If you have installed the software and then initialized the Tor Browser (again, a one-time operation) the software should work as intended. However, if something went wrong and you need assistance, please contact kernelcorn on #tor-dev on OFTC IRC, or email kernelcorn at riseup dot net (PGP key 0xC20BEC80). If you would like to report a bug or file an enhancement request, please [open a ticket on Github](https://github.com/Jesse-V/OnioNS-client/issues) or contact me over IRC or email if you do not have a Github account.

### How to Contribute

Most of all, I need more testers to verify that the software is stable and reliable. If you find an issue, please report it on Github. I am working on adding unit tests, which should help address many corner-cases and crashes for unexpected input. If are a developer, I gladly accept pull requests.



# erebus - web dashboard for Tor relays.
License TBA

Description:
Erebus is a web dashboard for monitoring Tor relays. It's designed to run
in 3 modes:

* Server: in this mode, erebus will connect to Tor (through stem), fetch
information and make it available through websockets (at address:port).
E.g. address:port/bandwidth , address:port/log

* Client: in this mode, erebus will connect to a running erebus server
(address:port), fetch information from it and show the data on localhost
(localhost:port/)

* Dual: in this mode, erebus will provide both server and client functionalities
on the same port. This is, currently, the recommended mode to run erebus.

### Example run of erebus

- python run_erebus.py -d -L A -D ./debug_log

This will run erebus with dual mode (-d) at default port (8888), log all events (-L A) and save
debug log to a file (-D ./debug_log).

- python run_erebus.py -d -L E5 -D ./debug_log -p 8585

Same as above, but logging error events (-L E5, see help) and running on port 8585.

- python run_erebus.py --help
```
  -a, --address ADDRESS           address where erebus server will run. Default is localhost
  -p, --port PORT                 port where erebus will serve and wait for clients
  -l, --listen-port PORT          port where erebus client will run.
  -i, --interface [ADDRESS:]PORT  change control interface from 127.0.0.1:9051
  -S, --socket SOCKET_PATH        attach using unix domain socket if present,
                                    SOCKET_PATH defaults to: /var/run/tor/control
  -C, --config CONFIG_PATH        loaded configuration options, CONFIG_PATH
                                    defaults to: ./erebus/config/erebusrc
  -D, --debug LOG_PATH            writes all erebus logs to the given location
  -L, --log EVENT_FLAGS           event types to be logged (default: N3)
        d DEBUG      a ADDRMAP           k DESCCHANGED   s STREAM
        i INFO       f AUTHDIR_NEWDESCS  g GUARD         r STREAM_BW
        n NOTICE     h BUILDTIMEOUT_SET  l NEWCONSENSUS  t STATUS_CLIENT
        w WARN       b BW                m NEWDESC       u STATUS_GENERAL
        e ERR        c CIRC              p NS            v STATUS_SERVER
                     j CLIENTS_SEEN      q ORCONN
          DINWE tor runlevel+            A All Events
          12345 erebus runlevel+         X No Events
                                         U Unknown Events
  -s, --server                    run in server mode, waiting for clients to connect
  -c, --client                    run in client mode, connecting to a erebus server
  -d, --dual                      run erebus with both server and mode running in the same machine
  -v, --version                   provides version information
  -h, --help                      presents this help
```

-------------------------------------------------------------------------------

FAQ:
> Why is it called 'erebus'?

Erebus is the primordial god of shadow in greek mythology, and is also the
consort of Nyx (a greek goddess) which turns out to be the name of the application
on which erebus is based: https://gitweb.torproject.org/nyx.git/

> Is this a stable version?

No. It's a development version and is intended for testing purposes.

> How can I contact erebus developers?

You can send me an email to clv@riseup.net, or if you prefer you can open
an issue on github.
