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
