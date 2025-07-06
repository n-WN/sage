# sage_setup: distribution = sagemath-repl
"""
Diagnostics provider for SageMath LSP.

This module provides syntax and semantic diagnostics for Sage code by
leveraging Sage's preparser and Python's AST parsing capabilities.
"""

import ast
import re
from typing import List

try:
    from pygls.lsp.types import Diagnostic, DiagnosticSeverity, Position, Range
    PYGLS_AVAILABLE = True
except ImportError:
    PYGLS_AVAILABLE = False
    Diagnostic = object
    DiagnosticSeverity = object
    Position = object
    Range = object

# Lazy import of Sage preparse to avoid import issues
def _lazy_import_preparse():
    """Lazy import of Sage preparse function."""
    try:
        from sage.repl.preparse import preparse
        return preparse
    except ImportError:
        return None


class SageDiagnosticsProvider:
    """Provides diagnostics for SageMath code."""
    
    def get_diagnostics(self, text: str) -> List[Diagnostic]:
        """
        Get diagnostics for the given Sage code.
        
        Args:
            text: The Sage source code to analyze
            
        Returns:
            List of diagnostics (errors, warnings)
        """
        if not PYGLS_AVAILABLE:
            return []
        
        diagnostics = []
        
        # Check for syntax errors using Sage preparser
        preparse = _lazy_import_preparse()
        if not preparse:
            return diagnostics
        
        try:
            # First try to preparse the code
            preparsed_code = preparse(text)
            
            # Then try to parse the preparsed code as Python AST
            try:
                ast.parse(preparsed_code)
            except SyntaxError as e:
                # Convert syntax error to diagnostic
                line = e.lineno - 1 if e.lineno else 0
                col = e.offset - 1 if e.offset else 0
                
                diagnostic = Diagnostic(
                    range=Range(
                        start=Position(line=line, character=col),
                        end=Position(line=line, character=col + 1)
                    ),
                    message=f"Syntax Error: {e.msg}",
                    severity=DiagnosticSeverity.Error,
                    source="sage-lsp"
                )
                diagnostics.append(diagnostic)
        
        except Exception as e:
            # If preparsing fails, report as error
            diagnostic = Diagnostic(
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=0, character=1)
                ),
                message=f"Preparse Error: {str(e)}",
                severity=DiagnosticSeverity.Error,
                source="sage-lsp"
            )
            diagnostics.append(diagnostic)
        
        # Add additional Sage-specific checks
        diagnostics.extend(self._check_sage_specific_issues(text))
        
        return diagnostics
    
    def _check_sage_specific_issues(self, text: str) -> List[Diagnostic]:
        """Check for Sage-specific issues."""
        if not PYGLS_AVAILABLE:
            return []
        
        diagnostics = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines):
            # Check for common Sage issues
            
            # Warn about using Python's pow instead of Sage's ^
            if '**' in line and not line.strip().startswith('#'):
                # Look for numeric base with ** (suggest using ^ instead)
                if re.search(r'\d+\s*\*\*', line):
                    col = line.find('**')
                    diagnostic = Diagnostic(
                        range=Range(
                            start=Position(line=line_num, character=col),
                            end=Position(line=line_num, character=col + 2)
                        ),
                        message="Consider using ^ for exponentiation in Sage instead of **",
                        severity=DiagnosticSeverity.Information,
                        source="sage-lsp"
                    )
                    diagnostics.append(diagnostic)
            
            # Check for division that might need Integer() wrapping
            if re.search(r'\b\d+\s*/\s*\d+\b', line) and not line.strip().startswith('#'):
                matches = re.finditer(r'\b(\d+)\s*/\s*(\d+)\b', line)
                for match in matches:
                    col = match.start()
                    diagnostic = Diagnostic(
                        range=Range(
                            start=Position(line=line_num, character=col),
                            end=Position(line=line_num, character=match.end())
                        ),
                        message="Division of integers in Sage creates exact rational numbers. Use // for integer division.",
                        severity=DiagnosticSeverity.Information,
                        source="sage-lsp"
                    )
                    diagnostics.append(diagnostic)
            
            # Check for potentially undefined variables (simple heuristic)
            # This is a basic check - a full implementation would need symbol table analysis
            if re.search(r'\bx\b', line) and 'var(' not in text and 'x=' not in text:
                matches = re.finditer(r'\bx\b', line)
                for match in matches:
                    # Skip if it's in a string or comment
                    if self._is_in_string_or_comment(line, match.start()):
                        continue
                    
                    col = match.start()
                    diagnostic = Diagnostic(
                        range=Range(
                            start=Position(line=line_num, character=col),
                            end=Position(line=line_num, character=match.end())
                        ),
                        message="Variable 'x' may not be defined. Use var('x') to declare symbolic variables.",
                        severity=DiagnosticSeverity.Warning,
                        source="sage-lsp"
                    )
                    diagnostics.append(diagnostic)
                    break  # Only warn once per line
        
        return diagnostics
    
    def _is_in_string_or_comment(self, line: str, pos: int) -> bool:
        """Check if position is inside a string or comment."""
        # Simple check for comments
        comment_pos = line.find('#')
        if comment_pos != -1 and pos >= comment_pos:
            return True
        
        # Simple check for strings (basic implementation)
        in_single_quote = False
        in_double_quote = False
        
        for i, char in enumerate(line[:pos]):
            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
        
        return in_single_quote or in_double_quote