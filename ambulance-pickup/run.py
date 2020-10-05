import subprocess
import sys

if __name__ == "__main__":
    # example: `run.py ls -l`
    subprocess.run(sys.argv[1:], timeout=120)
