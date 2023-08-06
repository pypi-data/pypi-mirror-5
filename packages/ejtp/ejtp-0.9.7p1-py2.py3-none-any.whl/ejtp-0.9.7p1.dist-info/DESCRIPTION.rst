
Encrypted JSON Transport Protocol
---------------------------------

EJTP is an overlay protocol that allows the pluggable use of underlying transports, such as UDP, TCP, HTTP, IRC, Email and carrier pigeon to provide a cryptographically secure network of unreliable message forwarding. You can think of it as a bit like a more general-purpose and security-minded successor to XMPP, using JSON rather than XML as its frame medium.

On top of a simple frame format, EJTP boasts a consistent and simple format for describing encryption credentials, which is useful even without the rest of EJTP. The ejtp-crypto script makes it easy for other projects to take advantage of this pending a native port of ejtp.crypto to languages other than Python.

The intention of EJTP is to make it trivial to establish secure and NAT-oblivious distributed services across a common network of message relays. Your system only has to worry about exchanging encryption credentials and establishing a connection with a relay host, helping to pave the way toward distributed apps that run entirely in HTML5 (pending a port of the project to JS). You can be serverless *and* smartphone-friendly.

Optionally supports elliptic curve cryptography if the PyECC_ module is installed.

For more technical and in-depth information, visit the `Github project <https://github.com/campadrenalin/EJTP-lib-python>`_.

.. _PyECC: https://pypi.python.org/pypi/PyECC


