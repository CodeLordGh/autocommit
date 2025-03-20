# test_env.py
from dotenv import load_dotenv
import os

print("Before loading .env:")
print("GITHUB_CLIENT_ID:", os.environ.get("GITHUB_CLIENT_ID"))
# Get the directory where the app.py file is located
basedir = os.path.abspath(os.path.dirname(__file__))
# Load the .env file from that directory
env_path = os.path.join(basedir, '.env')
load_dotenv(env_path)
# load_dotenv()

print("After loading .env:")
print("GITHUB_CLIENT_ID:", os.environ.get("GITHUB_CLIENT_ID"))