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
