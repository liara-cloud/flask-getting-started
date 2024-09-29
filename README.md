# Send Email Using Flask (Liara + Flask-Mail)
## Steps
```
git clone https://github.com/liara-cloud/flask-getting-started.git
```
```
cd flask-getting-started
```
```
git checkout email-server
```
```
mv .env.example .env # and set ENVs
```
```
pip install virtualenv
```
```
python -m venv .venv
```
```
source .venv/Scripts/activate
```
```
pip install -r requirements.txt
```
```
python app.py
```
- check `http://localhost:5000/send-test-email`

## Need more info?
- [Liara Docs](https://docs.liara.ir/email-server/how-tos/connect-via-platform/flask/)
- [Flask Mail Docs](https://flask-mail.readthedocs.io/en/latest/)
