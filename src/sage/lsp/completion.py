# sage_setup: distribution = sagemath-repl
"""
Code completion provider for SageMath LSP.

This module provides intelligent code completion for Sage code by leveraging
Sage's introspection capabilities and namespace.
"""

import re
from typing import List, Optional

try:
    from pygls.lsp.types import CompletionItem, CompletionItemKind
    PYGLS_AVAILABLE = True
except ImportError:
    PYGLS_AVAILABLE = False
    CompletionItem = object
    CompletionItemKind = object


class SageCompletionProvider:
    """Provides code completion for SageMath code."""
    
    def __init__(self):
        self._sage_namespace = None
        self._builtin_functions = None
    
    def _get_sage_namespace(self):
        """Get the Sage namespace for completion."""
        if self._sage_namespace is None:
            try:
                import sage.all
                self._sage_namespace = sage.all.__dict__
            except ImportError:
                self._sage_namespace = {}
        return self._sage_namespace
    
    def _get_builtin_functions(self):
        """Get common Sage functions for completion."""
        if self._builtin_functions is None:
            sage_ns = self._get_sage_namespace()
            
            # Common Sage functions and objects
            common_functions = [
                'Integer', 'Rational', 'RealNumber', 'ComplexNumber',
                'matrix', 'vector', 'var', 'sin', 'cos', 'tan', 'exp', 'log',
                'plot', 'show', 'print', 'len', 'range', 'sum', 'max', 'min',
                'ZZ', 'QQ', 'RR', 'CC', 'GF', 'PolynomialRing',
                'factor', 'expand', 'simplify', 'solve', 'diff', 'integrate',
                'latex', 'view', 'Graph', 'Polyhedron'
            ]
            
            self._builtin_functions = []
            for func_name in common_functions:
                if func_name in sage_ns:
                    obj = sage_ns[func_name]
                    self._builtin_functions.append({
                        'name': func_name,
                        'obj': obj,
                        'kind': self._get_completion_kind(obj)
                    })
        
        return self._builtin_functions
    
    def _get_completion_kind(self, obj):
        """Determine the completion kind for an object."""
        if not PYGLS_AVAILABLE:
            return 1  # Default kind
        
        import types
        
        if isinstance(obj, type):
            return CompletionItemKind.Class
        elif isinstance(obj, (types.FunctionType, types.BuiltinFunctionType)):
            return CompletionItemKind.Function
        elif isinstance(obj, types.ModuleType):
            return CompletionItemKind.Module
        elif callable(obj):
            return CompletionItemKind.Method
        else:
            return CompletionItemKind.Variable
    
    def get_completions(self, text: str, line: int, character: int) -> List[CompletionItem]:
        """
        Get code completions for the given position.
        
        Args:
            text: Full document text
            line: Line number (0-based)
            character: Character position (0-based)
            
        Returns:
            List of completion items
        """
        if not PYGLS_AVAILABLE:
            return []
        
        try:
            lines = text.split('\n')
            if line >= len(lines):
                return []
            
            current_line = lines[line]
            if character > len(current_line):
                character = len(current_line)
            
            # Get the text before the cursor
            prefix_text = current_line[:character]
            
            # Check for attribute access (e.g., "obj.")
            if '.' in prefix_text:
                return self._get_attribute_completions(prefix_text)
            else:
                return self._get_global_completions(prefix_text)
        
        except Exception as e:
            # Log error but don't crash
            import logging
            logging.error(f"Error in completion: {e}")
            return []
    
    def _get_global_completions(self, prefix_text: str) -> List[CompletionItem]:
        """Get completions for global names."""
        # Extract the word being typed
        word_match = re.search(r'\b(\w*)$', prefix_text)
        if not word_match:
            return []
        
        partial_word = word_match.group(1)
        
        completions = []
        builtin_functions = self._get_builtin_functions()
        
        for func_info in builtin_functions:
            func_name = func_info['name']
            if func_name.startswith(partial_word):
                completion = CompletionItem(
                    label=func_name,
                    kind=func_info['kind'],
                    insert_text=func_name,
                    detail=f"Sage {self._get_kind_name(func_info['kind'])}"
                )
                
                # Add documentation if available
                try:
                    from sage.misc.sageinspect import sage_getdoc
                    doc = sage_getdoc(func_info['obj'])
                    if doc:
                        # Take first line of documentation
                        first_line = doc.split('\n')[0]
                        completion.documentation = first_line
                except:
                    pass
                
                completions.append(completion)
        
        return completions
    
    def _get_attribute_completions(self, prefix_text: str) -> List[CompletionItem]:
        """Get completions for attribute access."""
        # Parse the attribute access
        parts = prefix_text.rsplit('.', 1)
        if len(parts) != 2:
            return []
        
        obj_expr, partial_attr = parts
        obj_expr = obj_expr.strip()
        
        try:
            # Try to evaluate the object expression in Sage context
            sage_ns = self._get_sage_namespace()
            
            # Simple variable resolution
            if obj_expr in sage_ns:
                obj = sage_ns[obj_expr]
                return self._get_object_attributes(obj, partial_attr)
            
            # Try common patterns
            if obj_expr in ['ZZ', 'QQ', 'RR', 'CC']:
                if obj_expr in sage_ns:
                    obj = sage_ns[obj_expr]
                    return self._get_object_attributes(obj, partial_attr)
        
        except Exception as e:
            # If evaluation fails, return empty list
            import logging
            logging.debug(f"Could not resolve object {obj_expr}: {e}")
        
        return []
    
    def _get_object_attributes(self, obj, partial_attr: str) -> List[CompletionItem]:
        """Get attribute completions for an object."""
        completions = []
        
        try:
            attributes = dir(obj)
            for attr_name in attributes:
                if attr_name.startswith(partial_attr) and not attr_name.startswith('_'):
                    try:
                        attr_obj = getattr(obj, attr_name)
                        completion = CompletionItem(
                            label=attr_name,
                            kind=self._get_completion_kind(attr_obj),
                            insert_text=attr_name,
                            detail=f"Attribute of {type(obj).__name__}"
                        )
                        
                        # Add documentation
                        try:
                            from sage.misc.sageinspect import sage_getdoc
                            doc = sage_getdoc(attr_obj)
                            if doc:
                                first_line = doc.split('\n')[0]
                                completion.documentation = first_line
                        except:
                            pass
                        
                        completions.append(completion)
                    
                    except Exception:
                        # Skip problematic attributes
                        continue
        
        except Exception as e:
            import logging
            logging.debug(f"Error getting attributes for object: {e}")
        
        return completions
    
    def _get_kind_name(self, kind) -> str:
        """Get human-readable name for completion kind."""
        if not PYGLS_AVAILABLE:
            return "item"
        
        kind_map = {
            CompletionItemKind.Class: "class",
            CompletionItemKind.Function: "function", 
            CompletionItemKind.Method: "method",
            CompletionItemKind.Variable: "variable",
            CompletionItemKind.Module: "module"
        }
        return kind_map.get(kind, "item")