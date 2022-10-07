IMAGE_NAME=tybalex/opni-gauss:dev
docker build . -t $IMAGE_NAME

docker push $IMAGE_NAME