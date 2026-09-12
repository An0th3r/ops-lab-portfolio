"""Small service checks with automation-friendly reports."""

from .core import CheckResult, load_config, render_markdown, run_checks

__all__ = ["CheckResult", "load_config", "render_markdown", "run_checks"]

