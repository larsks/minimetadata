# minimetadata

This is a very simple implementation of the OpenStack/EC2 metadata
service.  It listens by default on port 8775 and serves data defined
in a YAML configuration file.

## Configuration

Here is a sample configuration file:

    meta-data:
      public-keys/0/openssh-key: '@~lkellogg/.ssh/id_rsa.pub'
      instance-id: i-{{client_ip_as_hex}}
    user-data: |
      #!/bin/sh
      rsync -rp /home/cloud/.ssh/ /root/.ssh
      fixfiles restore /root/

This sets the metadata key `public-keys/0/openssh-key` to the contents
of `~lkellogg/.ssh/id_rsa.pub`, and sets `instance-id` to a value
derived from the ip address of the requesting client.  This also sets
`user-data` to a simple shell script.

Generally:

- A request to `.../meta-data/foo` will return the value of `foo`
  under the `meta-data` key in your YAML file.
- If the value starts with `@`, the remainder of the value will be
  interpreted as a filesystem path and the contents of that file will
  be returned to the client.

## Access from your instances

Cloud images expect to access your metadata server at <http://169.254.169.254>.  To make this work, you'll need to make a few changes on your system.

The following rules (to be added to your `nat` table) will redirect
traffic to 169.254.169.254 port 80 to port 8775.  The `OUTPUT` rule is
necessary for locally originated traffic.

    -A OUTPUT_direct -d 169.254.169.254/32 -p tcp -m tcp --dport 80 -j REDIRECT --to-ports 8775
    -A PREROUTING_direct -d 169.254.169.254/32 -p tcp -m tcp --dport 80 -j REDIRECT --to-ports 8775

You will also need to add that address to a local interface.  I've
added it to `lo` by placing the following in
`/etc/sysconfig/network-scripts/icfg-lo-range`:

    IPADDR_START=169.254.169.254
    IPADDR_END=169.254.169.254

This should work on RHEL, Fedora, and derivatives.

