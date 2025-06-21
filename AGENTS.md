# AI Agents and Code Generation Guidelines for OpenCue

This document provides comprehensive guidelines for AI coding assistants working with the OpenCue render management system. OpenCue is a complex distributed system with multiple components written in different languages, requiring careful attention to architectural patterns and conventions.

## Project Overview

OpenCue is an open-source render management system used in visual effects and animation production. It consists of several interconnected components:

### Core Components

- **Cuebot** (Java/Spring Boot) - Central management server that distributes work and handles API requests
- **RQD** (Python) - Render Queue Daemon that runs on worker nodes and executes render tasks
- **CueGUI** (Python/PySide6) - Desktop GUI application for monitoring and managing jobs
- **CueSubmit** (Python/PySide6) - Job submission interface
- **PyCue** (Python) - Python API library for communicating with Cuebot
- **PyOutline** (Python) - Library for constructing job descriptions
- **CueWeb** (Next.js/React) - Web-based interface (newer alternative to CueGUI)
- **CueAdmin** (Python) - Command-line administration tool

### Supporting Components

- **Proto** - Protocol buffer definitions shared across components
- **REST Gateway** - RESTful API wrapper for the gRPC services

## Architecture Patterns

### Communication

- **gRPC** is the primary communication protocol between components
- **Protocol Buffers** define all data structures and service interfaces
- **Database** (PostgreSQL) stores persistent state in Cuebot

### Build System

- Each component has its own build system and package configuration
- **Rez** package management is used in production environments
- **Docker** containers for development and deployment
- **Gradle** for Java components (Cuebot)
- **Python setuptools/pip** for Python components

## Code Generation Guidelines

### 1. Language-Specific Conventions

#### Python Components (RQD, PyCue, PyOutline, CueGUI, CueSubmit, CueAdmin)

**Import Patterns:**

```python
# Correct: Use compiled proto imports for RQD
from rqd.compiled_proto import job_pb2
from rqd.compiled_proto import rqd_pb2

# Correct: Use opencue_proto imports for other Python components
import opencue_proto.job_pb2
import opencue_proto.rqd_pb2

# Correct: OpenCue API imports
import opencue
from opencue import api
```

**Error Handling:**

```python
# Correct: OpenCue-style exception handling
try:
    job = opencue.api.getJob(job_id)
except opencue.EntityNotFoundException:
    logger.warning(f"Job {job_id} not found")
    return None
except Exception:
    logger.exception(f"Failed to get job {job_id}")
    raise

# Avoid: Silent failures or generic exception catching
try:
    job = get_job(job_id)
except:
    pass  # This is problematic
```

**Logging:**

```python
# Correct: Use appropriate logger
import logging
logger = logging.getLogger(__name__)

# Or for RQD components, use loguru if configured
from loguru import logger
```

**Testing:**

```python
# Correct: Use unittest for consistency
import unittest
import mock  # or unittest.mock in Python 3

class TestMyComponent(unittest.TestCase):
    def setUp(self):
        # Setup test fixtures
        pass

    @mock.patch('module.dependency')
    def test_functionality(self, mock_dep):
        # Test implementation
        pass
```

#### Java Components (Cuebot)

**Spring Boot Patterns:**

```java
// Correct: Use dependency injection
@RestController
@RequestMapping("/api")
public class JobController {

    @Autowired
    private JobManager jobManager;

    @GetMapping("/jobs/{id}")
    public ResponseEntity<Job> getJob(@PathVariable String id) {
        // Implementation
    }
}

// Correct: Service layer pattern
@Service
@Transactional
public class JobManagerImpl implements JobManager {
    // Implementation
}
```

**Exception Handling:**

```java
// Correct: Use appropriate exception types
try {
    Job job = jobDao.getJob(jobId);
    return job;
} catch (EntityNotFoundException e) {
    logger.warn("Job {} not found", jobId);
    throw e;
} catch (DataAccessException e) {
    logger.error("Database error retrieving job {}", jobId, e);
    throw new ServiceException("Failed to retrieve job", e);
}
```

### 2. Protocol Buffer Handling

