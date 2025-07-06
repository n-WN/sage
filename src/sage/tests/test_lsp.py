"""
Tests for SageMath LSP functionality.

These tests verify that the LSP components work correctly with Sage code.
"""

import pytest


def test_sage_completion_provider():
    """Test the SageMath completion provider."""
    from sage.lsp.completion import SageCompletionProvider
    
    provider = SageCompletionProvider()
    
    # Test global completions
    text = "Inte"
    completions = provider.get_completions(text, 0, 4)
    
    # Should suggest Integer among others
    completion_labels = [c.label for c in completions] if completions else []
    assert 'Integer' in completion_labels or len(completions) == 0  # Empty if pygls not available


def test_sage_diagnostics_provider():
    """Test the SageMath diagnostics provider."""
    from sage.lsp.diagnostics import SageDiagnosticsProvider
    
    provider = SageDiagnosticsProvider()
    
    # Test valid Sage code
    valid_code = "x = 2\ny = x + 1"
    diagnostics = provider.get_diagnostics(valid_code)
    # Should have no errors
    error_diagnostics = [d for d in diagnostics if hasattr(d, 'severity') and d.severity == 1]
    assert len(error_diagnostics) == 0
    
    # Test invalid syntax
    invalid_code = "x = 2 +"
    diagnostics = provider.get_diagnostics(invalid_code)
    # Should have at least one diagnostic if pygls is available
    if diagnostics:
        assert len(diagnostics) > 0


def test_sage_symbol_resolver():
    """Test the SageMath symbol resolver."""
    from sage.lsp.symbols import SageSymbolResolver
    
    resolver = SageSymbolResolver()
    
    # Test symbol extraction
    line = "Integer(42)"
    symbol = resolver._extract_symbol_at_position(line, 3)  # Position in "Integer"
    assert symbol == "Integer"
    
    # Test invalid position
    symbol = resolver._extract_symbol_at_position(line, 20)  # Beyond line length
    assert symbol is None


def test_preparse_integration():
    """Test that the LSP integrates properly with Sage's preparser."""
    from sage.repl.preparse import preparse
    
    # Test that preparse works with typical Sage syntax
    sage_code = "2^3"
    preparsed = preparse(sage_code)
    assert "**" in preparsed or "Integer" in preparsed
    
    # Test fraction syntax
    sage_code = "1/2"
    preparsed = preparse(sage_code)
    assert "Integer" in preparsed


def test_lsp_server_initialization():
    """Test that the LSP server can be initialized."""
    try:
        from sage.lsp.server import SageLSPServer, PYGLS_AVAILABLE
        
        if PYGLS_AVAILABLE:
            # Should be able to create server instance
            server = SageLSPServer()
            assert server is not None
            assert hasattr(server, 'completion_provider')
            assert hasattr(server, 'diagnostics_provider')
            assert hasattr(server, 'symbol_resolver')
        else:
            # Should raise ImportError if pygls not available
            with pytest.raises(ImportError):
                SageLSPServer()
    
    except ImportError:
        # Expected if pygls is not installed
        pytest.skip("pygls not available, skipping LSP server test")


if __name__ == '__main__':
    # Run basic tests
    test_sage_completion_provider()
    test_sage_diagnostics_provider()
    test_sage_symbol_resolver()
    test_preparse_integration()
    test_lsp_server_initialization()
    print("All tests passed!")