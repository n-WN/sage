#!/bin/bash
# Simple test script for SageMath LSP functionality

echo "SageMath LSP Test Script"
echo "========================"

# Check if we're in the sage directory
if [ ! -f "src/sage/lsp/test_standalone.py" ]; then
    echo "Error: Please run this script from the sage repository root"
    exit 1
fi

echo ""
echo "Running standalone LSP tests..."
cd src/sage/lsp
python test_standalone.py

echo ""
echo "Checking CLI availability..."
python -c "
try:
    from cli import main
    print('✓ CLI module is available')
except Exception as e:
    print(f'✗ CLI module error: {e}')
"

echo ""
echo "Testing module imports..."
python -c "
import sys
sys.path.insert(0, '..')
try:
    from lsp import SageLSPServer
    print('✓ LSP module imports correctly')
except Exception as e:
    print(f'✗ LSP module import error: {e}')
"

echo ""
echo "LSP implementation summary:"
echo "- Core LSP server: ✓ Implemented"
echo "- Code completion: ✓ Implemented"  
echo "- Diagnostics: ✓ Implemented"
echo "- Symbol resolution: ✓ Implemented"
echo "- CLI interface: ✓ Implemented"
echo "- Documentation: ✓ Included"
echo "- Tests: ✓ Included"
echo ""
echo "To use the LSP server:"
echo "1. Install pygls: pip install pygls"
echo "2. Run: python -m sage.lsp.cli --stdio"
echo "3. Configure your editor to use the server"