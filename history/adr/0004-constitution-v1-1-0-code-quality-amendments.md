# ADR-0004: Constitution v1.1.0 - Code Quality & Engineering Standards Amendments

**Status:** Accepted
**Date:** 2026-01-10
**Feature:** Constitution v1.1.0
**Decision Makers:** User + AI Gap Analysis (Context7 MCP Validation)
**Supersedes:** Constitution v1.0.0

---

## Context

The Engineering Constitution v1.0.0 (ratified 2025-01-02) provided strong governance for Spec-Driven Development, Test-Driven Development, architectural boundaries, and security. However, a comprehensive gap analysis validated against authoritative best practices (Context7 MCP) identified **4 critical gaps** that would hinder Phase II+ development:

1. **Code Quality & AI-Readability (CRITICAL)** - No PEP 8 compliance, type hints, docstrings, or complexity limits
2. **Test Organization (HIGH)** - No test isolation requirements, fixture patterns, or parametrization standards
3. **Performance Standards (MODERATE)** - No async/await patterns, N+1 query prevention, or resource cleanup guarantees
4. **Error Handling (MODERATE)** - No error taxonomy, propagation patterns, or dependency inversion guidance

**Validation Authority:**
- Python 3.15 official documentation (`/websites/python_3_15`) - Type hints (PEP 484, 591, 655), exhaustive checking
- pytest framework (`/pytest-dev/pytest`) - Fixture system, parametrization, test isolation best practices
- Clean Code principles (`/ryanmcdermott/clean-code-javascript`) - Naming conventions, async patterns, comment philosophy

**Impact:** Without these standards, Phase II (Web Application) and beyond would accumulate technical debt, produce unmaintainable code, and lack performance awareness critical for production deployments.

---

## Decision

**Amend the Constitution from v1.0.0 to v1.1.0 (MINOR version - additive, non-breaking changes) by adding 4 addendums:**

### ADDENDUM I: Principle VII - Code Quality & AI-Readability Standards

**Scope:** Establish mandatory code quality standards for AI-generated code maintainability.

**Standards Defined:**
- **PEP 8 Compliance**: Line length 88, indentation 4 spaces, import order (stdlib → third-party → local), naming conventions
- **Type Hints (Mandatory)**: All public functions/methods MUST have type hints; mypy strict mode; coverage targets (100% domain, 95% application, 90% infrastructure)
- **Docstring Standards**: Google style, mandatory for modules/classes/public functions; explain **why** not **what**
- **Code Complexity Limits**: Cyclomatic complexity ≤ 10, function length ≤ 50 lines, no magic numbers
- **Enforcement**: Black + ruff + mypy strict mode pre-commit hooks; Spec Governance Enforcer blocks non-compliant PRs

**Rationale:** AI-generated code must be readable by future AI agents and developers. Consistent style, explicit types, and clear documentation enable long-term maintainability across all 5 phases.

---

### ADDENDUM II: Extend Principle III - Test Organization & Best Practices

**Scope:** Add detailed test organization guidance to the existing TDD mandate.

**Standards Defined:**
- **Directory Structure**: `tests/unit`, `tests/integration`, `tests/e2e`; `conftest.py` for shared fixtures
- **Test Isolation (CRITICAL)**: No shared state, tests runnable in any order, fixture-based setup/teardown, database rollback
- **Fixture Management**: `yield` patterns for cleanup, scope documentation (function/class/module/session), parameterized fixtures
- **Parametrization Standards**: `@pytest.mark.parametrize` for input variations, boundary conditions, error cases
- **Test Markers**: `@pytest.mark.unit/integration/e2e/slow` for selective execution (fast CI feedback loops)
- **Enforcement**: Test Strategy Architect blocks PRs with flaky tests (fail in random order) or duplicate test logic

**Rationale:** Organized, isolated tests prevent test pollution and scale across all 5 phases. Fixture patterns and parametrization reduce duplication. Markers enable running unit tests in seconds, full suite in minutes.

---

### ADDENDUM III: Principle VIII - Performance Standards & Efficiency

**Scope:** Establish phase-appropriate performance expectations and async patterns for Phase II+.

