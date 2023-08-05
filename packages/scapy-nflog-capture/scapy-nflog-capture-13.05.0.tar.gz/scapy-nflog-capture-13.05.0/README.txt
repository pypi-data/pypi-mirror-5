scapy-nflog-capture
-------------------

Driver for `scapy network manipulation
tool <http://www.secdev.org/projects/scapy/>`_ to allow capturing
packets via `Linux NFLOG
interface <http://wiki.wireshark.org/CaptureSetup/NFLOG>`_.

Installation
------------

It's a regular package for Python 2.7 (not 3.X).

Using `pip <http://pip-installer.org/>`_ is the best way:

::

    % pip install scapy-nflog-capture

If you don't have it, use:

::

    % easy_install pip
    % pip install scapy-nflog-capture

Alternatively (`see
also <http://www.pip-installer.org/en/latest/installing.html>`_):

::

    % curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python
    % pip install scapy-nflog-capture

Or, if you absolutely must:

::

    % easy_install scapy-nflog-capture

But, you really shouldn't do that.

Current-git version can be installed like this:

::

    % pip install 'git+https://github.com/mk-fg/scapy-nflog-capture.git#egg=scapy-nflog-capture'

Requirements
~~~~~~~~~~~~

-  Python 2.7 with ctypes support
-  `scapy <http://www.secdev.org/projects/scapy/>`_
-  `CFFI <http://cffi.readthedocs.org>`_ (for libnetfilter\_log
   bindings)
-  `libnetfilter\_log <http://netfilter.org/projects/libnetfilter_log>`_

CFFI uses C compiler to generate bindings, so gcc (or other compiler)
should be available if module is being built from source or used from
checkout tree.

Usage
-----

Two python modules are installed: scapy\_nflog and nflog\_ctypes.

scapy\_nflog has NFLOGListenSocket class (implementing SuperSocket),
which can be installed as default L2 listener like this:

::

    >>> import scapy_nflog
    >>> scapy_nflog.install_nflog_listener()

install\_nflog\_listener above is a one-line function, doing
``conf.L2listen = NFLOGListenSocket``, so if you're building custom
module on scapy, NFLOGListenSocket class can just be passed directly to
scapy internals a listening socket without setting it to be default one.

IDs of NFLOG queues to grab packets from can be controlled via passing
optional "queues" keyword on instance init (int or a list of ints) or by
overriding default "queues" class attribute in a subclass and setting
that one as listener class instead.

Note that NFLOG actually returns L3 packets, so despite the listener
being installed as L2 above, it will always return instances of IP
class, not Ether or such.

Linux NFLOG
~~~~~~~~~~~

NFLOG is a Linux `netfilter <http://www.netfilter.org/>`_ subsystem
target, somewhat like old and simple LOG target, which dumped info for
each packet to kmsg, but using special netlink queues to export
netfilter-matched (think
`iptables <http://www.netfilter.org/projects/iptables/index.html>`_
rules) packets to userspace.

To export all sent/received packets via nflog:

::

    iptables -t raw -I PREROUTING -j NFLOG
    iptables -t raw -I OUTPUT -j NFLOG

Of course, any arbitrary filters can be added there, to dump only
packets matching specific protocol, port or whatever arbitrary netfilter
matcher - see `iptables
manpage <http://ipset.netfilter.org/iptables.man.html>`_ (or
iptables-extensions(8)) for the list/info on the ones shipped with
mainline linux.

Note that it's safe to add the above catch-all rules, as with no
listeners (nothing queries nflog for these packets), they'll just be
discarded regardless of these rules and won't be wasting much ram, cpu
or anything like that.

Userspace readers (like this module) can subscribe to receive these
packets, setting how many bytes of these will be buffered in-kernel for
later recv() calls (optional "nlbufsiz" keyword to nflog\_generator),
the rest will be just dropped (producing python logging warning by
default, unless ``handle_overflows=False`` is passed) until userspace
catches up.

NFLOG itself is configurable with parameters like --nflog-group and
--nflog-range (see iptables-extensions(8)), allowing to have multiple
nflog queues for different apps and not passing lots of useless L7 data
around.

Performance - especially coupled with in-kernel noise filtering and
packet truncation - seem to be more efficient than simpler approaches
like using AF\_PACKET/SOCK\_RAW sockets, but it's highly unlikely to be
any kind of a bottleneck with scapy sitting on top of it anyway.

One interesting advantage over libpcap is the ability to capture
tunneled packets after decryption (traffic coming from ipsec, pptp,
openvpn, ssh, etc) or transformation (stripping of ipip wrapping,
netlink re-injection and such) here.

nflog\_cffi
~~~~~~~~~~~

scapy\_nflog is based on nflog\_cffi module, which can be used from any
python code (scapy shell included):

::

    from nflog_cffi import NFLOG

    # without extra_attrs just packet payload (possibly truncated) is returned
    nflog = NFLOG().generator(0, extra_attrs=['len', 'ts'], nlbufsiz=2*2**20)
    fd = next(nflog) # netlink fd to do select/poll on, if necessary

    # pkt_len is the *real* length, before nflog-truncation (if any)
    # pkt_ts is the packet timestamp, as reported by kernel/lib
    pkt, pkt_len, pkt_ts = next(nflog)
    print('Got packet, len: {}, ts: {}'.format(pkt_len, pkt_ts))

    for pkt, pkt_len, pkt_ts in nflog: # do stuff with each captured packet

Module uses libnetfilter\_log via CFFI.

NFLOG generator has the keywords to control parameters of netlink socket
that are passed to libnetfilter\_log, see `libnetfilter\_log
documentation <http://www.netfilter.org/projects/libnetfilter_log/doxygen/group__Log.html>`_
for more verbose description of these.

Not all `libnetfilter\_log-exposed
attributes <http://www.netfilter.org/projects/libnetfilter_log/doxygen/group__Parsing.html>`_
are exposed through bindings.
