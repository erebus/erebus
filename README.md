#Erebus - a web dashboard for Tor relays
### Introduction

Erebus is a web dashboard for monitoring your Tor relay, providing a clean user interface to visualize information about your relay, such as bandwidth, logs, etc. Erebus consists of two parts: a server and a client. The server
is written in Python on top of [Stem](https://stem.torproject.org) and the
client is written using [AngularJS](https://angularjs.org).

* [Code](https://github.com/erebus/erebus)
* [Online UI demo](https://erebus.github.io)

**Erebus is currently under active development and should not be considered as a stable software.**

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

You can install them by running pip install name_of_package.

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

* ```--t or --tls```
Indicates that we want to run erebus with TLS support. For this to work you should have your key and certificate files in the same path where you are running erebus, and they should have the name: **erebus_key.pem** and **erebus_cert.pem**. Future improvements should allow to specify custom filenames for this option.

**A note about certificates**: a very quick guide to generate self-signed certificates is the following:

```
openssl genrsa -out erebus_key.pem
openssl req -new -key erebus_key.pem -out csr.pem
openssl x509 -req -days 365 -in csr.pem -signkey erebus_key.pem -out erebus_cert.pem
rm csr.pem
```
I hope to explain this process with more details in the short time.

* ```--i or --interface```
Indicates a valid interface ([server:]port) where erebus will try to connect for establishing a connection tor control. Ideally, this should be localhost on port 9051 (connectint to a relay on the same machine).

* ```--S or --socket```
Indicates a Unix socket path where erebus will try to connect for establishing a connection to tor control.

* ```-c or --config```
Indicates a path for reading erebus config options.

* ```-d or --debug```
Indicates a path where erebus will write a debug file with erebus logs.

* ```-l or --log```
Indicates which (tor or erebus) event types will be logged. See help for further details.

* ```-v or --version```
Provides information about current erebus version.

* ```-h or --help```
Provides help for running erebus.

### Example usage

The following are some examples of useful usages of erebus:

Running erebus on your localhost relay.
```
python run_erebus.py
[INFO] Erebus is running on port 8887 with dual mode.
[INFO] Erebus server is located at http://127.0.0.1:8887
```
Then, you should go to http://127.0.0.1:8887 to see erebus dashboard.

Same as above, but with TLS support.
```
python run_erebus.py -t
[INFO] Erebus is running on port 8887 with dual mode.
[INFO] Erebus server is located at https://127.0.0.1:8887
```
Then, you should go to https://127.0.0.1:8887 and accept the self-signed certificate, and then you'll be able to see erebus dashboard.


Running erebus on your localhost relay, with separated server and client.
```
python run_erebus.py -m S -p 9876
[INFO] Erebus is running on port 9876 with server mode.
[INFO] Erebus server is located at http://127.0.0.1:9876
```
You won't be able to see the dashboard yet, as erebus is running on server mode only. You'll need to run a separate client instance on a different port:
```
python run_erebus.py -m C -p 9877 -s 9876
[INFO] Erebus is running on port 9877 with client mode.
[INFO] Erebus server is located at http://127.0.0.1:9876
```
Then, you should go to http://127.0.0.1:9877 to see erebus dashboard, which will be connecting to http://127.0.0.1:9876 to fetch information.


### Getting Help

If you are interested on tryin out erebus, and you have any problem, please contact **clv** on #tor-dev on OFTC IRC, or email clv at riseup dot net. If you would like to report a bug or file an enhancement request, please [open a ticket on Github](https://github.com/erebus/erebus/issues) or contact me over IRC or email if you do not have a Github account.

### How to Contribute

Contributions are welcome! Whether you would like to test erebus or to develop functionalities (backend or frontend). In any case, don't hesitate to contact either **atagar** or **clv** and ask for guidance on what would be useful at the moment.

### License

Erebus is licensed under a BSD license. See LICENSE file for more information.

### Short FAQ

* **Why is it called 'erebus'?**

Erebus is the primordial god of shadow in greek mythology, and is also the
consort of **Nyx** (a greek goddess) which turns out to be the name of the application
on which erebus is based: https://gitweb.torproject.org/nyx.git/

* **How did 'erebus' come to life?**

Erebus was initially conceived by [Damian Johnson](https://atagar.com) as a web version of [nyx](https://gitweb.torproject.org/nyx.git). The project was listed on the [volunteers](https://www.torproject.org/getinvolved/volunteer.html.en) section in torproject.org and it was then taken and developed by **clv** during **Tor Summer of Privacy 2015**.

* **Is this a stable version?**

No. It's a development version and is intended for testing purposes.
