import os
import subprocess
import logging
import shlex

logger = logging.getLogger(__name__)


LOCAL_NODE = "host"


class ToolExecutor(object):

    def __init__(self, allowed_commands, timeout=120, work_dir="/tmp/agent_workspace",
                 default_user="", nodes=None):
        self.allowed_commands = allowed_commands
        self.default_timeout = timeout
        self.work_dir = work_dir
        self.default_user = default_user or os.environ.get("SUDO_USER", "")
        self.nodes = nodes or {}
        os.makedirs(work_dir, exist_ok=True)

    # white list
    def _is_allowed(self, cmd_str):
        try:
            parts = shlex.split(cmd_str)
        except ValueError:
            return False
        if not parts:
            return False
        
        cmd_name = os.path.basename(parts[0])
        for allowed in self.allowed_commands:
            if cmd_name == allowed or cmd_name.startswith(allowed):
                return True
        return False

    def _build_local_argv(self, cmd_str, run_as):
        if not run_as or run_as == "root":
            return shlex.split(cmd_str)

        target_user = self.default_user if run_as == "default" else run_as
        if not target_user:
            logger.warning(
                "run_as='%s' while default_user not found. Still run as root: %s",
                run_as, cmd_str,
            )
            return shlex.split(cmd_str)

        return ["su", "-s", "/bin/sh", target_user, "-c", cmd_str]
    
    def _build_ssh_argv(self, cmd_str, node_name, run_as):
       if node_name not in self.nodes:
           raise ValueError("Unknown node outside the white list: {}".format(node_name))

       if not run_as or run_as == "root":
           remote_cmd = cmd_str
       else:
           target_user = self.default_user if run_as == "default" else run_as
           if target_user:
               safe_cmd = cmd_str.replace("'", "'\\''")
               remote_cmd = "su -s /bin/sh {} -c '{}'".format(target_user, safe_cmd)
           else:
               logger.warning(
                   "SSH node %s: run_as='%s' while default_user is not defined, still run as root",
                   node_name, run_as,
               )
               remote_cmd = cmd_str
       return ["ssh", "root@{}".format(node_name), remote_cmd]


    def run(self, cmd_str, run_as=None, node=None, timeout=None, stdin_data=None):
        effective_timeout = timeout if timeout is not None else self.default_timeout
        is_local = (not node) or (node == LOCAL_NODE)
        node_label = LOCAL_NODE if is_local else node

        result = {
            "cmd":        cmd_str,
            "node":       node_label,
            "run_as":     run_as or "root",
            "returncode": -1,
            "stdout":     "",
            "stderr":     "",
            "error":      None,
        }

        if not self._is_allowed(cmd_str):
            msg = "Command is refused: {}".format(cmd_str)
            logger.warning(msg)
            result["error"] = msg
            return result

        try:
            if is_local:
                argv = self._build_local_argv(cmd_str, run_as)
                logger.info("Run on host [%s]: %s", result["run_as"], cmd_str)
            else:
                argv = self._build_ssh_argv(cmd_str, node, run_as)
                logger.info("SSH Run [node=%s, run_as=%s]: %s",
                            node, result["run_as"], cmd_str)
        except ValueError as e:
            result["error"] = str(e)
            logger.error(result["error"])
            return result

        logger.debug("argv: %s", argv)

        # Run
        try:
            proc = subprocess.Popen(
                argv,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.work_dir if is_local else None,
            )
            stdout, stderr = proc.communicate(
                input=stdin_data.encode("utf-8") if stdin_data else None,
                timeout=effective_timeout,
            )
            result["returncode"] = proc.returncode
            result["stdout"] = stdout.decode("utf-8", errors="replace")
            result["stderr"] = stderr.decode("utf-8", errors="replace")
            logger.debug("Return code: %d, stdout: %d bytes (Timeout: %ds)",
                         proc.returncode, len(result["stdout"]), effective_timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            msg = "Timeout ({}s) [node={}]: {}".format(
                effective_timeout, node_label, cmd_str)
            logger.error(msg)
            result["error"] = msg
        except Exception as e:
            msg = "Failed to run command: {}".format(str(e))
            logger.error(msg)
            result["error"] = msg

        return result