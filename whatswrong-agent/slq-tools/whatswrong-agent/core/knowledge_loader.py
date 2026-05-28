# -*- coding: utf-8 -*-
"""
KnowledgeLoader: 加载 knowledge/ 和 skills/ 目录下的知识文件
- knowledge/*.txt  : 业务知识文本（日志位置、关注点等）
- skills/*.json    : 技能定义（可用诊断命令及其描述）
"""

import os
import json
import logging

logger = logging.getLogger(__name__)


class KnowledgeLoader(object):

    def __init__(self, knowledge_dir):
        self.knowledge_dir = knowledge_dir
        self._knowledge_texts = {}   # name -> str
        self._skills = {}            # name -> dict
        self._load_all()

    def _load_all(self):
        kdir = self.knowledge_dir
        if not os.path.isdir(kdir):
            logger.warning("knowledge_dir does not exist: %s", kdir)
            return

        for fname in os.listdir(kdir):
            fpath = os.path.join(kdir, fname)
            if fname.endswith(".md"):
                with open(fpath, "r", encoding="utf-8") as f:
                    self._knowledge_texts[fname[:-4]] = f.read()
                logger.info("Loaded knowledge file: %s", fname)
            elif fname.endswith(".json"):
                with open(fpath, "r", encoding="utf-8") as f:
                    self._skills[fname[:-5]] = json.load(f)
                logger.info("Loaded skill file: %s", fname)

    def get_system_context(self):
        parts = []
        for name, text in sorted(self._knowledge_texts.items()):
            parts.append("## Knowledge: {}\n{}".format(name, text.strip()))
        return "\n\n".join(parts)

    def get_available_tools(self):
        tools = []
        for skill_name, skill_data in self._skills.items():
            for tool in skill_data.get("tools", []):
                tool.setdefault("_skill", skill_name)
                tools.append(tool)
        return tools

    def get_log_sources(self):
        sources = []
        for skill_data in self._skills.values():
            sources.extend(skill_data.get("log_sources", []))
        return sources
