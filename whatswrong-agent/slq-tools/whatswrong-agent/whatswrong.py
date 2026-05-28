#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage: whatswrong --problem "describe your problem here"
"""

import sys
import os
import json
import argparse
import logging
from datetime import datetime

from core.llm_client import LLMClient
from core.knowledge_loader import KnowledgeLoader
from core.tool_executor import ToolExecutor
from core.log_analyzer import LogAnalyzer
from core.report_generator import ReportGenerator
from core.agent_loop import AgentLoop, UserAbortError

def check_root():
    """Check run as root"""
    if os.geteuid() != 0:
        print("[ERROR] whatswrong agent must be run as root")
        sys.exit(1)


def make_run_dir():
    """
    run dir: run_YYYYMMDD_HHMMSS
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(os.getcwd(), "run_{}".format(ts))
    os.makedirs(run_dir)
    return run_dir


def setup_logging(run_dir, verbose=False):
    level = logging.DEBUG if verbose else logging.INFO
    fmt = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(logging.Formatter(fmt, datefmt))
    root_logger.addHandler(console)

    log_path = os.path.join(run_dir, "agent.log")
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(fmt, datefmt))
    root_logger.addHandler(file_handler)

    return log_path


def parse_args():
    parser = argparse.ArgumentParser(description="whatswrong agent")
    parser.add_argument("--problem", required=True, help="Describe your problem in natural language")
    parser.add_argument("--config", default="config.json", help="Config file path")
    parser.add_argument("--verbose", action="store_true", help="If specified, print log")
    parser.add_argument("--plan-mode", action="store_true", dest="plan_mode", help="Plan mode: Print plan and ask for user to confirm before execute (y to confirm, n to skip and q to quit)")
    return parser.parse_args()


def load_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():

    check_root()

    args = parse_args()
    
    
    run_dir = make_run_dir()
    log_path = setup_logging(run_dir, verbose=args.verbose)
    logger = logging.getLogger("agent")
    logger.info("Running dir: %s", run_dir)
    logger.info("Log: %s", log_path)

    config = load_config(args.config)

    llm = LLMClient(
        base_url=config["ollama"]["base_url"],
        model=config["ollama"]["model"],
        timeout=config["ollama"].get("timeout", 120),
    )
    knowledge = KnowledgeLoader(config["knowledge_dir"])
    executor = ToolExecutor(
        allowed_commands=config.get("allowed_commands", []),
        timeout=config.get("command_timeout", 120),
        work_dir=run_dir,
        default_user=config.get("default_user", ""),
        nodes=config.get("nodes", {}),
    )
    log_analyzer = LogAnalyzer(config.get("log_rules", {}))
    report_gen = ReportGenerator()

    loop = AgentLoop(
        llm=llm,
        knowledge=knowledge,
        executor=executor,
        log_analyzer=log_analyzer,
        max_iterations=config.get("max_iterations", 10),
        plan_mode=args.plan_mode,
    )

    logger.info("Start diagnostic, user complaint: %s", args.problem)
    if args.plan_mode:
        logger.info("Plan mode activated: Running plan will be printed before execute and ask for user confirm")

    try:
        result = loop.run(args.problem)
    except UserAbortError:
        print("\nAborted by user")
        sys.exit(0)

    report_path = os.path.join(run_dir, "report.md")
    report_gen.write(result, report_path)
    logger.info("Diagnostic report saved to: %s", report_path)

    print("\n" + "=" * 60)
    print(report_gen.render_summary(result))
    print("=" * 60)
    print("Running dir: {}".format(run_dir))
    print("  ├── agent.log")
    print("  └── report.md")


if __name__ == "__main__":
    main()
