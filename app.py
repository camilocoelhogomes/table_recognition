import boto3
s3 = boto3.resource('s3')
reader = boto3.client('rekognition')


def list_files():
    files = []
    bucket = s3.Bucket('test-bucket-camilo')
    for file in bucket.objects.all():
        files.append(file.key)
    return files


def detect_text(images):
    response = reader.detect_text(
        Image={'S3Object': images[0]})
    print(response)
    return response


images = list_files()
images
