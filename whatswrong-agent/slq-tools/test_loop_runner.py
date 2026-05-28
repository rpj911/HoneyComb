import subprocess
import sys
import argparse

# ROUNDS = 25
# COMMAND = "syscab manufacturing_test --force-full 6765000-w6164299"
# LOGFILE = "TST_25.log"

def run_command(cmd, rounds, logfile):
    with open(logfile, "a", encoding="utf-8") as f:
        for i in range(rounds):
            header = "=== Round {} ===\n".format(i+1)
            print(header, end="")
            f.write(header)

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                bufsize=1,
                universal_newlines=True
            )

            for line in process.stdout:
                sys.stdout.write(line)
                sys.stdout.flush()
                f.write(line)
                f.flush()

            process.wait()
            footer = "=== Round {} finished with exit code {} ===\n".format(i+1, process.returncode)
            print(footer, end="")
            f.write(footer)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run long test command multiple times and log output.")
    parser.add_argument("--cmd", required=True, help="Command to run")
    parser.add_argument("--rounds", type=int, required=True, help="Iterations")
    parser.add_argument("--logfile", default="test_output.log", help="log path")
    args = parser.parse_args()

    run_command(args.cmd, args.rounds, args.logfile)