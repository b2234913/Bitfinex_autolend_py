docker build --no-cache -t b2234913/auto_lend -f docker/Dockerfile .
docker rmi $(docker images -f “dangling=true” -q)