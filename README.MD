# Opni Gauss

## TEST
nats docker:
```
docker run -p 4222:4222 -ti nats:latest
```

fastapi backend:
```
uvicorn api_host:app --reload
```

job controller script:
```
python job_controller.py
```

### check gpu available
```
kubectl describe nodes  |  tr -d '\000' | sed -n -e '/^Name/,/Roles/p' -e '/^Capacity/,/Allocatable/p' -e '/^Allocated resources/,/Events/p'  | grep -e Name  -e  nvidia.com  | perl -pe 's/\n//'  |  perl -pe 's/Name:/\n/g' | sed 's/nvidia.com\/gpu:\?//g'  | sed '1s/^/Node Available(GPUs)  Used(GPUs)/' | sed 's/$/ 0 0 0/'  | awk '{print $1, $2, $3}'  | column -t
```
