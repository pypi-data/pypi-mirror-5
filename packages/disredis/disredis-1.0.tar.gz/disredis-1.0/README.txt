========================
Distributed Redis client
========================

Distributed Redis Client (disredis) to enable real-time failover of 
redis masters to paired slaves, providing improved availability and reliability 
where needed.

The DisredisClient class can be used in place of a StrictRedis client. 
Instead of passing the host and port in, pass in a list of Sentinel addresses in
the form of "host:port". It will connect to the first responding Sentinel
and query it for masters that it knows about. These masters will become the
nodes that are sharded across. As long as the number of masters does not
change, the sharding will be stable even if there is a node failure.

Node failures are handled by asking the Sentinel for the updated master of
the given node. During the initial failure, some requests may error out
with a ConnectionError if they are made between when the node fails and
when Sentinel executes the fail-over procedure.

Redis and Sentinel Configuration
================================

We recommend using at least Redis version 2.6.13.

For testing you need a minimum of two sentinels and two redis instances 
(one master and one slave) to test fail over.

For production we recommend at least two servers. Each server should run 
two sentinels and at least one master and one slave redis instance, 
running on opposite servers.
::
    |   Server One   |    |   Server Two   |
    |----------------|    |----------------|
    | Sentinel01     |    | Sentinel03     |
    | Sentinel02     |    | Sentinel04     |
    | Redis01-Master |    | Redis01-Slave  |
    | Redis02-Slave  |    | Redis02-Master |
    | ...            |    | ...            |

**Important:** If you are running on AWS please ensure your django servers 
can connect to the internal IP of the AWS redis servers. AWS ec2 instances 
resolve to their internal IP which results in sentinels returning the 
internal IP when queried. To check the IP address of redis instances run 
the following command:

    redis-cli -p <SENTINEL PORT, e.g. 26379> sentinel masters

Example Sentinel Configuration:

    port  26379 #Sentinel Port

    sentinel monitor redis-Redis1 server1.com 6382 2
    sentinel down-after-milliseconds redis-Redis1 60000
    sentinel failover-timeout redis-Redis1 900000
    sentinel can-failover redis-Redis1 yes
    sentinel parallel-syncs redis-Redis1 1

    sentinel monitor redis-Redis2 server2.com 6383 2
    sentinel down-after-milliseconds redis-Redis2 60000
    sentinel failover-timeout redis-Redis2 900000
    sentinel can-failover redis-Redis2 yes
    sentinel parallel-syncs redis-Redis2 1

Please check the redis documentation for more details on Redis and 
Sentinel installation and configuration.

We also recommend using Supervisor or similar to manage the various 
Redis and Sentinel instances.

Django Setup
============

Either download from github and run
    
    python setup.py install

or

    pip install disredis

Add the disredis code to the django app.

Add the following to django settings

    SESSION_COOKIE_AGE = 2592000 # thirty days - Adjust to your needs

    SESSION_REDIS_PREFIX = '<REPLACE - e.g. mysessions>'
    SESSION_REDIS_HOST = 'localhost'
    SESSION_REDIS_DB = 6

    SESSION_ENGINE = 'disredis_sessions.session'

    SESSION_REDIS_SENTINEL_URLS = [
        'SENTINEL_SERVER:SENTINEL_PORT',
        ...]

Restart django to start using Redis for user sessions

Troubleshooting
===============

Ensure the django application servers can connect to the redis 
and sentinel ports.

Run the following command on the redis servers to check all 
redis instances are listed (check IP and master/slave status):

    $ redis-cli -p <SENTINEL PORT, e.g. 26379> sentinel master
