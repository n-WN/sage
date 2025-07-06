# sage_setup: distribution = sagemath-repl
"""
Symbol resolver for SageMath LSP.

This module provides symbol resolution and go-to-definition functionality
by leveraging Sage's introspection capabilities.
"""

import re
from typing import Optional

try:
    from pygls.lsp.types import Location, Position, Range
    PYGLS_AVAILABLE = True
except ImportError:
    PYGLS_AVAILABLE = False
    Location = object
    Position = object
    Range = object

# Lazy import of Sage inspection functions
def _lazy_import_sage_inspect():
    """Lazy import of Sage inspection functions."""
    try:
        from sage.misc.sageinspect import sage_getfile, sage_getsourcelines
        return sage_getfile, sage_getsourcelines
    except ImportError:
        return None, None


class SageSymbolResolver:
    """Resolves symbols and provides go-to-definition functionality."""
    
    def get_definition_location(self, text: str, line: int, character: int) -> Optional[Location]:
        """
        Get the definition location for a symbol at the given position.
        
        Args:
            text: Full document text
            line: Line number (0-based)
            character: Character position (0-based)
            
        Returns:
            Location of the symbol definition, or None if not found
        """
        if not PYGLS_AVAILABLE:
            return None
        
        try:
            lines = text.split('\n')
            if line >= len(lines):
                return None
            
            current_line = lines[line]
            if character >= len(current_line):
                return None
            
            # Extract the symbol at the position
            symbol = self._extract_symbol_at_position(current_line, character)
            if not symbol:
                return None
            
            # Try to resolve the symbol
            location = self._resolve_symbol_location(symbol)
            return location
        
        except Exception as e:
            import logging
            logging.error(f"Error in symbol resolution: {e}")
            return None
    
    def _extract_symbol_at_position(self, line: str, character: int) -> Optional[str]:
        """Extract the symbol name at the given character position."""
        # Find word boundaries around the character position
        start = character
        end = character
        
        # Move start backwards to find word start
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == '_'):
            start -= 1
        
        # Move end forwards to find word end
        while end < len(line) and (line[end].isalnum() or line[end] == '_'):
            end += 1
        
        if start == end:
            return None
        
        symbol = line[start:end]
        if not symbol or not symbol[0].isalpha() and symbol[0] != '_':
            return None
        
        return symbol
    
    def _resolve_symbol_location(self, symbol: str) -> Optional[Location]:
        """Resolve the location of a symbol definition."""
        try:
            # Try to get the symbol from Sage namespace
            import sage.all
            sage_globals = sage.all.__dict__
            
            if symbol in sage_globals:
                obj = sage_globals[symbol]
                return self._get_object_location(obj, symbol)
            
            # Try to resolve as a module or class
            try:
                # Check if it's a Sage object we can introspect
                import sage
                sage_modules = [
                    'sage.rings', 'sage.matrix', 'sage.plot', 'sage.graphs',
                    'sage.geometry', 'sage.functions', 'sage.calculus'
                ]
                
                for module_name in sage_modules:
                    try:
                        module = __import__(module_name, fromlist=[symbol])
                        if hasattr(module, symbol):
                            obj = getattr(module, symbol)
                            return self._get_object_location(obj, symbol)
                    except:
                        continue
            
            except Exception:
                pass
            
            return None
        
        except Exception as e:
            import logging
            logging.debug(f"Could not resolve symbol {symbol}: {e}")
            return None
    
    def _get_object_location(self, obj, symbol: str) -> Optional[Location]:
        """Get the file location for an object."""
        sage_getfile, sage_getsourcelines = _lazy_import_sage_inspect()
        if not sage_getfile or not sage_getsourcelines:
            return None
        
        try:
            # Get the source file
            filename = sage_getfile(obj)
            if not filename:
                return None
            
            # Try to get source lines to find the definition line
            try:
                source_lines, start_line = sage_getsourcelines(obj)
                if source_lines and start_line:
                    # Convert to 0-based line number
                    definition_line = start_line - 1
                    
                    # Find the actual definition line (look for 'def' or 'class')
                    for i, line in enumerate(source_lines):
                        if ('def ' + symbol in line or 
                            'class ' + symbol in line or
                            symbol + ' = ' in line):
                            definition_line = start_line - 1 + i
                            break
                    
                    return Location(
                        uri=f"file://{filename}",
                        range=Range(
                            start=Position(line=definition_line, character=0),
                            end=Position(line=definition_line, character=0)
                        )
                    )
            
            except Exception:
                # If we can't get source lines, just return the file location
                return Location(
                    uri=f"file://{filename}",
                    range=Range(
                        start=Position(line=0, character=0),
                        end=Position(line=0, character=0)
                    )
                )
        
        except Exception as e:
            import logging
            logging.debug(f"Could not get location for object {symbol}: {e}")
            return None
        
        return None