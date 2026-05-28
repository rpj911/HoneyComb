# whatswrong-agent
A edge-side LLM agent aims to diagnostic the recon-console, simulator or Bay problem. User can describe their problem/question/complaint with natural language and the agent will do the rest of jobs.

You can use this whatswrong-agent like: `python3 whatswrong.py --probelm "I can not access to igc1 node"`. Then the agent will work on your problem.

Currently the agent can only investigate the problem of SDA and Recon subsystem due to the limit of knowledge and skills.

## Demo Example
```shell
[root@re74 whatswrong-agent]# python3 whatswrong.py --problem "Please help me to check the status of raw-data-service on sdac"
[2026-03-10 22:20:35] INFO agent: Running dir: /usr/g/ctuser/shilangqing/whatswrong-agent/run_20260310_222035
[2026-03-10 22:20:35] INFO agent: Log: /usr/g/ctuser/shilangqing/whatswrong-agent/run_20260310_222035/agent.log
[2026-03-10 22:20:35] INFO core.knowledge_loader: Loaded skill file: system_diagnostics.json
[2026-03-10 22:20:35] INFO core.knowledge_loader: Loaded knowledge file: background.md
[2026-03-10 22:20:35] INFO core.knowledge_loader: Loaded knowledge file: important_services.md
[2026-03-10 22:20:35] INFO core.knowledge_loader: Loaded knowledge file: system_logs.md
[2026-03-10 22:20:35] INFO agent: Start diagnostic, user complaint: Please help me to check the status of raw-data-service on sdac
[2026-03-10 22:20:35] INFO core.agent_loop: --- Agent Iteration 1 ---

┌─ Plan of Step1 ────────────────────────────────────────
│ Action Type: Run Command
│ Thoughts: The user wants to check the status of raw-data-service on sdac node. According to the background knowledge, raw-data-service is a systemd service that runs on sdac. I should use the check_service_status tool to check this service.
│ Run Command: systemctl status raw-data-service on node sdac
│ On node: sdac
│ Run as: root
│ Timeout: 15s
└──────────────────────────────────────────────────
[2026-03-10 22:20:52] INFO core.tool_executor: SSH Run [node=sdac, run_as=root]: systemctl status raw-data-service
[2026-03-10 22:20:52] INFO core.agent_loop: --- Agent Iteration 2 ---

┌─ Plan of Step2 ────────────────────────────────────────
│ Action Type: Read Log
│ Thoughts: The raw-data-service is showing as 'inactive (dead)' which is a problem since this service is important for sending raw data to IG nodes. I need to investigate why it's not running by checking the system logs for any errors related to this service.
│ Log source: /usr/g/service/log/gesys_*.log
│ Filter mode: errors_only
│ Keywords:   raw-data-service
└──────────────────────────────────────────────────
[2026-03-10 22:21:02] WARNING core.log_analyzer: Log file does not exist: /usr/g/service/log/gesys_*.log
[2026-03-10 22:21:02] INFO core.agent_loop: --- Agent Iteration 3 ---

┌─ Plan of Step3 ────────────────────────────────────────
│ Action Type: Read Log
│ Thoughts: The gesys log doesn't contain information about raw-data-service. Let me check the syscab_install.log and syscab_diag.log files which might have more information about remote node issues or service problems.
│ Log source: /usr/g/service/log/syscab_install.log
│ Filter mode: errors_only
│ Keywords:   raw-data-service, sdac
└──────────────────────────────────────────────────
[2026-03-10 22:21:06] INFO core.agent_loop: --- Agent Iteration 4 ---

┌─ Plan of Step4 ────────────────────────────────────────
│ Action Type: Read Log
│ Thoughts: The gesys log and syscab_install.log are empty. Let me check the syscab_diag.log which might contain information about remote node hardware problems, network issues, or other system-level problems that could be causing raw-data-service to fail.
│ Log source: /usr/g/service/log/syscab_diag.log
│ Filter mode: errors_only
│ Keywords:   raw-data-service, sdac
└──────────────────────────────────────────────────
[2026-03-10 22:21:10] INFO core.agent_loop: --- Agent Iteration 5 ---

┌─ Plan of Step5 ────────────────────────────────────────
│ Action Type: Run Command
│ Thoughts: All logs are empty. Let me try a different approach - I'll check if there are any obelus processes running on sdac, and also examine the raw-data-service unit file to understand what dependencies or configuration might be causing it to fail.
│ Run Command: ps -ef | grep obelus on node sdac
│ On node: sdac
│ Run as: default
│ Timeout: 10s
│ Notes: Combine with grep to filter the process name
└──────────────────────────────────────────────────
[2026-03-10 22:21:13] INFO core.tool_executor: SSH Run [node=sdac, run_as=default]: ps -ef | grep obelus
[2026-03-10 22:21:13] INFO core.agent_loop: --- Agent Iteration 6 ---

┌─ Plan of Step6 ────────────────────────────────────────
│ Action Type: Run Command
│ Thoughts: The obelus processes are running on sdac (diags_obelusd processes visible). Now I need to check the raw-data-service unit file to understand its dependencies and configuration. Let me also check if ge_cpuset service is running, as it's another important systemd service on sdac that might be related.
│ Run Command: systemctl status ge_cpuset on node sdac
│ On node: sdac
│ Run as: root
│ Timeout: 15s
└──────────────────────────────────────────────────
[2026-03-10 22:21:18] INFO core.tool_executor: SSH Run [node=sdac, run_as=root]: systemctl status ge_cpuset
[2026-03-10 22:21:18] INFO core.agent_loop: --- Agent Iteration 7 ---

┌─ Plan of Step7 ────────────────────────────────────────
│ Action Type: Run Command
│ Thoughts: The ge_cpuset service is not found, which could indicate a configuration issue. Let me examine the raw-data-service unit file to understand its dependencies and configuration, and also check if there are any other important services that need to be running.
│ Run Command: cat /etc/systemd/system/raw-data-service.service on node sdac
│ On node: sdac
│ Run as: root
└──────────────────────────────────────────────────
[2026-03-10 22:21:22] INFO core.tool_executor: SSH Run [node=sdac, run_as=root]: cat /etc/systemd/system/raw-data-service.service
[2026-03-10 22:21:22] INFO core.agent_loop: --- Agent Iteration 8 ---

┌─ Plan of Step8 ────────────────────────────────────────
│ Action Type: Run Command
│ Thoughts: The raw-data-service unit file shows it has a hard dependency on ge_cpuset.service ('Requires=docker.service ge_cpuset.service network-online.target'). However, when I checked earlier, ge_cpuset.service was not found ('Unit ge_cpuset.service not found'). This is the root cause - without ge_cpuset.service, raw-data-service cannot start. Let me check if there's a way to enable or fix this service.
│ Run Command: systemctl status docker.service on node sdac
│ On node: sdac
│ Run as: root
│ Timeout: 15s
└──────────────────────────────────────────────────
[2026-03-10 22:21:28] INFO core.tool_executor: SSH Run [node=sdac, run_as=root]: systemctl status docker.service
[2026-03-10 22:21:28] INFO core.agent_loop: --- Agent Iteration 9 ---

┌─ Plan of Step9 ────────────────────────────────────────
│ Action Type: Read Log
│ Thoughts: The root cause is identified: raw-data-service has a hard dependency on ge_cpuset.service which is not found ('Unit ge_cpuset.service not found'). This prevents raw-data-service from starting. Let me check the syscab_diag.log more thoroughly with different keywords to see if there are any clues about ge_cpuset service issues or configuration problems.
│ Log source: /usr/g/service/log/syscab_diag.log
│ Filter mode: all
│ Keywords:   ge_cpuset, sdac
└──────────────────────────────────────────────────
[2026-03-10 22:21:32] INFO core.agent_loop: --- Agent Iteration 10 ---

┌─ Plan of Step10 ────────────────────────────────────────
│ Action Type: Run Command
│ Thoughts: The logs are empty but I've identified the root cause: ge_cpuset.service is not found, which is a hard dependency for raw-data-service. Let me run syscab diag on sdac to get more detailed hardware and service information that might help resolve this issue.
│ Run Command: syscab diag sdac on node host
│ On node: host
│ Run as: root
│ Timeout: 300s
│ Notes: Provides the hardware info of remote nodes. Run syscab diag will diag all nodes. If you want to diagnostic specific node, use syscab diag <node_name>
└──────────────────────────────────────────────────
[2026-03-10 22:21:36] INFO core.tool_executor: Run on host [root]: syscab diag sdac
[2026-03-10 22:25:09] WARNING core.agent_loop: Max operation limit reached. Finish now and give conclusion.
[2026-03-10 22:25:17] INFO agent: Diagnostic report saved to: /usr/g/ctuser/shilangqing/whatswrong-agent/run_20260310_222035/report.md

============================================================
[Problem Description]Please help me to check the status of raw-data-service on sdac
[Root Cause]1. ge_cpuset.service is not found on sdac (Unit ge_cpuset.service not found), but it is listed as a required dependency in raw-data-service.service unit file. 2. The sdac node appears to be powered off according to syscab diag results.
[Conclusion]The raw-data-service is inactive (dead) on sdac node. The root cause is that ge_cpuset.service is missing/not found, which is a hard dependency for raw-data-service to start. Additionally, syscab diag indicates the sdac node may be powered off.
[Suggestion]
  - Check if the sdac node hardware is properly powered on using syscab diag
  - Verify ge_cpuset.service configuration and enable it if needed
  - Check /etc/systemd/system/ for ge_cpuset.service file existence
  - Review raw-data-service logs at /usr/ge_sda/log/raw-data-service-regulator.log for more detailed error messages
  - Ensure all required dependencies (docker.service, network-online.target) are properly configured
[Iteration]10
============================================================
Running dir: /usr/g/ctuser/shilangqing/whatswrong-agent/run_20260310_222035
  ├── agent.log
  └── report.md
```


