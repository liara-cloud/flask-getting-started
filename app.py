from flask import Flask, render_template, request, flash
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# Load environment variables
LIARA_ENDPOINT_URL = os.getenv("LIARA_ENDPOINT_URL")
LIARA_ACCESS_KEY   = os.getenv("LIARA_ACCESS_KEY")
LIARA_SECRET_KEY   = os.getenv("LIARA_SECRET_KEY")
BUCKET_NAME        = os.getenv("BUCKET_NAME")

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    endpoint_url=LIARA_ENDPOINT_URL,
    aws_access_key_id=LIARA_ACCESS_KEY,
    aws_secret_access_key=LIARA_SECRET_KEY
)

# Controller: List all buckets
def list_buckets():
    try:
        response = s3_client.list_buckets()
        return [bucket['Name'] for bucket in response.get('Buckets', [])]
    except NoCredentialsError:
        flash("Credentials not available.", "error")
        return []
    except ClientError as e:
        flash(f"Error listing buckets: {e}", "error")
        return []

# Controller: List all files in a bucket
def list_files(bucket_name):
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        return [obj['Key'] for obj in response.get('Contents', [])]
    except ClientError as e:
        flash(f"Error listing files: {e}", "error")
        return []

# Controller: Upload a file
def upload_file(file, bucket_name):
    try:
        s3_client.upload_fileobj(file, bucket_name, file.filename)
        flash(f"File '{file.filename}' uploaded successfully.", "success")
    except ClientError as e:
        flash(f"Error uploading file: {e}", "error")

# Controller: Delete a file
def delete_file(bucket_name, file_name):
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=file_name)
        flash(f"File '{file_name}' deleted successfully.", "success")
    except ClientError as e:
        flash(f"Error deleting file: {e}", "error")

# Controller: Generate a pre-signed URL
def generate_presigned_url(bucket_name, file_name, expiration=3600):
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_name},
            ExpiresIn=expiration
        )
        return url
    except ClientError as e:
        flash(f"Error generating pre-signed URL: {e}", "error")
        return None

# Controller: Generate a permanent URL
def generate_permanent_url(bucket_name, file_name):
    return f"{LIARA_ENDPOINT_URL}/{bucket_name}/{file_name}"

# Main route
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Handle file upload
        if "file" in request.files:
            file = request.files["file"]
            if file.filename:
                upload_file(file, BUCKET_NAME)

        # Handle file deletion
        file_to_delete = request.form.get("delete_file")
        if file_to_delete:
            delete_file(BUCKET_NAME, file_to_delete)

    # Fetch bucket names and files
    buckets = list_buckets()
    files = list_files(BUCKET_NAME)

    # Generate pre-signed URLs and permanent URLs for each file
    presigned_urls = {}
    permanent_urls = {}
    for file in files:
        presigned_urls[file] = generate_presigned_url(BUCKET_NAME, file)
        permanent_urls[file] = generate_permanent_url(BUCKET_NAME, file)

    return render_template(
        "index.html",
        buckets=buckets,
        files=files,
        presigned_urls=presigned_urls,
        permanent_urls=permanent_urls
    )

# Run the app
if __name__ == "__main__":
    app.run(debug=True)