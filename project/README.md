# Distributed Key-Value store with Consul
To run, you must have Consul installed and running (docker works too). Please configure setup.py to determine the initial number of nodes. When server_consumer.py is run, it will automatically scan for nodes on consul and take care of threading. Lastly, when client_producer.py is started, it will also scan for the number of available consul nodes and distributed data among them. Client-producer.py will demonstrate Round Robin, HRW Hashing, and Consistent Hashing, in that order. Finally, it will display the functionality of adding and removing nodes from the consul cluster and deal with the data accordingly. Statistics for data density is reported along every step of the way.

<p>If you have a docker image of consul, you can start a consul server yourself with something like <code>
    docker run \
        -d \
        -p 8500:8500 \
        -p 8600:8600/udp \
        --name=badger \
        consul agent -server -ui -node=server-1 -bootstrap-expect=1 -client=0.0.0.0</code>.
  If you have GNU make, you can run <code>make server-up</code> to start up a server </p>
<p>Once the server is up, you can load some initial nodes with <code>python setup.py</code> to run the setup script. To change the number of nodes, go ahead and change the script parameters.</p>
<p>At this point, you can run the server code and client code with <code>python server_consumer.py</code> and <code>python client_producer.py</code> respectively.</p>
