# Test configuration and examples

## Running Tests

### Run all tests:
```bash
python -m pytest tests/ -v
```

### Run tests with coverage:
```bash
python -m pytest tests/ --cov=src --cov-report=term-missing
```

### Run a specific test class:
```bash
python -m pytest tests/test_api.py::TestSignupEndpoint -v
```

### Run a specific test:
```bash
python -m pytest tests/test_api.py::TestSignupEndpoint::test_signup_success -v
```

## Test Structure

The test suite covers:

1. **Root Endpoint Tests**: Testing the redirect functionality
2. **Activities Endpoint Tests**: Testing activity data retrieval
3. **Signup Endpoint Tests**: Testing user registration functionality
4. **Unregister Endpoint Tests**: Testing user unregistration functionality  
5. **Data Integrity Tests**: Testing data consistency and edge cases
6. **API Response Format Tests**: Testing response structure
7. **Workflow Integration Tests**: Testing complete user journeys

## Coverage

Current test coverage: 100% of the FastAPI application code

## Test Dependencies

- `pytest`: Testing framework
- `pytest-asyncio`: Async testing support
- `pytest-cov`: Coverage reporting
- `httpx`: HTTP client for testing FastAPI