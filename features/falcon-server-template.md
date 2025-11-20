# Feature: Falcon Server Template

## Summary

Create a new templates directory structure that houses self-contained, testable, runnable applications. The first template will be a generic Falcon web server with a modular features system for configuring and extending capabilities. Each template in the templates directory should be an independent application that leverages the utility classes and functions from the main utils package.

This establishes a pattern for creating reusable application templates that demonstrate best practices while providing production-ready starting points for common server types.

## Acceptance Criteria

- [ ] templates directory exists at project root with clear organization
- [ ] templates/falcon directory contains a complete, runnable Falcon server application
- [ ] Falcon server has a features directory for modular capability configuration
- [ ] Falcon server can be run standalone with minimal configuration
- [ ] Falcon server has its own test suite that passes
- [ ] Falcon server uses utility classes from the main utils package (String, Logger, Session, Dict, Path, etc.)
- [ ] Template includes README with setup and usage instructions
- [ ] Template includes requirements/dependencies specification
- [ ] Template can be copied out and run independently of the parent project

## Scope/Non-Goals

### In Scope
- Create templates directory structure at project root
- Build generic Falcon server base implementation
- Implement features directory pattern for modular capabilities
- Include basic server configuration (port, host, logging)
- Demonstrate integration with utils package (Logger, Session, String, Dict, Path)
- Provide minimal working example with health check endpoint
- Add comprehensive README for the template
- Create test suite for the Falcon server template
- Set up proper dependency management for the template

### Non-Goals
- Implementing specific features for the Falcon server (will be separate follow-up work)
- Creating multiple templates in this phase (only Falcon server)
- Database integration (can be added as a feature later)
- Authentication/authorization (can be added as a feature later)
- Deployment configuration (Docker, Kubernetes, etc.)
- Front-end or UI components
- Complete production hardening (focus on solid foundation)

## Files to Modify

### New Files to Create

- **templates/README.md**: Overview of the templates directory structure, how to use templates, and guidelines for creating new templates

- **templates/falcon/README.md**: Complete documentation for the Falcon server template including setup instructions, usage examples, feature system explanation, and how to extend with new features

- **templates/falcon/pyproject.toml**: Python project configuration with dependencies (falcon, plus imports from parent utils package)

- **templates/falcon/app.py**: Main application entry point that initializes the Falcon server, loads features, and starts the server

- **templates/falcon/server.py**: Core Falcon server class that handles application setup, middleware configuration, and feature registration

- **templates/falcon/config.py**: Configuration management using environment variables and defaults, leveraging Dict utility for config handling

- **templates/falcon/features/__init__.py**: Features package initialization that auto-discovers and registers available features

- **templates/falcon/features/base.py**: Base feature class that defines the interface all features must implement (routes, middleware, setup, teardown)

- **templates/falcon/features/health.py**: Example feature that adds health check endpoint demonstrating the feature pattern

- **templates/falcon/tests/__init__.py**: Test package initialization

- **templates/falcon/tests/test_server.py**: Tests for core server functionality

- **templates/falcon/tests/test_features.py**: Tests for feature loading and registration system

- **templates/falcon/tests/test_health.py**: Tests for the health check feature

### Existing Files to Modify

- **pyproject.toml**: Update the hatch.build exclude section to exclude templates directory from the main utils package build

- **README.md**: Add a new section documenting the templates directory and linking to template-specific documentation

## Design/Approach

### Key Design Decisions

**Templates as Independent Applications**: Each template directory should be a complete, self-contained application that can be copied out and used independently. This means each template has its own pyproject.toml, tests, and documentation. The templates import from the parent utils package during development but could be modified to install utils as a dependency if deployed separately.

**Feature-Based Architecture**: The Falcon server uses a plugin-like features system where each feature is a self-contained module that can register routes, add middleware, and configure server behavior. Features inherit from a base class and are auto-discovered at startup. This allows the server to remain generic while being easily extensible.

**Leverage Utils Package**: The template should demonstrate practical usage of the utils package utilities. Use Logger for structured logging, Session for HTTP clients, String for text processing, Dict for config manipulation, Path for file operations, etc. This serves both as documentation by example and ensures the template benefits from the utility functions.

**Configuration via Environment**: Use environment variables for configuration with sensible defaults. Config class uses Dict utility methods for handling nested configuration and type conversions.

**Test-Driven Design**: Each template includes comprehensive tests. The Falcon template should have tests for server initialization, feature loading, route registration, and individual features.

### Architecture Impact

This introduces a new top-level templates directory that sits alongside utils. The templates import from utils but are otherwise independent. This doesn't affect the core utils package structure or functionality.

The build system needs minor updates to exclude templates from the utils package distribution.

### Data Flow

**Server Startup Flow**:
1. app.py loads configuration from environment/defaults
2. Server instance is created with config
3. Features directory is scanned for feature modules
4. Each feature is instantiated and registered
5. Features can add routes, middleware, hooks
6. Falcon application is configured with all registered components
7. Server starts listening on configured host/port

