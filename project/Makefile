server-up:
	docker run \
    	-d \
    	-p 8500:8500 \
    	-p 8600:8600/udp \
    	--name=badger \
    	consul agent -server -ui -node=server-1 -bootstrap-expect=1 -client=0.0.0.0

members:
	docker exec badger consul members

client-up:
	docker run \
   	--name=client-${num} \
	consul agent -node=client-${num} -join=172.17.0.2

client-down:
	docker stop client-${num}

leave:
	docker exec badger consul leave
	docker rm badger

docker-clean:
	docker rm $(docker ps -a -q)
