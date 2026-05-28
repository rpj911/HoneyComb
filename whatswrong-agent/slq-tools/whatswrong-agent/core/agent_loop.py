# -*- coding: utf-8 -*-
"""
AgentLoop: ReAct style agent loop
Workflow: Think → [Print Plan] → [User Confirm] → Act → Observe → Think → ... → Finish
"""

import json
import logging
import re
import sys

logger = logging.getLogger(__name__)


ACTION_LABELS = {
    "run_command":  "Run Command",
    "read_log":     "Read Log",
    "analyze_log":  "Analyze Log",
    "finish":       "Finish Diagnostic",
}


SYSTEM_PROMPT_TEMPLATE = """You are a CT system diagnostic expert agent。Your task is to analyze log and running commands to check the system problem.

## Background Knowledge
{knowledge_context}

## Available Tools
{tools_json}

## Available Logs
{log_sources_json}

## Workflow
You need to output a JSON object each iteration (no extra content) in the following format:：
{{
  "thought": "Current analysis ideas",
  "action": "run_command | read_log | analyze_log | finish",
  "params": {{
    // run_command:   {{"cmd": "The shell command string. If you want to run cmd on remote nodes, DO NOT include ssh in this string", "node": "On which node to run the shell command"}}
    // read_log:      {{"source": "Log file path", "mode": "errors_only|warnings_and_errors|all", "keywords": ["optional keywords"]}}
    // analyze_log:   {{"log_ref": "Refer to the log content of some steps before", "question": "Specific question of the log"}}
    // finish:        {{"conclusion": "The final conclusion", "root_cause": "Root cause", "suggestions": ["suggestion1","suggestion2"]}}
  }}
}}

Note:
- Output ONE json each time and no explaination
- Only the listed tools in Available Tools section are available. Tools beyond the white list will be refused.
- Must finish after {max_iterations} iterations of operation
"""


class UserAbortError(Exception):
    pass


