IMAGE_NAME=tybalex/opni-gauss:training
docker build . -t $IMAGE_NAME

docker push $IMAGE_NAME