# sage_setup: distribution = sagemath-repl
"""
SageMath Language Server Implementation

This module implements the core Language Server Protocol server for SageMath,
providing language features like completion, diagnostics, and symbol resolution.
"""

import logging
import re
from typing import List, Optional, Union

try:
    from pygls.lsp.methods import (
        COMPLETION, DEFINITION, HOVER, INITIALIZE, SHUTDOWN, 
        TEXT_DOCUMENT_DID_CHANGE, TEXT_DOCUMENT_DID_OPEN, TEXT_DOCUMENT_DID_SAVE
    )
    from pygls.lsp.types import (
        CompletionItem, CompletionItemKind, CompletionList, CompletionParams,
        DefinitionParams, Hover, HoverParams, InitializeParams, Location,
        MarkupContent, MarkupKind, Position, Range, TextDocumentPositionParams
    )
    from pygls.server import LanguageServer
    PYGLS_AVAILABLE = True
except ImportError:
    PYGLS_AVAILABLE = False
    LanguageServer = object  # Fallback for when pygls is not available

# Import Sage modules lazily to avoid import issues
def _lazy_import_sage():
    """Lazy import of Sage modules."""
    try:
        from sage.repl.preparse import preparse
        from sage.misc.sageinspect import sage_getdoc, sage_getsource, sage_getfile
        return preparse, sage_getdoc, sage_getsource, sage_getfile
    except ImportError:
        return None, None, None, None

from sage.lsp.completion import SageCompletionProvider
from sage.lsp.diagnostics import SageDiagnosticsProvider
from sage.lsp.symbols import SageSymbolResolver


logger = logging.getLogger(__name__)


