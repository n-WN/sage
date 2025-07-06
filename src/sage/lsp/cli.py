#!/usr/bin/env python3
"""
SageMath Language Server CLI

Entry point for starting the SageMath Language Server Protocol server.
"""

import sys
import argparse
import logging


def main():
    """Main entry point for the SageMath LSP server."""
    parser = argparse.ArgumentParser(
        description='SageMath Language Server Protocol server'
    )
    parser.add_argument(
        '--host', 
        default='localhost', 
        help='Host to bind the server to (default: localhost)'
    )
    parser.add_argument(
        '--port', 
        type=int, 
        default=8080, 
        help='Port to bind the server to (default: 8080)'
    )
    parser.add_argument(
        '--log-level', 
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    parser.add_argument(
        '--stdio',
        action='store_true',
        help='Use stdio for communication instead of TCP'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        from sage.lsp.server import SageLSPServer, PYGLS_AVAILABLE
        
        if not PYGLS_AVAILABLE:
            logger.error("pygls is required for LSP functionality. Install it with: pip install pygls")
            sys.exit(1)
        
        server = SageLSPServer()
        
        if args.stdio:
            logger.info("Starting SageMath LSP server on stdio")
            server.start_io()
        else:
            logger.info(f"Starting SageMath LSP server on {args.host}:{args.port}")
            server.start_tcp(args.host, args.port)
    
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure SageMath is properly installed and accessible")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()