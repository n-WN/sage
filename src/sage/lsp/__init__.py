# sage_setup: distribution = sagemath-repl
"""
SageMath Language Server Protocol (LSP) Implementation

This module provides a Language Server Protocol implementation for SageMath,
enabling advanced code editing features like code completion, diagnostics,
symbol resolution, and hover information in LSP-compatible editors.

The LSP server integrates with Sage's existing preparser and introspection
capabilities to provide intelligent code assistance for Sage code.
"""

from sage.lsp.server import SageLSPServer

__all__ = ['SageLSPServer']