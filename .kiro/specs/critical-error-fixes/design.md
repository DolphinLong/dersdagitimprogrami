# Design Document

## Overview

This design addresses critical errors by implementing a systematic restoration and configuration strategy. The approach prioritizes git-based file restoration, environment configuration, and dependency management to restore project functionality with minimal code changes.

## Architecture

### Restoration Strategy

1. **Git-Based Recovery**: Use `git restore` for deleted files that exist in git history
2. **Configuration Generation**: Create missing .env files with secure defaults
3. **Dependency Pinning**: Update requirements.txt with explicit versions
4. **Fallback Mechanisms**: Add SQLite fallback for PostgreSQL
5. **Test Alignment**: Update frontend tests to match actual component content

### Component Hierarchy

```
Project Root
├── backend/
│   ├── .env (CREATE)
│   ├── .env.example (CREATE)
│   ├── requirements.txt (UPDATE)
│   └── ders_dagitim/settings.py (UPDATE - add fallback)
├── frontend/
│   ├── package.json (UPDATE - versions)
│   ├── .eslintrc.json (CREATE)
│   ├── .prettierrc (CREATE)
│   └── src/App.test.tsx (UPDATE)
├── database/ (RESTORE from git)
├── algorithms/ (RESTORE from git)
├── reports/ (RESTORE from git)
├── ui/ (RESTORE from git)
└── utils/ (RESTORE from git)
```

## Components and Interfaces

### 1. Git Restoration Module

**Purpose**: Restore deleted files from git history

**Operations**:
- Check git status for deleted files
- Restore specific paths using `git restore`
- Verify restoration success

**Files to Restore**:
- `database/__init__.py`, `database/db_manager.py`, `database/models.py`
- `algorithms/__init__.py`, `algorithms/scheduler.py`, `algorithms/simple_perfect_scheduler.py`, etc.
- `reports/__init__.py` and all report generators
- `ui/__init__.py` and all UI dialogs
- `utils/__init__.py` and all utility modules

### 2. Environment Configuration Module

**Purpose**: Create secure .env files

**Template Structure**:
```python
SECRET_KEY = generate_secret_key()  # 50+ chars, cryptographically random
DEBUG = True (dev) / False (prod)
DB_NAME = ders_dagitim_db
DB_USER = postgres
DB_PASSWORD = (user-provided)
DB_HOST = localhost
DB_PORT = 5432
CORS_ALLOWED_ORIGINS = http://localhost:3000 (dev) / env-based (prod)
```

**Files**:
- `backend/.env` - Actual configuration (gitignored)
- `backend/.env.example` - Template with placeholders

### 3. Database Fallback Module

**Purpose**: Handle PostgreSQL unavailability gracefully

**Implementation**:
```python
# In settings.py
try:
    # Try PostgreSQL first
    DATABASES = {'default': {...postgresql config...}}
    # Test connection
    connection.ensure_connection()
except Exception:
    # Fallback to SQLite
    DATABASES = {'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }}
    logger.warning("PostgreSQL unavailable, using SQLite fallback")
```

### 4. Dependency Version Manager

**Purpose**: Pin all package versions

**Updated requirements.txt**:
```
Django==5.2.5
djangorestframework==3.15.2
django-cors-headers==4.4.0
python-decouple==3.8
numpy==1.26.4
psycopg2-binary==2.9.9
```

**Updated package.json**:
```json
{
  "typescript": "^5.3.3",
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "@types/react": "^18.2.0",
  "@types/react-dom": "^18.2.0"
}
```

### 5. Frontend Test Alignment Module

**Purpose**: Fix failing App.test.tsx

**Strategy**:
1. Read actual App.tsx content
2. Update test assertions to match real content
3. Use data-testid attributes for stable selectors

### 6. Code Quality Configuration

**Purpose**: Add ESLint and Prettier

**ESLint Config** (`.eslintrc.json`):
```json
{
  "extends": ["react-app", "react-app/jest"],
  "rules": {
    "no-unused-vars": "warn",
    "@typescript-eslint/no-unused-vars": "warn"
  }
}
```

