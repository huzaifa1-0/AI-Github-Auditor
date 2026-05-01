# debug.py
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

print("=== Environment Debugger ===")

# 1. Show current working directory
cwd = Path.cwd()
print(f"\n1. Current Directory: {cwd}")

# 2. Show files in directory
print("\n2. Directory Contents:")
for f in cwd.iterdir():
    print(f" - {f.name}")

# 3. Try loading .env
env_path = cwd / ".env"
print(f"\n3. Loading .env from: {env_path}")

if env_path.exists():
    load_dotenv(env_path)
    print("   .env file loaded successfully!")
else:
    print("   .env file not found!")

# 4. Check GitHub token
token = os.getenv("GITHUB_TOKEN")
print(f"\n4. GitHub Token: {'Exists' if token else 'MISSING'}")
if token:
    print(f"   Token starts with: {token[:10]}")
    print(f"   Token length: {len(token)} characters")

# 5. Test GitHub API
if token:
    print("\n5. Testing GitHub API...")
    try:
        from github import Github
        g = Github(token)
        user = g.get_user()
        print(f"   Authenticated as: {user.login}")
        print(f"   Rate limit: {g.get_rate_limit().core}")
        print("   API test successful!")
    except Exception as e:
        print(f"   API test failed: {str(e)}")
else:
    print("\n5. Skipping GitHub API test (no token)")

print("\n=== Debug Complete ===")