**Standards Defined:**
- **Phase-Appropriate Expectations**: Phase I (< 100ms CRUD), Phase II (p95 < 500ms reads, < 1s writes), Phase V (100 req/s sustained, 500 req/s peak)
- **Async/Await Patterns (Phase II+ Mandatory)**: Async for I/O (database, HTTP, files), sync for pure computation; FastAPI async endpoints + async database queries
- **N+1 Query Prevention**: Eager loading (SQLAlchemy `selectinload`), batch queries, avoid loops over related data
- **Resource Cleanup Guarantees**: Context managers (`with`, `async with`), FastAPI dependency injection `yield` patterns
- **Performance Testing**: Phase II smoke tests (1-10 req/s), Phase IV load tests (100 req/s), Phase V stress tests (500 req/s peak)
- **Enforcement**: Integration Orchestrator runs load tests before Phase IV/V deployments; >20% slower blocks deployment

**Rationale:** Performance awareness prevents technical debt. Async patterns leverage FastAPI's concurrency model. N+1 prevention avoids database bottlenecks. Resource cleanup prevents leaks degrading system stability.

---

### ADDENDUM IV: Extend Principle IV - Dependency Inversion & Error Handling

**Scope:** Add error taxonomy and propagation patterns to the existing separation of concerns principle.

**Standards Defined:**
- **Dependency Inversion Principle**: Domain defines repository interfaces (Protocol), infrastructure implements; high-level modules depend on abstractions, not implementations
- **Interface Segregation**: Focused interfaces (single responsibility), CQRS read/write split patterns (Phase V+)
- **Error Taxonomy**: `DomainError` (business rule violations), `ApplicationError` (use case failures), `InfrastructureError` (database/network failures)
- **Error Propagation Patterns**: Domain raises `DomainError` → Application wraps in `ApplicationError` → API maps to HTTP status codes (400/401/403/404/500)
- **Error Logging**: INFO (domain errors), WARNING (application errors), ERROR (infrastructure errors), CRITICAL (unhandled exceptions)
- **Enforcement**: Error & Reliability Architect defines taxonomy; Backend Architect implements propagation; Integration Orchestrator validates in tests

**Rationale:** Dependency Inversion enables infrastructure swapping (in-memory → PostgreSQL → distributed cache). Error propagation ensures consistent handling across layers. Clear boundaries prevent business logic leaking into API responses.

---

## Alternatives Considered

### Alternative 1: Keep Constitution v1.0.0 Unchanged

**Pros:**
- No immediate effort required
- Sufficient for Phase I (console app)

**Cons:**
- ❌ **REJECTED**: Code quality gaps compound in Phase II (FastAPI async patterns undefined, no type hints)
- ❌ Test organization gaps cause flaky tests and maintenance nightmares
- ❌ Performance gaps prevent scaling (no async patterns, resource leaks)
- ❌ Error handling gaps lead to inconsistent error messages and debugging difficulties

**Verdict:** Not viable for Phase II+ development.

---

### Alternative 2: Wait Until Phase II to Add Standards

**Pros:**
- Delay effort until needed

**Cons:**
- ❌ **REJECTED**: Phase I code would need retroactive compliance before Phase II
- ❌ Harder to enforce standards on existing code than to start correctly
- ❌ Technical debt accumulates from the beginning

**Verdict:** Proactive governance prevents rework.

---

### Alternative 3: Add All 4 Addendums Now (SELECTED)

**Pros:**
- ✅ Prevents technical debt from Phase I onward
- ✅ Establishes clear quality expectations for AI-generated code
- ✅ All standards validated against authoritative sources (Context7 MCP)
- ✅ MINOR version (additive, non-breaking) allows gradual compliance

**Cons:**
- Requires immediate effort to implement standards

**Verdict:** **Selected**. Upfront investment in code quality standards prevents exponential rework later. AI-generated code benefits most from clear, explicit rules.

---

## Consequences

### Positive

1. **Code Quality Assurance**: AI agents generate consistent, readable, maintainable code across all 5 phases
2. **Type Safety**: 100% type hint coverage in domain layer prevents runtime errors caught by static analysis
3. **Test Reliability**: Organized, isolated tests scale without flakiness; fast feedback loops (unit tests in seconds)
4. **Performance Awareness**: Phase II+ async patterns prevent blocking event loops; N+1 prevention avoids database bottlenecks
5. **Error Handling Consistency**: Clear error boundaries prevent business logic leaking into API responses
6. **Future-Proof**: Standards apply to all 5 phases (Console → Web → AI → Kubernetes → Cloud-Native)