class SageLSPServer(LanguageServer):
    """
    Language Server Protocol implementation for SageMath.
    
    This server provides intelligent code assistance for Sage code including:
    - Code completion
    - Syntax diagnostics  
    - Symbol resolution
    - Hover information
    - Go to definition
    """
    
    def __init__(self, *args, **kwargs):
        if not PYGLS_AVAILABLE:
            raise ImportError("pygls is required for LSP functionality. Install it with: pip install pygls")
        
        super().__init__(*args, **kwargs)
        
        # Initialize providers
        self.completion_provider = SageCompletionProvider()
        self.diagnostics_provider = SageDiagnosticsProvider()
        self.symbol_resolver = SageSymbolResolver()
        
        # Store document contents
        self.documents = {}
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register LSP message handlers."""
        
        @self.feature(INITIALIZE)
        def initialize(params: InitializeParams):
            """Initialize the language server."""
            logger.info("Initializing SageMath LSP server")
            return {
                'capabilities': {
                    'textDocumentSync': 1,  # Full document sync
                    'completionProvider': {
                        'triggerCharacters': ['.', '(', '[']
                    },
                    'hoverProvider': True,
                    'definitionProvider': True,
                }
            }
        
        @self.feature(TEXT_DOCUMENT_DID_OPEN)
        def did_open(params):
            """Handle document open."""
            uri = params.text_document.uri
            text = params.text_document.text
            self.documents[uri] = text
            
            # Provide diagnostics
            diagnostics = self.diagnostics_provider.get_diagnostics(text)
            self.publish_diagnostics(uri, diagnostics)
        
        @self.feature(TEXT_DOCUMENT_DID_CHANGE)
        def did_change(params):
            """Handle document changes."""
            uri = params.text_document.uri
            for change in params.content_changes:
                if hasattr(change, 'text'):
                    # Full document update
                    self.documents[uri] = change.text
                else:
                    # Incremental update - for now just store the full text
                    self.documents[uri] = change.text
            
            # Provide updated diagnostics
            text = self.documents[uri]
            diagnostics = self.diagnostics_provider.get_diagnostics(text)
            self.publish_diagnostics(uri, diagnostics)
        
        @self.feature(TEXT_DOCUMENT_DID_SAVE)
        def did_save(params):
            """Handle document save."""
            # Re-run diagnostics on save
            uri = params.text_document.uri
            if uri in self.documents:
                text = self.documents[uri]
                diagnostics = self.diagnostics_provider.get_diagnostics(text)
                self.publish_diagnostics(uri, diagnostics)
        
        @self.feature(COMPLETION)
        def completion(params: CompletionParams):
            """Provide code completion."""
            uri = params.text_document.uri
            position = params.position
            
            if uri not in self.documents:
                return CompletionList(is_incomplete=False, items=[])
            
            text = self.documents[uri]
            completions = self.completion_provider.get_completions(
                text, position.line, position.character
            )
            
            return CompletionList(is_incomplete=False, items=completions)
        
        @self.feature(HOVER)
        def hover(params: HoverParams):
            """Provide hover information."""
            uri = params.text_document.uri
            position = params.position
            
            if uri not in self.documents:
                return None
            
            text = self.documents[uri]
            hover_info = self._get_hover_info(text, position.line, position.character)
            
            if hover_info:
                return Hover(
                    contents=MarkupContent(
                        kind=MarkupKind.Markdown,
                        value=hover_info
                    )
                )
            return None
        
        @self.feature(DEFINITION)
        def definition(params: DefinitionParams):
            """Provide go-to-definition."""
            uri = params.text_document.uri
            position = params.position
            
            if uri not in self.documents:
                return None
            
            text = self.documents[uri]
            location = self.symbol_resolver.get_definition_location(
                text, position.line, position.character
            )
            
            return location
        
        @self.feature(SHUTDOWN)
        def shutdown(params=None):
            """Shutdown the server."""
            logger.info("Shutting down SageMath LSP server")
    
    def _get_hover_info(self, text: str, line: int, character: int) -> Optional[str]:
        """Get hover information for symbol at position."""
        try:
            # Lazy import sage modules
            _, sage_getdoc, _, _ = _lazy_import_sage()
            if not sage_getdoc:
                return None
            
            lines = text.split('\n')
            if line >= len(lines):
                return None
            
            current_line = lines[line]
            if character >= len(current_line):
                return None
            
            # Extract word at position
            word_match = re.search(r'\b\w+\b', current_line[character:])
            if not word_match:
                # Look backwards
                word_match = re.search(r'\b\w+\b', current_line[:character][::-1])
                if word_match:
                    word = word_match.group()[::-1]
                else:
                    return None
            else:
                word = word_match.group()
            
            if not word:
                return None
            
            # Try to get documentation for the symbol
            try:
                # Import sage modules to get access to symbols
                import sage.all
                sage_globals = sage.all.__dict__
                
                # Try to resolve the symbol
                if word in sage_globals:
                    obj = sage_globals[word]
                    doc = sage_getdoc(obj)
                    if doc:
                        return f"**{word}**\n\n{doc}"
                
                # Try as attribute access (e.g., for methods)
                context_line = current_line.strip()
                if '.' in context_line:
                    # Simple attribute resolution
                    parts = context_line.split('.')
                    if len(parts) >= 2:
                        try:
                            obj_name = parts[-2].strip()
                            attr_name = parts[-1].strip()
                            if obj_name in sage_globals:
                                obj = sage_globals[obj_name]
                                if hasattr(obj, attr_name):
                                    attr_obj = getattr(obj, attr_name)
                                    doc = sage_getdoc(attr_obj)
                                    if doc:
                                        return f"**{obj_name}.{attr_name}**\n\n{doc}"
                        except:
                            pass
                
            except Exception as e:
                logger.debug(f"Error getting hover info: {e}")
                return None
            
            return None
            
        except Exception as e:
            logger.error(f"Error in hover info: {e}")
            return None


def start_sage_lsp_server(host='localhost', port=8080):
    """
    Start the SageMath LSP server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
    """
    if not PYGLS_AVAILABLE:
        raise ImportError("pygls is required for LSP functionality. Install it with: pip install pygls")
    
    server = SageLSPServer()
    logger.info(f"Starting SageMath LSP server on {host}:{port}")
    server.start_tcp(host, port)


if __name__ == '__main__':
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='SageMath Language Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--log-level', default='INFO', help='Log level')
    
    args = parser.parse_args()
    
    logging.basicConfig(level=getattr(logging, args.log_level.upper()))
    
    try:
        start_sage_lsp_server(args.host, args.port)
    except KeyboardInterrupt:
        print("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)