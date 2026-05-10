import os
import subprocess
import sys
import platform
def run_cmd(cmd, shell=True):
    try:
        subprocess.run(cmd, shell=shell, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
def install_docker():
    system = platform.system()
    if system == "Linux":
        print("Checking for apt-get...")
        if run_cmd("which apt-get"):
            print("Installing Docker via apt...")
            run_cmd("sudo apt-get update && sudo apt-get install -y docker.io docker-compose")
    elif system == "Windows":
        print("Checking for choco...")
        if run_cmd("where choco"):
            print("Installing Docker via choco...")
            run_cmd("choco install docker-desktop -y")
    else:
        print(f"Unsupported OS: {system}. Please install Docker manually.")
def setup_env_file():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        with open(env_path, "w") as f:
            f.write("GOOGLE_API_KEY=your-google-api-key-here\n")
            f.write("DATABASE_URL=postgresql://postgres:password@db:5432/cache_me_db\n")
            f.write("API_SECRET_KEY=change-this-in-prod\n")
        print(f"Created default .env at {env_path}")
    else:
        print(".env already exists.")
def main():
    print("=== Self-Auditing RAG: One-Click Setup ===")
    if not run_cmd("docker --version"):
        print("Docker not found. Attempting installation...")
        install_docker()
    setup_env_file()
    print("Building and launching Docker containers...")
    if run_cmd("docker-compose up -d --build"):
        print("Containers started successfully.")
        print("Initializing database tables...")
        run_cmd("docker-compose exec app python3 -c 'from backend.retrieval_service.storage.postgres_tables import init_tables; init_tables()'")
        print("Setup complete! Terminal logs available at backend.log inside the container.")
        print("API is running at http://localhost:8000")
    else:
        print("Docker-compose failed. Please check the logs.")
if __name__ == "__main__":
    main()
