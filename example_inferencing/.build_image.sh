IMAGE_NAME=tybalex/opni-gauss:inferencing
docker build . -t $IMAGE_NAME

docker push $IMAGE_NAME