**Generation Process:**

```bash
# For RQD
python -m grpc_tools.protoc -I=. \
    --python_out=../rqd/rqd/compiled_proto \
    --grpc_python_out=../rqd/rqd/compiled_proto \
    ./*.proto

# Always run the fix script after generation
python ../ci/fix_compiled_proto.py ../rqd/rqd/compiled_proto
```

**Usage Patterns:**

```python
# Correct: Create proto messages properly
request = job_pb2.JobGetJobRequest(id=job_id)
response = stub.GetJob(request)

# Correct: Handle proto enums
if host.state == host_pb2.UP:
    # Process up host
    pass
```

### 3. Build System Integration

**RQD Build Pattern:**

```python
# In build.py - follow existing patterns for proto compilation
def build(source_path: str, build_path: str, install_path: str, targets: List[str]) -> None:
    # Compile proto files
    proto_src_path = os.path.join(os.path.dirname(source_path), "proto", "src")
    compiled_proto_path = os.path.join(source_path, "rqd", "compiled_proto")

    # Use grpc_tools.protoc for compilation
    # Run fix_compiled_proto.py for import corrections
    # Handle 2to3 conversion if needed
```

**Package Configuration:**

```python
# In package.py - follow existing patterns
name = "component_name"
version = "1.4.x"
authors = ["Open Cue"]
description = "Component description"
requires = ["python-3.11", "loguru"]  # Use consistent dependencies
tools = ["component_executable"]
build_command = "python3 {root}/build.py {install}"
```

### 4. Testing Guidelines

**Test Structure:**

```python
# Follow existing test patterns
class ComponentTests(unittest.TestCase):

    @mock.patch("component.dependency")
    def setUp(self, mock_dep):
        self.component = Component()
        self.mock_dep = mock_dep

    def test_specific_functionality(self):
        # Arrange
        expected_result = "expected"

        # Act
        result = self.component.method()

        # Assert
        self.assertEqual(expected_result, result)
```

**Test File Organization:**

```
component/
├── component/
│   ├── __init__.py
│   ├── main_module.py
│   └── sub_module.py
└── tests/
    ├── __init__.py
    ├── main_module_test.py
    └── sub_module_test.py
```

### 5. Security Considerations

**Input Validation:**

```python
# Correct: Validate all inputs
def validate_job_name(job_name: str) -> bool:
    """Validate job name with proper sanitization."""
    if not job_name or len(job_name) > 255:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_.-]+$', job_name))

# Avoid: Direct string interpolation in SQL or commands
# query = f"SELECT * FROM job WHERE name = '{job_name}"  # SQL injection risk
```

**Configuration Management:**

```python
# Correct: Use configuration files
config_dir = os.path.expanduser("~/.opencue")
config_file = os.path.join(config_dir, "config.yaml")

# Avoid: Hardcoded values
# server_host = "production-server.example.com"  # Don't hardcode
```

### 6. Documentation Standards

**Docstring Format:**

```python
def submit_job(outline: outline.Outline,
               show: str,
               shot: str = None) -> job_pb2.Job:
    """Submit a job to the OpenCue system.

    Args:
        outline: The PyOutline outline defining the job structure
        show: The show name for job organization
        shot: Optional shot name for additional categorization

    Returns:
        A protobuf Job object representing the submitted job

    Raises:
        JobSubmissionError: If job submission fails

    Example:
        >>> outline = outline.Outline('my_job')
        >>> job = submit_job(outline, 'test_show')
        >>> print(f"Submitted job {job.name}")
    """
```

**README Structure:**

```markdown
# Component Name

Brief description of the component's purpose.

## Installation

Instructions for installing the component.

## Usage

Basic usage examples.

## Development

Instructions for developers.
```

## Common Patterns to Follow

### 1. Frame Processing in RQD

```python
# Follow the FrameAttendantThread pattern
class FrameAttendantThread(threading.Thread):
    def __init__(self, rqCore, runFrame, frameInfo):
        threading.Thread.__init__(self)
        self.rqCore = rqCore
        self.runFrame = runFrame
        self.frameInfo = frameInfo

    def run(self):
        # Follow existing patterns for process management
        # Handle platform differences (Linux/Windows/Darwin)
        # Proper logging and error handling
        pass
```

