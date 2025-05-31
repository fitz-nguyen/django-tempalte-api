import subprocess

# Define the command to run your test script
command = [
    "python",  # Path to Python interpreter in virtual environment
    "/home/app/api/receiver_trigger_from_postgresql.py",  # Script to run
]

# Run the script as a subprocess
subprocess.Popen(command)
