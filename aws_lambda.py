#!/usr/bin/env python
# -*- coding: utf-8 -*-
#@Time: 2018/10/14 16:04
#@Authore : gzq
#@File: aws_lambda.py

from __future__ import print_function
import boto3
import os
import sys
import uuid
from PIL import Image
import PIL.Image

s3_client = boto3.client('s3')

def getImagepath(image_path):
    #print(image_path.split(".jpg"))
    imageName = image_path[0:-4]
    imagePrix = image_path[-4:]
    return (imageName,imagePrix)

def resize_image(image_path, resized_path,re_size):
    #
    imageName,imagePreix = getImagepath(image_path)
    newWidth = re_size[0]
    newHeight = re_size[1]
    with Image.open(image_path) as image:
        #image.thumbnail(tuple(x / 2 for x in image.size))
        image.thumbnail(re_size)
        resize_path = "%s_%s_%s%s" % (imageName, str(newWidth), str(newHeight), imagePreix)
        image.save(resize_path)

def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)
        upload_path = '/tmp/resized-{}'.format(key)

        s3_client.download_file(bucket, key, download_path)
        resize_image(download_path, upload_path)
        s3_client.upload_file(upload_path, '{}resized'.format(bucket), key)

image_path1 = "F:\\kilimall\\tmp\\IMG_1914_1.jpg"
image_path2 = "F:\\kilimall\\tmp\\IMG_1948_1.jpg"
resize_path = "F:\\kilimall\\tmp\\2.jpg"
imglist = [image_path1, image_path2]
resize = [(320, 680), (760, 1024), (64, 64)]

for i in imglist:
    for s in resize:
        resize_image(i, resize_path,  s)