## Agent Workflow

```
User describe problem
     │
     ▼
┌─────────────────────────────────┐
│         AgentLoop (ReAct)       │
│  Think(LLM) → Act → Observe     │
│         Iterate till finish     │
└─────────────────────────────────┘
     │              │
     ▼              ▼
ToolExecutor    LogAnalyzer
(subprocess)   (Filter by code → Analyze by LLM)
                    │
                    ▼
              Filter the log with rules to avoid the LLM context being exhausted
                    │
                    ▼
            ReportGenerator
            (Markdown Report)
```

## Knowledge and Skills
Knowledge and skills is the most important part of whatswrong-agent.

When the agent starts, it will read knowledge and skills from the knowledge/ folder, knowledge in Markdown and skill in JSON format.

Currently there are several basic knowledge and skill files.
- background.md: Provides the overview of the CT system
- important_services.md: Provides the introduction of important services in CT system (Most are Recon and SDA services. Services of other subsystems can be ). Agent will focus on these services to investigate the problem.
- system_diagnostic.json: The main skill list, provides the log sources that agent can check and the system tools/commands that can be used to check the problem.
- system_logs.md: Tells the agent what information does a log provide. Works together with the log sources section in system_diagnostic.json

The more accurate skills, the powerful the agent will be.

## Future Enhancement & Open Source Community
More skills and knowledge enable the agent to work better and stronger. It's kind for you if you can contribute your knowledge & skills to whatswrong-agent project. You can add knowledge & skills in existing files, or add stand-alone files under `knowledge/` folder.

