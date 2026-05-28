import os
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DEFAULT_MAX_LINES = 200


class LogAnalyzer(object):

    def __init__(self, log_rules=None):
        """
        :param log_rules: dict
            {
              "error_keywords": ["ERROR", "CRITICAL", "Exception", "Traceback"],
              "warning_keywords": ["WARN", "WARNING"],
              "max_lines_to_llm": 200,
              "tail_lines": 500
            }
        """
        rules = log_rules or {}
        self.error_keywords = rules.get("error_keywords", ["ERROR", "CRITICAL", "Exception", "Traceback", "FATAL"])
        self.warning_keywords = rules.get("warning_keywords", ["WARN", "WARNING"])
        self.max_lines_to_llm = rules.get("max_lines_to_llm", DEFAULT_MAX_LINES)
        self.tail_lines = rules.get("tail_lines", 500)

    def read_tail(self, filepath, n=None):
        n = n or self.tail_lines
        if not os.path.exists(filepath):
            logger.warning("Log file does not exist: %s", filepath)
            return []
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            return [l.rstrip("\n") for l in lines[-n:]]
        except Exception as e:
            logger.error("Failed to read log file %s: %s", filepath, e)
            return []

    def read_text(self, text):
        return text.splitlines()

    # ------------------------------------------------------------------ #
    #  Filter Rules                                                      #
    # ------------------------------------------------------------------ #

    def filter_errors(self, lines):
        result = []
        for line in lines:
            upper = line.upper()
            if any(kw.upper() in upper for kw in self.error_keywords):
                result.append(line)
        return result

    def filter_warnings_and_errors(self, lines):
        keywords = self.error_keywords + self.warning_keywords
        result = []
        for line in lines:
            upper = line.upper()
            if any(kw.upper() in upper for kw in keywords):
                result.append(line)
        return result

    def filter_by_time_range(self, lines, start_dt, end_dt, time_pattern=None):
        pattern = time_pattern or r"(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})"
        result = []
        for line in lines:
            m = re.search(pattern, line)
            if m:
                try:
                    ts = datetime.strptime(m.group(1).replace("T", " "), "%Y-%m-%d %H:%M:%S")
                    if start_dt <= ts <= end_dt:
                        result.append(line)
                except ValueError:
                    pass
        return result

    def filter_by_keywords(self, lines, keywords):
        result = []
        for line in lines:
            if any(kw in line for kw in keywords):
                result.append(line)
        return result

    def deduplicate(self, lines, max_repeat=3):
        from collections import Counter
        counts = {}
        result = []
        for line in lines:
            key = line.strip()
            counts[key] = counts.get(key, 0) + 1
            if counts[key] <= max_repeat:
                result.append(line)
        return result

    def preprocess(self, lines, mode="errors_only", extra_keywords=None):
        """
        Log pre process
        """
        if mode == "errors_only":
            filtered = self.filter_errors(lines)
        elif mode == "warnings_and_errors":
            filtered = self.filter_warnings_and_errors(lines)
        else:
            filtered = lines

        if extra_keywords:
            filtered = self.filter_by_keywords(filtered, extra_keywords)

        filtered = self.deduplicate(filtered)

        if len(filtered) > self.max_lines_to_llm:
            logger.info("There are %d lines of log after filter, cut to %d line", len(filtered), self.max_lines_to_llm)
            half = self.max_lines_to_llm // 2
            filtered = (
                filtered[:half]
                + ["... [{} lines omitted] ...".format(len(filtered) - self.max_lines_to_llm)]
                + filtered[-half:]
            )

        return "\n".join(filtered)

    def analyze_with_llm(self, llm, log_text, problem_description, context=""):
        system_prompt = (
            "You are an expert of CT system diagnostic. Please analyze the root cause of problem according to the following log patch.\n"
            "Only focus on the exceptions related with the problem and give direct feasible conclusion.\n"
            + (context if context else "")
        )
        user_prompt = (
            "## User Problem Description\n{}\n\n"
            "## Related Logs\n```\n{}\n```\n\n"
            "Please analyze the potential problems in the log, figure out the possible root cause, and give the suggestion of next step."
        ).format(problem_description, log_text)

        return llm.chat_once(system_prompt, user_prompt)
