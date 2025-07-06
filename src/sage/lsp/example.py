#!/usr/bin/env python3
"""
Example usage of the SageMath Language Server Protocol implementation.

This script demonstrates how to start the LSP server and shows what
functionality it provides.
"""

def demo_lsp_features():
    """Demonstrate LSP features without requiring a full server."""
    print("SageMath LSP Demo")
    print("=================")
    
    try:
        from sage.lsp.completion import SageCompletionProvider
        from sage.lsp.diagnostics import SageDiagnosticsProvider
        from sage.lsp.symbols import SageSymbolResolver
        
        print("\n1. Code Completion Demo:")
        completion_provider = SageCompletionProvider()
        
        # Example: Get completions for "Inte"
        text = "Inte"
        completions = completion_provider.get_completions(text, 0, 4)
        if completions:
            print(f"Completions for '{text}':")
            for comp in completions[:5]:  # Show first 5
                print(f"  - {comp.label}")
        else:
            print("  (Completions require pygls to be installed)")
        
        print("\n2. Diagnostics Demo:")
        diagnostics_provider = SageDiagnosticsProvider()
        
        # Example: Check valid code
        valid_code = "x = Integer(42)\ny = x^2"
        diagnostics = diagnostics_provider.get_diagnostics(valid_code)
        print(f"Diagnostics for valid code: {len(diagnostics)} issues found")
        
        # Example: Check code with potential issues
        issue_code = "x = 2**3\ny = 1/2"  # Uses ** instead of ^, integer division
        diagnostics = diagnostics_provider.get_diagnostics(issue_code)
        if diagnostics:
            print(f"Diagnostics for code with style issues: {len(diagnostics)} suggestions")
            for diag in diagnostics:
                if hasattr(diag, 'message'):
                    print(f"  - {diag.message}")
        else:
            print("  (Diagnostics require pygls to be installed)")
        
        print("\n3. Symbol Resolution Demo:")
        symbol_resolver = SageSymbolResolver()
        
        # Example: Extract symbol
        line = "Integer(42).factor()"
        symbol = symbol_resolver._extract_symbol_at_position(line, 3)
        print(f"Symbol at position 3 in '{line}': '{symbol}'")
        
        symbol = symbol_resolver._extract_symbol_at_position(line, 12)
        print(f"Symbol at position 12 in '{line}': '{symbol}'")
        
        print("\n4. Preparser Integration Demo:")
        from sage.repl.preparse import preparse
        
        sage_examples = [
            "2^3",
            "1/2", 
            "x.0",
            "matrix([[1,2],[3,4]])"
        ]
        
        print("Sage code -> Preparsed Python:")
        for example in sage_examples:
            preparsed = preparse(example)
            print(f"  {example:20} -> {preparsed}")
    
    except ImportError as e:
        print(f"Error importing LSP modules: {e}")
        print("Make sure SageMath is properly installed.")


def show_lsp_server_usage():
    """Show how to start the LSP server."""
    print("\n\nStarting the LSP Server:")
    print("========================")
    print("To start the SageMath LSP server, you can:")
    print()
    print("1. Use the CLI module directly:")
    print("   python -m sage.lsp.cli --host localhost --port 8080")
    print()
    print("2. Use it with stdio (for editor integration):")
    print("   python -m sage.lsp.cli --stdio")
    print()
    print("3. Use it programmatically:")
    print("   from sage.lsp.server import start_sage_lsp_server")
    print("   start_sage_lsp_server('localhost', 8080)")
    print()
    print("Note: The LSP server requires 'pygls' to be installed:")
    print("      pip install pygls")
    print()
    print("Editor Integration:")
    print("- VS Code: Install a generic LSP client extension")
    print("- Vim/Neovim: Use LSP clients like coc.nvim or nvim-lspconfig")
    print("- Emacs: Use lsp-mode or eglot")


if __name__ == '__main__':
    demo_lsp_features()
    show_lsp_server_usage()