class AgentLoop(object):

    def __init__(self, llm, knowledge, executor, log_analyzer,
                 max_iterations=10, plan_mode=False):
        self.llm = llm
        self.knowledge = knowledge
        self.executor = executor
        self.log_analyzer = log_analyzer
        self.max_iterations = max_iterations
        self.plan_mode = plan_mode

    def _get_tool_meta(self, cmd_str):
        """
        Search for the tool definition matches the command from knowledge, return the dict。
        Rule: Command string starts with the command_template of tool
        """
        import shlex as _shlex
        try:
            cmd_name = _shlex.split(cmd_str)[0] if cmd_str.strip() else ""
        except ValueError:
            cmd_name = ""

        for tool in self.knowledge.get_available_tools():
            tmpl = tool.get("command_template", "")
            try:
                tmpl_name = _shlex.split(tmpl)[0] if tmpl.strip() else ""
            except ValueError:
                tmpl_name = ""
            if cmd_name and tmpl_name and (
                cmd_name == tmpl_name or cmd_str.startswith(tmpl)
            ):
                return tool
        return {}


    def _print_plan(self, iteration, action_obj):
        action = action_obj.get("action", "unknown")
        thought = action_obj.get("thought", "")
        params  = action_obj.get("params", {})
        label   = ACTION_LABELS.get(action, action)

        print("")
        print("┌─ Plan of Step{} {}".format(iteration, "─" * 40))
        print("│ Action Type: {}".format(label))
        print("│ Thoughts: {}".format(thought))

        if action == "run_command":
            cmd = params.get("cmd", "")
            node = params.get("node", "host")
            print("│ Run Command: '{}'".format(cmd))
            meta = self._get_tool_meta(cmd)
            # node = meta.get("node", "host")
            run_as = meta.get("run_as", "root")
            tool_timeout = meta.get("timeout", None)
            print("│ On node: {}".format(node))
            print("│ Run as: {}".format(run_as))
            if tool_timeout:
                print("│ Timeout: {}s".format(tool_timeout))
            notes = meta.get("notes", "")
            if notes:
                print("│ Notes: {}".format(notes))
        elif action == "read_log":
            print("│ Log source: {}".format(params.get("source", "")))
            print("│ Filter mode: {}".format(params.get("mode", "errors_only")))
            kws = params.get("keywords", [])
            if kws:
                print("│ Keywords:   {}".format(", ".join(kws)))
        elif action == "analyze_log":
            print("│ Referred log: {}".format(params.get("log_ref", "")))
            print("│ Problem analyze: {}".format(params.get("question", "")))
        elif action == "finish":
            print("│ Conclusion Abstract: {}".format(params.get("conclusion", "")))
            print("│ Root Cause: {}".format(params.get("root_cause", "")))
            suggestions = params.get("suggestions", [])
            for i, s in enumerate(suggestions, 1):
                print("│ Suggestion {}: {}".format(i, s))

        print("└" + "─" * 50)

    def _confirm_plan(self):
        prompt = ">>> Accept? [y=yes / n=skip / q=quit]: "
        while True:
            try:
                sys.stdout.write(prompt)
                sys.stdout.flush()
                choice = sys.stdin.readline().strip().lower()
            except (KeyboardInterrupt, EOFError):
                choice = "q"

            if choice in ("y", "yes", ""):
                return "yes"
            elif choice in ("n", "no"):
                return "skip"
            elif choice in ("q", "quit", "exit"):
                return "abort"
            else:
                print("    Please type y/n/q")


    def _build_system_prompt(self):
        tools = self.knowledge.get_available_tools()
        log_sources = self.knowledge.get_log_sources()
        return SYSTEM_PROMPT_TEMPLATE.format(
            knowledge_context=self.knowledge.get_system_context(),
            tools_json=json.dumps(tools, ensure_ascii=False, indent=2),
            log_sources_json=json.dumps(log_sources, ensure_ascii=False, indent=2),
            max_iterations=self.max_iterations,
        )

    def _parse_action(self, llm_response):
        text = llm_response.strip()
        m = re.search(r"```(?:json)?\s*([\s\S]+?)```", text)
        if m:
            text = m.group(1).strip()
        try:
            return json.loads(text)
        except ValueError as e:
            logger.error("Failed to parse LLM output: %s\nOutput: %s", e, llm_response[:300])
            return None

    def _execute_action(self, action_obj, observations):
        action = action_obj.get("action", "")
        params = action_obj.get("params", {})

        if action == "run_command":
            cmd = params.get("cmd", "")
            meta = self._get_tool_meta(cmd)
            run_as = meta.get("run_as", "root")
            node = params.get("node", "host")
            # node = meta.get("node", None)
            tool_timeout = meta.get("timeout", None)
            result = self.executor.run(cmd, run_as=run_as, node=node,
                                       timeout=tool_timeout)
            if result["error"]:
                obs = "Command Failed: {}".format(result["error"])
            else:
                output = result["stdout"] or result["stderr"]
                lines = self.log_analyzer.read_text(output)
                obs = self.log_analyzer.preprocess(lines, mode="all")
                if not obs.strip():
                    obs = "(No output, retuen code: {})".format(result["returncode"])
            observations.append({"type": "command", "cmd": cmd,
                                  "node": result["node"], "run_as": run_as,
                                  "result": obs})
            return obs

        elif action == "read_log":
            source = params.get("source", "")
            mode = params.get("mode", "errors_only")
            keywords = params.get("keywords", [])
            log_path = self._resolve_log_source(source)
            lines = self.log_analyzer.read_tail(log_path)
            obs = self.log_analyzer.preprocess(lines, mode=mode, extra_keywords=keywords or None)
            if not obs.strip():
                obs = "(Log is empty or nothing matches: {})".format(log_path)
            observations.append({"type": "log_read", "source": source, "result": obs})
            return obs

        elif action == "analyze_log":
            log_ref = params.get("log_ref", "")
            question = params.get("question", "")
            log_text = ""
            for obs_item in reversed(observations):
                if log_ref in obs_item.get("source", "") or log_ref in obs_item.get("cmd", ""):
                    log_text = obs_item.get("result", "")
                    break
            if not log_text:
                log_text = observations[-1].get("result", "") if observations else ""
            analysis = self.log_analyzer.analyze_with_llm(
                self.llm, log_text, question, context=self.knowledge.get_system_context()
            )
            observations.append({"type": "log_analysis", "result": analysis})
            return analysis

        elif action == "finish":
            return None

        else:
            obs = "Unknown action type: {}".format(action)
            logger.warning(obs)
            return obs

    def _resolve_log_source(self, source_name):
        for src in self.knowledge.get_log_sources():
            if src.get("name") == source_name:
                return src.get("path", source_name)
        return source_name

    # ------------------------------------------------------------------ #
    #  Main Loop                                                         #
    # ------------------------------------------------------------------ #

    def run(self, problem_description):
        system_prompt = self._build_system_prompt()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "## Problem Description\n{}".format(problem_description)},
        ]

        observations = []
        iterations = 0
        final_action = None

        while iterations < self.max_iterations:
            iterations += 1
            logger.info("--- Agent Iteration %d ---", iterations)

            response = self.llm.chat(messages)
            action_obj = self._parse_action(response)

            if action_obj is None:
                messages.append({"role": "assistant", "content": response})
                messages.append({
                    "role": "user",
                    "content": "Your output is not an available JSON. Try again."
                })
                continue

            logger.debug("Action: %s | Thought: %s",
                         action_obj.get("action"), action_obj.get("thought", "")[:80])

            self._print_plan(iterations, action_obj)

            if action_obj.get("action") == "finish":
                if self.plan_mode:
                    choice = self._confirm_plan()
                    if choice == "abort":
                        logger.info("User Abort")
                        raise UserAbortError("User Abort in Plan Mode")
                messages.append({"role": "assistant", "content": response})
                final_action = action_obj
                break

            # ---- Confirm in Plan Mode ----
            if self.plan_mode:
                choice = self._confirm_plan()
                if choice == "abort":
                    logger.info("User Abort")
                    raise UserAbortError("User Abort in Plan Mode")
                elif choice == "skip":
                    print("    ↳ Skip. Notify agent to continue...")
                    messages.append({"role": "assistant", "content": response})
                    messages.append({
                        "role": "user",
                        "content": "User skipped this step ({}). Try other ideas and go on.".format(
                            action_obj.get("action")
                        ),
                    })
                    continue

            messages.append({"role": "assistant", "content": response})
            observation = self._execute_action(action_obj, observations)
            obs_message = "## Observation\n{}".format(observation)
            messages.append({"role": "user", "content": obs_message})

        # Max iteration reached
        if final_action is None:
            logger.warning("Max operation limit reached. Finish now and give conclusion.")
            messages.append({
                "role": "user",
                "content": "You have reached max operation iteration limit. Output finish action and give your conclusion."
            })
            response = self.llm.chat(messages)
            final_action = self._parse_action(response) or {}

        return {
            "problem": problem_description,
            "iterations": iterations,
            "observations": observations,
            "final_action": final_action,
            "messages": messages,
        }
