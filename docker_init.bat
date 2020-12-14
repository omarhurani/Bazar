:: Create a docker network for containers to run in
:: This enables each container to be assign an IP address, which matches the one in the env vars files
docker network create --gateway 172.18.0.1 --subnet 172.18.0.0/16  -d bridge "bazar"


:: Create a docker image for each server
docker build -t bzr-catalog:latest ./bzr-catalog
docker build -t bzr-order:latest ./bzr-order
docker build -t bzr-front-end:latest ./bzr-front-end


:: Run the 3 images in 5 containers (1 front-end, 2 order, 2 catalog)
docker run -d --env-file ./env-vars/order1.txt -it --network "bazar" --ip 172.18.0.51 -p 5001:5000 --name BazarOrderServer1  bzr-order:latest
docker run -d --env-file ./env-vars/order2.txt -it --network "bazar" --ip 172.18.0.61 -p 6001:5000 --name BazarOrderServer2  bzr-order:latest
docker run -d --env-file ./env-vars/catalog1.txt -it --network "bazar" --ip 172.18.0.50 -p 5000:5000 --name BazarCatalogServer1  bzr-catalog:latest
docker run -d --env-file ./env-vars/catalog2.txt -it --network "bazar" --ip 172.18.0.60 -p 6000:5000 --name BazarCatalogServer2  bzr-catalog:latest
docker run -d --env-file ./env-vars/front-end.txt -it --network "bazar" --ip 172.18.0.52 -p 5002:5000 --name BazarFrontEndServer  bzr-front-end:latest
