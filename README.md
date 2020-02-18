# Bitfinex_autolend_py

## How to Run it?

### Download files

```
git clone https://github.com/b2234913/Bitfinex_autolend_py.git
cd Bitfinex_autolend_py
````

### Input your "API_Key" and "API_Secret" in "config.json" file

```
vim config.json
```

### Prepare docker image
```
docker pull b2234913/auto_lend
```
or build docker image by yourself
```
sh docker_build.sh
```

### Run docker contioner

```
docker run --restart=always -d -it \
  -v $(pwd)/config.json:/app/config.json \
  -w /app b2234913/auto_lend \
  python3 auto_lend.py
```

### Check auto lend status
get imformationo f container
```
docker ps -a 
```
go in container and check log file
```
docker exec -it <container id> bash
cat auto_lend.log
```