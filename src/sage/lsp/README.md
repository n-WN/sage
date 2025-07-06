# SageMath Language Server Protocol (LSP) Implementation

This module provides a Language Server Protocol implementation for SageMath, enabling advanced code editing features in LSP-compatible editors such as VS Code, Vim/Neovim, Emacs, and others.

## Features

- **Code Completion**: Intelligent autocompletion for Sage functions, classes, and methods
- **Syntax Diagnostics**: Real-time error detection and Sage-specific style suggestions
- **Symbol Resolution**: Go-to-definition functionality for Sage objects
- **Hover Information**: Display documentation and type information on hover
- **Preparser Integration**: Seamless integration with Sage's preparser for proper syntax handling

## Installation

The LSP server requires the `pygls` (Python Generic Language Server) library:

```bash
pip install pygls
```

## Usage

### Starting the LSP Server

#### Command Line Interface

Start the server on TCP (for debugging):
```bash
python -m sage.lsp.cli --host localhost --port 8080
```

Start the server with stdio (for editor integration):
```bash
python -m sage.lsp.cli --stdio
```

#### Programmatic Usage

```python
from sage.lsp.server import start_sage_lsp_server

# Start TCP server
start_sage_lsp_server('localhost', 8080)

# Or create server instance directly
from sage.lsp.server import SageLSPServer
server = SageLSPServer()
server.start_io()  # For stdio communication
```

### Editor Integration

#### VS Code

1. Install a generic LSP client extension like "Generic LSP Client"
2. Configure it to use the SageMath LSP server:
   ```json
   {
     "genericLsp.clients": [
       {
         "name": "SageMath",
         "command": ["python", "-m", "sage.lsp.cli", "--stdio"],
         "fileExtensions": [".sage", ".py"]
       }
     ]
   }
   ```

#### Vim/Neovim

With `coc.nvim`:
```json
{
  "languageserver": {
    "sage": {
      "command": "python",
      "args": ["-m", "sage.lsp.cli", "--stdio"],
      "filetypes": ["sage", "python"]
    }
  }
}
```

With `nvim-lspconfig`:
```lua
local lspconfig = require('lspconfig')
local configs = require('lspconfig.configs')

configs.sage_lsp = {
  default_config = {
    cmd = { 'python', '-m', 'sage.lsp.cli', '--stdio' },
    filetypes = { 'sage', 'python' },
    root_dir = lspconfig.util.root_pattern('.git', 'setup.py', 'pyproject.toml'),
  },
}

lspconfig.sage_lsp.setup{}
```

#### Emacs

With `lsp-mode`:
```elisp
(add-to-list 'lsp-language-id-configuration '(sage-mode . "sage"))

(lsp-register-client
 (make-lsp-client :new-connection (lsp-stdio-connection '("python" "-m" "sage.lsp.cli" "--stdio"))
                  :major-modes '(sage-mode python-mode)
                  :server-id 'sage-lsp))
```

## Architecture

The LSP implementation consists of several key components:

### Core Modules

- **`server.py`**: Main LSP server implementation using pygls
- **`completion.py`**: Code completion provider leveraging Sage's namespace
- **`diagnostics.py`**: Syntax checking and Sage-specific linting
- **`symbols.py`**: Symbol resolution and go-to-definition functionality
- **`cli.py`**: Command-line interface for starting the server

### Integration with Sage

The LSP server integrates tightly with Sage's existing infrastructure:

- **Preparser Integration**: Uses `sage.repl.preparse` to handle Sage-specific syntax
- **Introspection**: Leverages `sage.misc.sageinspect` for symbol information
- **Namespace Access**: Accesses Sage's global namespace for completions and symbol resolution

### Language Server Features

#### Code Completion

- Global function and class completion (e.g., `Integer`, `Matrix`, `Graph`)
- Attribute completion for Sage objects (e.g., `x.factor()`, `M.eigenvalues()`)
- Context-aware suggestions based on object types

#### Diagnostics

- Python syntax error detection
- Sage-specific style suggestions:
  - Recommends `^` over `**` for exponentiation
  - Warns about integer division behavior
  - Suggests `var()` for undefined symbolic variables

#### Symbol Resolution

- Go-to-definition for Sage functions and classes
- File location resolution using Sage's introspection capabilities
- Support for both built-in and user-defined symbols

#### Hover Information

- Display documentation for Sage objects
- Show function signatures and parameter information
- Provide examples and usage hints

## Development and Testing

### Running Tests

```bash
# Run standalone tests (no full Sage environment required)
python src/sage/lsp/test_standalone.py

# Run example demonstration
python src/sage/lsp/example.py
```

### Extending the LSP

To add new LSP features:

1. Implement the feature in the appropriate provider module
2. Add message handlers in `server.py`
3. Update the server capabilities in the `initialize` method
4. Add tests and documentation

## Limitations and Future Work

### Current Limitations

- Requires `pygls` library for full functionality
- Limited semantic analysis (no full type checking)
- Basic symbol resolution (may not handle complex expressions)
- No workspace-wide symbol indexing

### Future Enhancements

- Enhanced semantic analysis with type inference
- Workspace-wide symbol search and indexing
- Code formatting and refactoring support
- Integration with Sage's documentation system
- Support for notebook-specific features
- Advanced diagnostics with Sage-specific analysis

## Contributing

When contributing to the LSP implementation:

1. Follow existing code style and patterns
2. Add comprehensive tests for new features
3. Update documentation for user-facing changes
4. Ensure lazy loading of Sage modules to avoid import issues
5. Handle cases where optional dependencies are not available

## License

This LSP implementation is part of SageMath and follows the same license terms as the main project.