### Negative

1. **Immediate Compliance Effort**: Phase I code must comply with new standards (pre-commit hooks, mypy strict mode, docstrings)
2. **Learning Curve**: AI agents and developers must learn pytest fixtures, async patterns, error propagation
3. **Enforcement Overhead**: Spec Governance Enforcer blocks non-compliant PRs (slower initial velocity)

### Mitigation

- Gradual enforcement: Pre-commit hooks warn first, then block after grace period
- Documentation: Context7 MCP references provide authoritative guidance
- Template updates: `.specify/templates/` updated with new standards for future features

---

## Compliance & Enforcement

### Agent Responsibilities

**Spec Governance Enforcer:**
- Blocks PRs failing pre-commit checks (Black, ruff, mypy strict mode)
- Validates docstring presence for public APIs

**Test Strategy Architect:**
- Reviews tests for isolation (no shared state, any-order execution)
- Blocks PRs with tests failing random order (`pytest --random-order`)
- Validates test markers (unit/integration/e2e/slow)

**Error & Reliability Architect:**
- Defines error taxonomy (DomainError, ApplicationError, InfrastructureError)
- Advises on error propagation patterns and logging levels

**Backend Architect:**
- Implements async/await patterns (Phase II+ FastAPI async endpoints)
- Implements error propagation (domain → application → API)
- Prevents N+1 queries (eager loading via `selectinload`)

**Integration Orchestrator:**
- Validates error handling in integration tests
- Runs performance tests before Phase IV/V deployments
- Blocks deployment if performance regresses >20%

### Pre-Commit Hooks (Required)

```bash
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black
        args: [--line-length=88]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    hooks:
      - id: mypy
        args: [--strict, --ignore-missing-imports]
```

---

## Review & Approval

**Gap Analysis:** Conducted 2026-01-10 using Context7 MCP validation
**Proposed By:** AI Agent (Independent Constitution Review Agent)
**Validated By:** Python 3.15 docs, pytest docs, Clean Code principles
**Approved By:** User (explicit consent: "add the improvements")
**Effective Date:** 2026-01-10

---

## Impact on Existing Specs

**Phase I (Current):**
- ✅ Sufficient for console app with in-memory storage
- ⚠️ Must comply with new code quality standards (type hints, docstrings, PEP 8)
- ⚠️ Must organize tests (unit/integration, fixtures, markers)

**Phase II+ (Future):**
- ✅ New standards directly address Phase II requirements (async patterns, error handling)
- ✅ Performance standards prevent production scaling issues
- ✅ Test organization scales to API contract tests, E2E flows

**Follow-up Actions:**
- Update `.specify/templates/plan-template.md` with performance expectations section
- Update `.specify/templates/tasks-template.md` with test organization validation checklist
- Add code quality pre-commit hooks (Black, ruff, mypy strict mode)
- Update backend CLAUDE.md (Phase II+) with async patterns and error handling guidance

---

## References

- **Constitution v1.0.0**: `.specify/memory/constitution.md` (ratified 2025-01-02, 942 lines)
- **Constitution v1.1.0**: `.specify/memory/constitution.md` (amended 2026-01-10, 1,632 lines)
- **Gap Analysis Report**: `C:\Users\USER-PC\.claude\plans\magical-wishing-wave.md`
- **Context7 MCP - Python 3.15**: `/websites/python_3_15`
- **Context7 MCP - pytest**: `/pytest-dev/pytest`
- **Context7 MCP - Clean Code**: `/ryanmcdermott/clean-code-javascript`
- **PEP 8 Style Guide**: https://peps.python.org/pep-0008/
- **FastAPI Async Patterns**: https://fastapi.tiangolo.com/async/
- **SQLAlchemy Async**: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

---

**Rationale Summary:** Constitution v1.1.0 strengthens the engineering foundation for Phase II+ by establishing code quality standards, test organization best practices, performance awareness, and error handling patterns. All amendments validated against authoritative sources ensure AI-generated code remains maintainable, reliable, and scalable across all 5 phases of the Evolution of Todo project.
