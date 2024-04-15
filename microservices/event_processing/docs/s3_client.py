import boto3
import cv2

import numpy as np
# from io import BytesIO

client = boto3.client('s3')

# List all object names in a bucket
obj_dict = client.list_objects(Bucket='ivsr-aiot')
obj_list = obj_dict["Contents"]
for obj in obj_list:
    print(obj["Key"])

# Upload an object to bucket
with open('lamp.jpg', 'rb') as data:
    client.put_object(
        Bucket='ivsr-aiot',
        Key='lamp.jpg',
        Body=data)


# Download an object from bucket
response = client.get_object(
    Bucket='ivsr-aiot',
    Key='hacking.jpg'
)

# Display the image object using cv2
image_data = response["Body"].read()
image_np = np.frombuffer(image_data, np.uint8)
image_cv2 = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

cv2.imshow('hacking.jpg', image_cv2)
cv2.waitKey(0)
cv2.destroyAllWindows()
