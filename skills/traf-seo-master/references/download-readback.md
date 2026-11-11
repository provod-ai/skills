# Verify the actual download protocol

The download-parity check covers server-delivered and client-generated files.
The acceptance remains agreement of the advertised revision, filename, MIME
type, saved bytes, length, hash and useful content.

Record the delivery scheme and initiating URI. For HTTP(S), retain the actual
request, final URL/status, response headers, redirects and downloaded bytes.
Review Content-Type, Content-Disposition and relevant access/cache behavior.
For data/blob delivery, retain the browser action, initiating URI, declared
type, proposed/suggested filename and the actual saved file. A URI or a Blob in
memory alone is not proof that the advertised file was downloaded.

The delivery-protocol facet is protocol-appropriate evidence. Never label
data/blob handling as a raw HTTP transaction or invent response headers.
Missing or stale bytes, mismatched contents or an unobserved download remain
unverified. Server downloads still require their real HTTP evidence.

The generic Master validator checks artifact hashes, identity, coverage and
facet joins. The native actor must review the meaning of the protocol fields;
it does not automatically parse every HTTP header or validate CSV semantics.

The correction replaces revision 2's unconditional raw-http facet for this
one criterion. It preserves all download-bytes, publication-binding and
source-review requirements and the full 145-check universe.

Primary basis, inspected 2026-11-06:

- [HTML download processing](https://html.spec.whatwg.org/multipage/links.html#downloading-resources) defines the download attribute and filename processing, including data URLs.
- [Fetch scheme handling](https://fetch.spec.whatwg.org/#scheme-fetch) handles data/blob separately from HTTP(S), producing the applicable response/body from their own source.