**Prettier Config** (`.prettierrc`):
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2
}
```

## Data Models

### Environment Configuration Model

```typescript
interface EnvConfig {
  SECRET_KEY: string;        // Min 50 chars
  DEBUG: boolean;
  DB_NAME: string;
  DB_USER: string;
  DB_PASSWORD: string;
  DB_HOST: string;
  DB_PORT: number;
  CORS_ALLOWED_ORIGINS: string[];
}
```

### Git Restoration Status

```typescript
interface RestorationStatus {
  path: string;
  status: 'pending' | 'restored' | 'failed';
  error?: string;
}
```

## Error Handling

### Git Restoration Errors

- **File not in history**: Log warning, skip file
- **Merge conflicts**: Abort restore, notify user
- **Permission errors**: Check file permissions, suggest sudo if needed

### Environment Configuration Errors

- **Missing SECRET_KEY**: Generate new one automatically
- **Invalid DB credentials**: Provide clear error message with .env.example reference
- **CORS misconfiguration**: Default to localhost in dev, fail in prod

### Database Connection Errors

- **PostgreSQL unavailable**: Automatic fallback to SQLite with warning
- **SQLite creation fails**: Check disk space and permissions
- **Migration errors**: Provide rollback instructions

### Dependency Installation Errors

- **Version conflicts**: Use pip's dependency resolver
- **Missing system libraries**: Provide installation instructions (e.g., PostgreSQL dev headers)
- **Network errors**: Suggest offline installation or mirror usage

## Testing Strategy

### Unit Tests

- Test SECRET_KEY generation (length, randomness)
- Test database fallback logic
- Test .env parsing and validation

### Integration Tests

- Test full git restoration workflow
- Test Django startup with new .env
- Test database connection with fallback
- Test frontend build with updated dependencies

### Validation Tests

- Verify all deleted files are restored
- Verify no ModuleNotFoundError on imports
- Verify Django starts without UndefinedValueError
- Verify frontend tests pass
- Verify git status is clean after restoration

### Manual Testing Checklist

1. Run `git status` - should show restored files
2. Run `python backend/manage.py check` - should pass
3. Run `python backend/manage.py migrate` - should succeed
4. Run `cd frontend && npm test` - should pass
5. Run `cd frontend && npm run build` - should succeed
6. Start backend server - should start without errors
7. Start frontend dev server - should start without errors

## Implementation Phases

### Phase 1: Git Restoration (Priority: Critical)
- Restore database/, algorithms/, reports/, ui/, utils/
- Verify imports work

### Phase 2: Environment Configuration (Priority: Critical)
- Create .env and .env.example
- Update .gitignore
- Generate secure SECRET_KEY

### Phase 3: Dependency Management (Priority: High)
- Pin versions in requirements.txt
- Update package.json versions
- Test installations

### Phase 4: Database Fallback (Priority: High)
- Add SQLite fallback logic to settings.py
- Test both PostgreSQL and SQLite paths

### Phase 5: Frontend Fixes (Priority: Medium)
- Fix App.test.tsx
- Add ESLint/Prettier configs
- Update TypeScript/React versions

### Phase 6: Git Cleanup (Priority: Low)
- Commit all changes
- Clean working directory

## Security Considerations

- SECRET_KEY must be cryptographically random (use `secrets` module)
- .env must be in .gitignore
- Production deployments must validate SECRET_KEY is not default
- Database passwords should not be logged
- CORS origins must be restricted in production

## Performance Considerations

- Git restore operations are fast (< 1 second per module)
- SQLite fallback has minimal performance impact for development
- Dependency installation time depends on network (2-5 minutes)

## Rollback Strategy

If restoration fails:
1. Run `git reset --hard HEAD` to undo all changes
2. Manually review git log to find last good commit
3. Create backup branch before attempting fixes
4. Use `git stash` to save any manual changes