### 2. gRPC Service Implementation

```python
# Follow existing servicer patterns
class MyServicer(my_service_pb2_grpc.MyServiceServicer):
    """Servicer implementation following OpenCue conventions."""

    def GetEntity(self, request, context):
        """Get entity with proper error handling."""
        try:
            return self._get_entity_impl(request)
        except Exception as e:
            logger.exception("Failed to get entity")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return response_pb2.EntityResponse()
```

### 3. Database Access (Cuebot)

```java
// Follow DAO patterns
@Repository
public class JobDaoImpl implements JobDao {

    @Override
    @Transactional(readOnly = true)
    public Job getJob(String jobId) {
        // Use proper SQL and parameter binding
        // Handle exceptions appropriately
    }
}
```

## Testing Requirements

### Unit Tests

- All new code must include comprehensive unit tests
- Use mock objects for external dependencies
- Follow existing test patterns and naming conventions
- Achieve reasonable code coverage

### Integration Tests

- Test gRPC communication between components
- Test database interactions in Cuebot
- Test proto message serialization/deserialization

### End-to-End Tests

- Test complete job submission and execution workflows
- Test GUI interactions where applicable
- Test error scenarios and recovery

## Build and Deployment

### Local Development

```bash
# Build RQD component
cd rqd
python build.py build

# Run tests
python -m pytest tests/

# Install for development
pip install -e .
```

### Docker Development

```bash
# Build component container
docker build -t opencue-component .

# Run with dependencies
docker-compose up
```

## CI/CD Integration

When generating code for CI/CD:

1. **Use existing GitHub Actions patterns**
2. **Run all tests before merging**
3. **Check code style with linters**
4. **Validate proto compilation**
5. **Test Docker builds**

## Performance Considerations

### RQD Performance

- Minimize frame startup overhead
- Efficient process monitoring
- Proper resource cleanup

### Cuebot Performance

- Database query optimization
- Connection pooling
- Caching strategies

### Network Efficiency

- Batch gRPC calls where possible
- Implement proper timeouts
- Handle network failures gracefully

## Troubleshooting Common Issues

### Proto Import Issues

```python
# If you see import errors, check:
# 1. Proto files are compiled correctly
# 2. fix_compiled_proto.py was run
# 3. PYTHONPATH includes compiled_proto directory
```

### Build System Issues

```bash
# Common fixes:
# 1. Clean build directories
# 2. Reinstall dependencies
# 3. Check environment variables (REZ_BUILD_*)
```

### gRPC Connection Issues

```python
# Check configuration
cuebot_hosts = os.environ.get('CUEBOT_HOSTS', 'localhost')
# Verify network connectivity
# Check firewall settings
```

## Code Review Guidelines

### For Reviewers

1. **Verify architectural consistency** with existing patterns
2. **Check error handling** and logging
3. **Validate test coverage** and quality
4. **Review security implications**
5. **Ensure documentation** is updated

### For AI-Generated Code

1. **Always include tests** for generated functionality
2. **Follow existing code style** and conventions
3. **Document any deviations** from standard patterns
4. **Test integration** with existing components
5. **Validate security** and performance implications

## Resources

- [OpenCue Documentation](https://www.opencue.io/docs/)
- [Contributing Guidelines](https://www.opencue.io/contributing/)
- [Architecture Overview](https://www.opencue.io/docs/concepts/)
- [API Reference](https://www.opencue.io/contributing/opencue/build-docs/)
- [TSC Meeting Notes](tsc/meetings/) for recent development discussions

## Getting Help

1. **Check existing code** for similar patterns
2. **Review test files** for usage examples
3. **Consult documentation** and API references
4. **Ask on the OpenCue Google Group** for design questions
5. **Create draft PRs** for early feedback from maintainers

---

Remember: AI is a powerful tool for accelerating OpenCue development, but human judgment, code review, and testing remain essential for maintaining the quality and reliability that production render farms require.
