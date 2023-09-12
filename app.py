import os
import boto3
from dotenv import load_dotenv
from flask import Flask, request
from botocore.exceptions import NoCredentialsError
from urllib.parse import quote

load_dotenv()

LIARA_ENDPOINT = os.getenv("LIARA_ENDPOINT")
LIARA_ACCESS_KEY = os.getenv("LIARA_ACCESS_KEY")
LIARA_SECRET_KEY = os.getenv("LIARA_SECRET_KEY")
LIARA_BUCKET_NAME = os.getenv("LIARA_BUCKET_NAME")

s3 = boto3.client(
    "s3",
    endpoint_url=LIARA_ENDPOINT,
    aws_access_key_id=LIARA_ACCESS_KEY,
    aws_secret_access_key=LIARA_SECRET_KEY,
)

app = Flask(__name__)


@app.route("/")
def index():
    urls = {"urls": list()}
    for url in app.url_map.iter_rules():
        if '/static/' not in str(url):
            urls["urls"].append(str(url))
    return {"api": "running", **urls}


@app.route("/upload", methods=["POST"])
def upload_file():
    response = {"message": ""}
    file = request.files["file"]
    if file:
        try:
            s3.upload_fileobj(file, LIARA_BUCKET_NAME, file.filename)
            response["message"] = "File uploaded."
        except NoCredentialsError:
            response["message"] = "Liara credentials not found."
        except Exception as e:
            response["message"] = str(e)
        finally:
            return response
    else:
        response["message"] = "No file selected."


@app.route("/download/<filename>")
def download_file(filename):
    response = {"message": ""}
    try:
        s3.download_file(LIARA_BUCKET_NAME, filename, filename)
        response["message"] = "File downloaded."
    except NoCredentialsError:
        response["message"] = "Liara credentials not found."
    except Exception as e:
        response["message"] = str(e)
    finally:
        return response


@app.route("/list")
def list_files():
    response = {"message": list()}
    try:
        files = s3.list_objects(Bucket=LIARA_BUCKET_NAME)
        for file in files["Contents"]:
            response["message"].append(file["Key"])
    except NoCredentialsError:
        response["message"] = "Liara credentials not found."
    except Exception as e:
        response["message"] = str(e)
    finally:
        return response


@app.route("/presigned-url/<filename>")
def get_presigned_url(filename):
    response = {"message": ""}
    try:
        pre_signed_url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": LIARA_BUCKET_NAME, "Key": filename},
            ExpiresIn=12 * 60 * 60,  # 12 hours
        )
        response["message"] = pre_signed_url
    except NoCredentialsError:
        response["message"] = "Liara credentials not found."
    except Exception as e:
        response["message"] = str(e)
    finally:
        return response


@app.route("/permanent-url/<filename>")
def get_permanent_url(filename):
    # bucket should be public
    response = {"message": ""}
    try:
        filename_encoded = quote(filename)
        permanent_url = f"https://{LIARA_BUCKET_NAME}.{LIARA_ENDPOINT.replace('https://', '')}/{filename_encoded}"
        response["message"] = permanent_url
    except NoCredentialsError:
        response["message"] = "Liara credentials not found."
    except Exception as e:
        response["message"] = str(e)
    finally:
        return response


if __name__ == "__main__":
    app.run()