"""
PEnhance Proxy Configuration
"""

import os
from pathlib import Path

# Base paths
PROJECT_DIR = Path(__file__).parent.parent
LOGS_DIR = PROJECT_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Proxy settings
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 8080

# GLM API settings
GLM_API_URL = os.getenv("GLM_API_URL", "https://open.bigmodel.cn/api/anthropic/v1")
GLM_API_KEY = os.getenv("GLM_API_KEY", "ed79dfb6bd5d442b9818011010d6faed.ExkY3SyIQqoyDpaO")

# OpenClaw settings (optional)
OPENCLAW_URL = os.getenv("OPENCLAW_URL", "http://139.224.42.111:18789")
OPENCLAW_TOKEN = os.getenv("OPENCLAW_TOKEN", "VqCkbaVWUtIQv5A-AYKSXTegmNWy2V2X8Y06KcZGA30")
ENABLE_OPENCLAW = os.getenv("ENABLE_OPENCLAW", "false").lower() == "true"

# Enhancement settings
CONTEXT_COMPRESSION_THRESHOLD = 100000  # tokens
ENABLE_CONTEXT_COMPRESSION = True
ENABLE_CODE_TEMPLATES = True
ENABLE_BEST_PRACTICES = True

# Fallback settings
FALLBACK_ON_ERROR = True
OPENCLAW_TIMEOUT = 5  # seconds
GLM_TIMEOUT = 120  # seconds

# Logging
LOG_FILE = LOGS_DIR / "proxy.log"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
