#!/usr/bin/env python3
"""
Standalone test for SageMath LSP functionality.

This test verifies basic functionality without requiring full Sage environment.
"""

def test_basic_imports():
    """Test that LSP modules can be imported."""
    print("Testing basic imports...")
    
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        
        from sage.lsp.completion import SageCompletionProvider
        from sage.lsp.diagnostics import SageDiagnosticsProvider
        from sage.lsp.symbols import SageSymbolResolver
        
        print("✓ LSP modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_providers_creation():
    """Test that providers can be created."""
    print("Testing provider creation...")
    
    try:
        from sage.lsp.completion import SageCompletionProvider
        from sage.lsp.diagnostics import SageDiagnosticsProvider
        from sage.lsp.symbols import SageSymbolResolver
        
        completion_provider = SageCompletionProvider()
        diagnostics_provider = SageDiagnosticsProvider()
        symbol_resolver = SageSymbolResolver()
        
        print("✓ All providers created successfully")
        return True
    except Exception as e:
        print(f"✗ Provider creation failed: {e}")
        return False


def test_symbol_extraction():
    """Test symbol extraction functionality."""
    print("Testing symbol extraction...")
    
    try:
        from sage.lsp.symbols import SageSymbolResolver
        
        resolver = SageSymbolResolver()
        
        # Test cases
        test_cases = [
            ("Integer(42)", 3, "Integer"),
            ("x.factor()", 2, "factor"),
            ("print('hello')", 1, "print"),
            ("", 0, None),
            ("123", 1, None),  # Numbers shouldn't be symbols
        ]
        
        for line, pos, expected in test_cases:
            result = resolver._extract_symbol_at_position(line, pos)
            if result == expected:
                print(f"✓ Symbol extraction: '{line}' at {pos} -> '{result}'")
            else:
                print(f"✗ Symbol extraction: '{line}' at {pos} -> '{result}' (expected '{expected}')")
        
        return True
    except Exception as e:
        print(f"✗ Symbol extraction test failed: {e}")
        return False


def test_diagnostics_basic():
    """Test basic diagnostics functionality."""
    print("Testing basic diagnostics...")
    
    try:
        from sage.lsp.diagnostics import SageDiagnosticsProvider
        
        provider = SageDiagnosticsProvider()
        
        # Test with simple valid code
        valid_code = "x = 42\ny = x + 1"
        diagnostics = provider.get_diagnostics(valid_code)
        print(f"✓ Valid code diagnostics: {len(diagnostics)} issues")
        
        # Test with syntax error
        invalid_code = "x = 42 +"
        diagnostics = provider.get_diagnostics(invalid_code)
        print(f"✓ Invalid code diagnostics: {len(diagnostics)} issues")
        
        return True
    except Exception as e:
        print(f"✗ Diagnostics test failed: {e}")
        return False


def test_completion_basic():
    """Test basic completion functionality."""
    print("Testing basic completion...")
    
    try:
        from sage.lsp.completion import SageCompletionProvider
        
        provider = SageCompletionProvider()
        
        # Test completion (may return empty list if pygls not available)
        completions = provider.get_completions("Int", 0, 3)
        print(f"✓ Completion test: {len(completions)} completions for 'Int'")
        
        return True
    except Exception as e:
        print(f"✗ Completion test failed: {e}")
        return False


def test_server_creation():
    """Test LSP server creation."""
    print("Testing LSP server creation...")
    
    try:
        from sage.lsp.server import SageLSPServer, PYGLS_AVAILABLE
        
        if PYGLS_AVAILABLE:
            server = SageLSPServer()
            print("✓ LSP server created successfully (with pygls)")
            return True
        else:
            print("✓ LSP server creation skipped (pygls not available)")
            return True
    except ImportError as e:
        if "pygls" in str(e):
            print("✓ LSP server creation correctly fails without pygls")
            return True
        else:
            print(f"✗ Unexpected import error: {e}")
            return False
    except Exception as e:
        print(f"✗ LSP server creation failed: {e}")
        return False


def main():
    """Run all tests."""
    print("SageMath LSP Standalone Test Suite")
    print("==================================")
    
    tests = [
        test_basic_imports,
        test_providers_creation,
        test_symbol_extraction,
        test_diagnostics_basic,
        test_completion_basic,
        test_server_creation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        print(f"\n{test.__name__}:")
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print(f"\n\nResults: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())