Currently, knowledge is in Markdown format and skills are in JSON format. The agent will load *.md and *.json to context.

## Agent Security
whatswrong-agent uses a white list to limit the tools/commands that the agent can run on console. The tools/commands beyond the white list will be refused and the LLM will be told to try another way.

## On-console Capability and Data Security
whatswrong-agent is implemented using python standard library (python3.6 friendly) and avoid to use third-party library. This makes the whatswrong-agent able to run on recon-console, simulator or Bay.

The agent uses Ollama instance as the LLM inference backend, which is running on the server of GE Healthcare and can be configured in config.json (For now, it uses the `qwen3.5:9b` model on `10.189.130.100`). This makes the agent runs on console/simulator/Bay can access to the LLM and the data is safely transfered only in GE Healthcare network.

## What's Next
This agent tool is still in development and there are some incoming features. Most of them aim to reduce the context.

### Sub-agents
Sub-agents can take tasks from the master agent and run/think the task in its own context. This design can isolate the task context of sub-agent from that of master agent. For example, a log-reading sub-agent can take the job from master agent to read/analyze log in its own context and return the abstract to master agent. Thus, the context of master agent will not be polluted by the log.

The sub-agents can work like a thread pool. The master agent push tasks to the task queue, and several sub-agent will be activated and take the tasks. When sub-agents finish their jobs, a callback function of master agent will be called and read the results from sub-agents.

### Dynamic Loaded Skills
Currently the agent will load all skills/knowledge at starting phase. While not all these skills/knowledge are useful in a single task and not used skills/knowledge will. Which skill should be loaded can be decided by the agent itself. In this way, only some background and basic knowledge (like a overview of the system, and HOW to load skills) will be loaded when agent starts. The agent will decide to load which skill as the reasoning goes on.

### More Flexible Log Filter
Currently the log filter only takes the log lines with specific keywords like ERROR, EE, etc. While in actual logs, the error line only tells what error is detected, and the clues are listed in couples of lines above. Thus, a more flexible lof filter need to take log from a range around the error line.