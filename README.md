# Order Integration System

This system retrieves third-party orders from various sources and places them in an ERP system. It handles orders from:

- EDI via SFTP connections
- REST APIs

The project follows clean architecture principles with four main layers:

- **Domain**: Contains business entities (like Order) and business rules
- **Application**: Contains order processing services and interfaces
- **Infrastructure**: Contains implementations for SFTP, REST API, and ERP integration
- **Presentation**: Contains monitoring API endpoints

## Key Features

- Asynchronous processing for improved performance
- Support for multiple order sources with different data formats
- Dependency injection for flexible configuration
- Protocol-based interfaces for clean boundaries between layers

## Technologies

- Python 3.13
- asyncssh for fully async SFTP connections
- httpx for async REST API calls
- Dependency-injector for dependency injection
- FastAPI for monitoring API (optional)
- Pydantic for data validation

## SFTP Implementation

The project uses asyncssh for asynchronous SFTP operations, which provides:

- Native asyncio integration with async/await syntax
- Better performance for concurrent SFTP operations
- Full SSH/SFTP functionality
- Built-in connection pooling

## Project Structure

```sh
/
├── src/
│   ├── domain/
│   │   ├── entities/          # Core business entities (Order, OrderLine)
│   │   ├── repositories/      # Repository interfaces
│   │   ├── usecases/          # Business use cases
│   │   └── exceptions/        # Domain-specific exceptions
│   │
│   ├── application/
│   │   ├── interfaces/        # Defines OrderSource protocol
│   │   ├── services/          # OrderService for managing workflow
│   │   └── dtos/              # Data transfer objects
│   │
│   ├── infrastructure/
│   │   ├── persistence/       # OrderRepository implementation
│   │   ├── external/          # SFTP and REST API integrations
│   │   └── config/            # DI container and configuration
│   │
│   └── presentation/
│       ├── api/               # FastAPI monitoring endpoints
│       └── web/               # Web UI (if needed)
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
└── config/                    # Configuration files
```

## Development

### Environment Setup

1. Install uv if not already installed:

   ```sh
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Create a virtual environment and install dependencies:

   ```sh
   uv sync
   ```

   uv is a fast Python package installer and resolver written in Rust, offering significantly faster dependency resolution and installation than traditional tools.

### Configuration

The system uses environment variables for configuration:

- `ERP_API_URL`: URL of the ERP API
- `ERP_API_TOKEN`: Authentication token for ERP API
- `PARTNER1_API_URL`: URL for Partner 1's REST API
- `PARTNER1_API_TOKEN`: Authentication token for Partner 1
- `PARTNER2_SFTP_HOST`: SFTP host for Partner 2
- `PARTNER2_SFTP_PORT`: SFTP port for Partner 2
- `PARTNER2_SFTP_USER`: SFTP username for Partner 2
- `PARTNER2_SFTP_PASS`: SFTP password for Partner 2
- `PARTNER2_SFTP_PATH`: Remote path for order files
- `PARTNER2_SFTP_ARCHIVE`: Archive path for processed files

### Running the Application

To run the main order processing routine:

```sh
uv run main.py
```

To start the monitoring API:

```sh
uv run -m src.presentation.api.app
```
