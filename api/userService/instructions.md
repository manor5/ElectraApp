# 📁 Project Structure Instructions

This project follows a **Clean Architecture** approach with clear separation of concerns. All contributions must adhere to the existing folder structure and architectural boundaries described below.

## 🧠 Architectural Principles

- Business logic should be independent of frameworks and databases.
- External concerns (like databases, APIs, or HTTP handlers) must not pollute core logic.
- Code should be modular, testable, and easy to refactor independently across layers.

## ✅ Folder Structure Guidelines

The project is organized into the following top-level directories:

### `core/`
Contains system-wide configurations such as application settings, database setup, and security logic.

### `domain/`
Defines core business entities and abstract interfaces. This layer must not import anything from infrastructure or interfaces.

- `models/`: Plain Python classes or dataclasses representing core concepts.
- `repositories/`: Abstract classes (e.g., using `abc`) that define expected repository behavior.

### `infrastructure/`
Houses all technology-specific implementations such as database models and services.

- `db/models/`: SQLAlchemy ORM classes representing database tables.
- `db/repositories/`: Concrete implementations of domain repository interfaces.
- `services/`: External API clients or infrastructure-dependent services.

### `application/`
Contains use cases that coordinate between domain and infrastructure. This layer holds the core business rules and application workflows.

### `interfaces/`
Represents the delivery mechanism, such as HTTP endpoints and request/response schemas.

- `api/routes/`: FastAPI route definitions.
- `schemas/`: Pydantic models used for request validation and response serialization.
- `dependencies.py`: FastAPI dependency injection logic.

### `main.py`
The application entry point. Sets up the FastAPI instance and includes routers.

### `alembic/` and `alembic.ini`
Used for managing database migrations. Follow proper Alembic versioning when introducing changes to the schema.

## 🛑 Do Not

- Place business logic inside route handlers.
- Mix SQLAlchemy models with domain models.
- Import infrastructure code in domain or application layers.
- Skip schema validation for API input/output.

## ✅ Do

- Keep domain logic clean and isolated.
- Use dependency injection to connect infrastructure to use cases.
- Follow consistent naming conventions and typing.
- Write unit tests per layer when applicable.

---

Please ensure all pull requests follow this structure to maintain consistency and code quality across the project.