**Request Flow**:
1. Request comes into Falcon
2. Middleware chain processes request (features can add middleware)
3. Route handler is invoked (provided by feature)
4. Handler uses utils (Logger for logging, Session for external calls, etc.)
5. Response is returned through middleware chain

## Tests to Add/Update

### Unit Tests
- Server initialization with various config options
- Feature discovery and loading mechanism
- Feature registration (routes, middleware)
- Config loading from environment variables
- Config defaults and overrides

### Integration Tests
- Full server startup and shutdown
- Health check endpoint returns correct response
- Multiple features can be loaded simultaneously
- Features can access shared server resources
- Logger integration captures structured logs
- Request/response cycle through full middleware stack

### Manual Testing
- Run server locally and verify health endpoint responds
- Test with different environment variable configurations
- Verify structured logs appear correctly
- Add a new feature and confirm it loads automatically
- Copy template to new location and verify independence

## Risks & Rollback

### Risks

**Risk 1: Import complexity between templates and utils**
- Mitigation: Use relative imports carefully and document the import pattern clearly. Consider making utils installable via pip for true independence

**Risk 2: Templates directory might confuse package structure**
- Mitigation: Clear documentation in both root README and templates README explaining the relationship. Proper build configuration to exclude templates from utils package

**Risk 3: Feature auto-discovery could be fragile**
- Mitigation: Keep feature discovery logic simple and explicit. Use clear naming conventions and provide good error messages when features fail to load

**Risk 4: Dependency version conflicts between template and parent utils**
- Mitigation: Templates should specify compatible version ranges for dependencies. Document dependency management strategy

### Rollback Plan

Since this is entirely new functionality with no modifications to existing utils code (except minor documentation and build config updates), rollback is straightforward:
- Delete templates directory
- Revert changes to root README.md
- Revert changes to pyproject.toml build exclusions

No risk to existing utils package functionality.

## Evidence

**During Development**:
- templates/falcon/README.md - discovered relevant patterns in Session, Logger usage
- utils/session/session.py - examined for HTTP client patterns to demonstrate in API features
- utils/logger.py - reviewed for structured logging integration
- tests/test_session.py - reviewed for testing patterns applicable to server tests

## Assumptions

**Python Version**: Templates will target the same Python version as the utils package (3.11+)

**Development Environment**: Assumes users have the parent utils package available for import during template development and testing

**Falcon Framework**: Assumes Falcon 3.x or later with modern Python support and async capabilities

**Testing Framework**: Will use pytest consistent with the main utils package testing approach

**Feature Discovery**: Features will be Python modules in the features directory that define a Feature class inheriting from BaseFeature

**Configuration**: Environment variables follow uppercase naming convention (e.g., FALCON_HOST, FALCON_PORT)

## Open Questions

- [ ] Should templates have their own virtual environments or share with parent project during development?
- [ ] Should we provide a template CLI for common operations (create new feature, run server, run tests)?
- [ ] What level of WSGI server should be included (just development server, or production-ready like gunicorn/uvicorn)?
- [ ] Should feature dependencies be declared separately or in the main template requirements?
- [ ] Should we include example features beyond health check in the initial implementation?

## Tasks

1. [x] Create templates directory structure at project root with README explaining the templates concept
2. [x] Create templates/falcon directory with basic structure (src, tests, docs)
3. [x] Set up templates/falcon/pyproject.toml with Falcon and necessary dependencies
4. [x] Implement templates/falcon/config.py for environment-based configuration using Dict utilities
5. [x] Create templates/falcon/features/base.py defining the BaseFeature interface
6. [x] Implement templates/falcon/features/__init__.py with auto-discovery logic
7. [x] Create templates/falcon/features/health.py as example feature with health check endpoint
8. [x] Implement templates/falcon/server.py for core Falcon application setup and feature registration
9. [x] Create templates/falcon/app.py as main entry point that ties everything together
10. [x] Write comprehensive tests in templates/falcon/tests for server, features, and health check
11. [x] Create detailed templates/falcon/README.md with setup, usage, and extension instructions
12. [x] Update root pyproject.toml to exclude templates from utils package build
13. [x] Update root README.md with templates section and link to template documentation
14. [x] Manual verification that server runs standalone and health endpoint works
15. [x] Manual verification that a new feature can be added by creating a new module in features directory

---

**Implementation Completed**: 2025-11-17

All tasks have been successfully completed. The Falcon server template is fully functional with:
- Working health check endpoint at `/health`
- Feature auto-discovery and registration
- Demo feature successfully added and tested at `/demo`
- Integration with utils package (Logger, String, Dict, Datetime, etc.)

**Notes**: This plan establishes the foundation for a templates system. Once the Falcon server template is complete, we can add individual features (database integration, authentication, rate limiting, etc.) as separate follow-up work. Each feature will be a new module in the features directory following the established pattern.
