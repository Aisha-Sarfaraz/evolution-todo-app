# Feature Specification: Full-Stack Web Application

**Feature Branch**: `001-fullstack-todo-web`
**Created**: 2026-01-11
**Status**: Draft
**Input**: User description: "Transform Phase I in-memory Python console Todo app into modern multi-user web application with persistent storage, secure authentication, clear frontend/backend separation, and RESTful API design. Includes Basic Level features (Add, Delete, Update, View, Mark Complete) and Intermediate Level features (Priorities with 4 levels Low/Medium/High/Urgent, Categories predefined + Tags user-created, Search title + description, Filter by status/priority/tags/categories/date range, Sort by priority/title alphabetically)"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Registration & Authentication (Priority: P1)

New users must be able to create accounts securely, verify their email addresses, sign in to access their tasks, reset forgotten passwords, and manage their profile information including display name and password updates.

**Why this priority**: Foundation for all other features - without authentication, no multi-user system exists. Blocking dependency for task isolation and security (P2, P3).

**Independent Test**: Complete registration flow → receive verification email → click verification link → sign in with credentials → access protected dashboard → navigate to profile → update display name → sign out → reset password via email → sign in with new password.

**Acceptance Scenarios**:

1. **Signup Flow - Valid Registration**
   - **Given** user is on application homepage, **When** user navigates to signup page and enters valid email "user@example.com" and strong password (10 chars with special characters), **Then** system creates account, sends verification email, redirects user to "Please verify your email" page with instructions

2. **Signup Flow - Duplicate Email**
   - **Given** user attempts to register with email "existing@example.com" that already exists in system, **Then** system returns error message "Email already registered. Please sign in or reset password."

3. **Signup Flow - Weak Password**
   - **Given** user enters password "pass123" (less than 8 characters, no special character), **Then** system shows inline validation error "Password must be at least 8 characters with at least 1 special character (!@#$%^&*)"

4. **Signup Flow - Password Mismatch**
   - **Given** user enters password "SecurePass123!" and confirmation "SecurePass456!", **Then** system shows error "Passwords do not match"

5. **Email Verification - Successful Verification**
   - **Given** user signed up and received verification email, **When** user clicks verification link within 24 hours, **Then** system marks email as verified, displays success message "Email verified! You can now sign in.", redirects to signin page

6. **Email Verification - Expired Link**
   - **Given** user clicks verification link after 24 hours, **Then** system shows error "Verification link expired. Please request a new verification email." with "Resend Verification" button

7. **Email Verification - Already Verified**
   - **Given** user clicks verification link for already-verified email, **Then** system shows message "Email already verified. Please sign in."

8. **Signin Flow - Successful Signin**
   - **Given** verified user on signin page, **When** user enters correct email and password, **Then** system issues JWT access token (1-hour expiration) and refresh token (7-day expiration), redirects user to dashboard showing their task list

9. **Signin Flow - Incorrect Password**
   - **Given** user enters correct email but wrong password, **Then** system returns generic error "Invalid email or password" (does not reveal which field is wrong for security)

10. **Signin Flow - Unverified Email**
    - **Given** user with unverified email attempts to sign in, **Then** system redirects to verification page with message "Please verify your email first. Check your inbox or resend verification."

11. **Password Reset - Request Reset**
    - **Given** user on signin page clicks "Forgot password?", **When** user enters registered email, **Then** system sends password reset email with reset link (1-hour expiration), displays "Password reset email sent. Check your inbox."

12. **Password Reset - Complete Reset**
    - **Given** user clicks reset link in email, **When** user enters new password "NewSecure456!" and confirms, **Then** system updates password hash, invalidates all existing tokens, displays "Password updated successfully. Please sign in with your new password.", redirects to signin page

13. **Password Reset - Expired Link**
    - **Given** user clicks reset link after 1 hour, **Then** system shows error "Reset link expired. Please request a new password reset." with "Resend Reset Link" button

14. **Profile Management - View Profile**
    - **Given** authenticated user, **When** user navigates to profile page, **Then** system displays email (read-only), account creation date, last signin timestamp, display name field (editable), password change option

15. **Profile Management - Update Display Name**
    - **Given** user on profile page, **When** user updates display name from "User" to "John Doe" and saves, **Then** system updates display name, shows success message, displays "John Doe" in dashboard header

16. **Profile Management - Change Password**
    - **Given** user on profile page, **When** user enters current password, new password, and confirmation, **Then** system validates current password, updates password hash, invalidates all refresh tokens, shows "Password updated successfully"

---

### User Story 2 - Core Task Management (Priority: P2)

Authenticated users must be able to create tasks with title and description, view their complete task list, view individual task details, update task information, mark tasks as complete or pending, and delete tasks. Each user sees only their own tasks with strict backend enforcement.

**Why this priority**: Core business value - delivers MVP functionality after authentication (P1). Depends on user isolation enforcement.

**Independent Test**: User signs in → creates 3 tasks ("Buy groceries", "Team meeting", "Write report") → views list showing all 3 tasks → opens "Team meeting" task detail → updates title to "Team meeting notes" → marks "Buy groceries" as complete → deletes "Write report" → views list showing 2 remaining tasks (1 pending, 1 complete).

**Acceptance Scenarios**:

1. **Create Task - Valid Task**
   - **Given** authenticated user on dashboard, **When** user clicks "Add Task" button, fills title "Buy groceries" and description "Get milk, eggs, bread", submits form, **Then** system creates task with unique UUID, user_id from JWT token, status "pending", current timestamps, displays task at top of list, shows success message "Task created successfully"

2. **Create Task - Empty Title Validation**
   - **Given** user on create task form, **When** user submits empty title, **Then** system shows inline validation error "Title cannot be empty" and prevents submission

3. **Create Task - Title Length Validation**
   - **Given** user enters title with 201 characters, **When** user types 201st character, **Then** system shows character counter "201/200" in red, disables submit button, displays warning "Title cannot exceed 200 characters"

4. **Create Task - Description Truncation**
   - **Given** user enters description with 2050 characters, **When** user submits form, **Then** system auto-truncates description to 2000 characters, shows warning "Description was truncated to 2000 characters", creates task successfully

5. **Create Task - User Isolation Enforced**
   - **Given** malicious user attempts API request `POST /api/{different_user_id}/tasks` with valid JWT for user A but URL parameter user_id for user B, **Then** system validates JWT user_id does not match URL user_id, returns 403 Forbidden error "Unauthorized access"

6. **View Task List - Non-Empty List**
   - **Given** user has 10 tasks in database, **When** user views dashboard, **Then** system displays 10 tasks sorted by created_at DESC (newest first), each task shows: abbreviated ID (first 8 chars of UUID), title (truncated to 50 chars if longer), status indicator ([ ] pending or [✓] complete), creation date

7. **View Task List - Empty List**
   - **Given** user has 0 tasks, **When** user views dashboard, **Then** system displays empty state message "No tasks yet. Create your first task!" with prominent "Add Task" button

8. **View Task List - Cross-User Isolation**
    - **Given** User A has 5 tasks, User B has 3 tasks, **When** User A views dashboard, **Then** system displays only User A's 5 tasks (User B's tasks not visible)

9. **View Task Details - Successful View**
   - **Given** user viewing task list, **When** user clicks task row, **Then** system opens modal showing full task details: complete UUID, title, description (full text), status, priority, category, tags, created_at, updated_at, completed_at (if complete)

10. **View Task Details - Unauthorized Access**
    - **Given** malicious user attempts API request `GET /api/{user_id}/tasks/{other_user_task_id}`, **Then** system validates task.user_id matches JWT token user_id, returns 404 Not Found (not 403 to hide task existence for security)

11. **Update Task - Title Update**
    - **Given** user viewing task detail modal, **When** user clicks "Edit", changes title from "Buy groceries" to "Buy organic groceries", saves, **Then** system validates title (non-empty, ≤200 chars), updates task.title, sets updated_at to current timestamp, closes modal, refreshes list, shows success message

12. **Update Task - Description Update**
    - **Given** user in edit mode, **When** user updates description only (title unchanged), **Then** system updates task.description, updates task.updated_at, title remains unchanged

13. **Update Task - Empty Title Validation**
    - **Given** user in edit mode, **When** user clears title field and attempts save, **Then** system shows validation error "Title cannot be empty", prevents save

14. **Update Task - Unauthorized Update**
    - **Given** malicious user attempts `PUT /api/{user_id}/tasks/{other_user_task_id}`, **Then** system returns 403 Forbidden

15. **Mark Complete - Pending to Complete**
    - **Given** task with status "pending", **When** user clicks "Mark Complete" button, **Then** system sets status="complete", sets completed_at=current timestamp, maintains updated_at unchanged (completion is status change, not field modification), shows [✓] indicator, displays "Completed at: 2026-01-11 14:30:00"

16. **Mark Complete - Complete to Pending (Toggle)**
    - **Given** task with status "complete", **When** user clicks "Mark Incomplete" button, **Then** system shows confirmation dialog "Mark this task as incomplete? This will reset completion time.", if user confirms, sets status="pending", sets completed_at=null

17. **Mark Complete - Checkbox Toggle**
    - **Given** user viewing task list, **When** user clicks checkbox next to task without opening modal, **Then** system toggles status (pending ↔ complete), updates UI immediately (optimistic update), rolls back if API call fails

18. **Delete Task - Successful Deletion**
    - **Given** user viewing task detail modal, **When** user clicks "Delete Task", confirms in dialog "Are you sure? This cannot be undone.", **Then** system deletes task from database (hard delete), closes modal, refreshes list, shows success message "Task deleted successfully"

19. **Delete Task - Cancel Deletion**
    - **Given** user clicks "Delete Task", **When** user clicks "Cancel" in confirmation dialog, **Then** system does not delete task, modal remains open

20. **Delete Task - Unauthorized Deletion**
    - **Given** malicious user attempts `DELETE /api/{user_id}/tasks/{other_user_task_id}`, **Then** system returns 403 Forbidden

---

### User Story 3 - User Isolation & Security (Priority: P3)

System must guarantee that users can only access their own data, all API endpoints require valid authentication tokens, cross-user access attempts are blocked and logged, and security events are audited for compliance and monitoring.

**Why this priority**: Security is non-negotiable but verified through P2 tests. This story formalizes security testing, audit logging, and rate limiting.

**Independent Test**: User A creates task → User B attempts to view/update/delete User A's task via API with User B's valid JWT → all attempts return 403 Forbidden or 404 Not Found → audit log records attempted unauthorized access with user_id, task_id, timestamp, IP address.

**Acceptance Scenarios**:

1. **Authentication Enforcement - Missing Token**
   - **Given** unauthenticated user (no JWT token), **When** user attempts to access `/api/{user_id}/tasks`, **Then** system returns 401 Unauthorized, response body: `{"error_code": "AUTHENTICATION_REQUIRED", "detail": "Valid authentication token required"}`, frontend redirects to signin page

2. **Authentication Enforcement - Expired Token**
   - **Given** user with expired JWT access token (issued > 1 hour ago), **When** user makes API request, **Then** system validates token expiration, returns 401 Unauthorized with error code "TOKEN_EXPIRED", detail "Token has expired. Please refresh or sign in again.", frontend attempts token refresh using refresh token

3. **Authentication Enforcement - Malformed Token**
   - **Given** user sends request with malformed JWT token (invalid format, missing signature), **When** backend validates token, **Then** system returns 401 Unauthorized with error code "INVALID_TOKEN", detail "Authentication token is invalid"

4. **User Isolation - URL Parameter Validation**
   - **Given** User A authenticated with JWT (user_id=123), **When** User A requests `/api/456/tasks` (URL user_id=456 ≠ JWT user_id=123), **Then** system validates URL user_id matches JWT sub claim, returns 403 Forbidden, error code "FORBIDDEN", detail "Cannot access other users' resources"

5. **User Isolation - Direct Task Access**
   - **Given** User B attempts to read User A's task via `GET /api/{user_b_id}/tasks/{user_a_task_id}`, **Then** system queries database filtering by user_id AND task_id, finds no matching task (task.user_id ≠ URL user_id), returns 404 Not Found (not 403 to hide task existence)

6. **User Isolation - Database Row-Level Security**
   - **Given** database query `SELECT * FROM tasks WHERE user_id = :user_id`, **When** query executed, **Then** database row-level security policy automatically filters results by user_id from session context, ensures no cross-user data leakage even if application logic fails

7. **Audit Logging - Unauthorized Access Attempt**
   - **Given** User B attempts unauthorized access to User A's task, **When** system blocks request, **Then** audit log entry created: `{"timestamp": "2026-01-11T14:30:00Z", "event": "UNAUTHORIZED_ACCESS", "user_id": "user_b_id", "attempted_resource": "/api/user_a_id/tasks/task_id", "ip_address": "192.168.1.100", "user_agent": "..."}`

8. **Audit Logging - Failed Signin Attempts**
   - **Given** user enters incorrect password 3 times, **When** each signin attempt fails, **Then** system logs event: `{"event": "SIGNIN_FAILED", "email": "user@example.com", "ip_address": "...", "attempt_count": 1/2/3}`

9. **Audit Logging - Sensitive Operations**
   - **Given** user changes password, **When** password update succeeds, **Then** system logs INFO event: `{"event": "PASSWORD_CHANGED", "user_id": "...", "timestamp": "...", "ip_address": "..."}`

10. **Rate Limiting - Request Limit Exceeded**
    - **Given** user makes 101 requests within 1 minute, **When** 101st request received, **Then** system returns 429 Too Many Requests, response body: `{"error_code": "RATE_LIMIT_EXCEEDED", "detail": "Maximum 100 requests per minute. Try again in 30 seconds.", "retry_after": 30}`

11. **Rate Limiting - Account Lockout**
    - **Given** user fails signin 5 times within 10 minutes, **When** 5th failure detected, **Then** system locks account for 15 minutes, returns error "Account temporarily locked due to multiple failed signin attempts. Try again in 15 minutes."

12. **Token Security - Modified Payload**
    - **Given** malicious user modifies JWT payload (changes user_id from 123 to 456) without private key, **When** backend verifies token signature, **Then** signature validation fails, system returns 401 Unauthorized "Invalid token signature"

13. **Token Security - Token Blacklisting**
    - **Given** user changes password, **When** system updates password_hash, **Then** system adds all user's refresh tokens to blacklist, future requests with old refresh tokens return 401 "Token invalidated. Please sign in again."

---

### User Story 4 - API Contracts & Documentation (Priority: P4)

System must provide well-defined REST API endpoints with consistent request/response formats, comprehensive error handling, and auto-generated interactive API documentation accessible via browser for developer testing and client integration.

**Why this priority**: Enables frontend-backend contract testing and future API consumers. Advisory priority (can be validated via P2 tests, but formal documentation critical for development and maintenance).

**Independent Test**: Developer accesses `/docs` endpoint → sees Swagger UI with all 15+ API endpoints documented → selects `POST /api/{user_id}/tasks` → reviews request schema (title: string required, description: string optional, priority, category, tags) → clicks "Try it out" → fills sample data → executes request → receives 201 Created response with task object.

**Acceptance Scenarios**:

1. **API Documentation - Swagger UI Availability**
   - **Given** system deployed, **When** developer navigates to `/docs`, **Then** system serves Swagger UI showing all 15+ endpoints grouped by category (Auth, Tasks, Categories, Tags) with endpoint descriptions, request/response schemas, authentication requirements

2. **API Documentation - Interactive Testing**
   - **Given** developer on Swagger UI, **When** developer selects endpoint `GET /api/{user_id}/tasks`, clicks "Try it out", enters user_id and JWT token, executes request, **Then** Swagger sends real API request, displays response with status code (200 OK), formatted JSON body, response headers

3. **Request/Response Consistency - Success Response Format**
   - **Given** `POST /api/{user_id}/tasks` endpoint, **When** valid request sent: `{"title": "Buy milk", "description": "2% milk", "priority": "Medium"}`, **Then** response returns 201 Created with body: `{"id": "uuid", "user_id": "uuid", "title": "Buy milk", "description": "2% milk", "status": "pending", "priority": "Medium", "category_id": null, "tags": [], "created_at": "ISO8601", "updated_at": "ISO8601", "completed_at": null}`

4. **Request/Response Consistency - Validation Error Format**
   - **Given** `POST /api/{user_id}/tasks` with invalid payload `{"title": ""}` (empty title), **When** request sent, **Then** response returns 422 Unprocessable Entity with body: `{"error_code": "VALIDATION_ERROR", "detail": "Title cannot be empty", "field": "title"}`

5. **Request/Response Consistency - Authentication Error Format**
   - **Given** any protected endpoint, **When** request sent without JWT token, **Then** response returns 401 Unauthorized with body: `{"error_code": "AUTHENTICATION_REQUIRED", "detail": "Valid authentication token required"}`

6. **Request/Response Consistency - Authorization Error Format**
   - **Given** user attempts access to another user's resource, **When** request blocked, **Then** response returns 403 Forbidden with body: `{"error_code": "FORBIDDEN", "detail": "Cannot access other users' resources"}`

7. **Request/Response Consistency - Not Found Format**
   - **Given** `GET /api/{user_id}/tasks/{non_existent_id}`, **When** task ID does not exist, **Then** response returns 404 Not Found with body: `{"error_code": "NOT_FOUND", "detail": "Task not found"}`

8. **Request/Response Consistency - Server Error Format**
   - **Given** internal server error occurs (database connection lost), **When** error bubbles to API layer, **Then** response returns 500 Internal Server Error with body: `{"error_code": "INTERNAL_ERROR", "detail": "An internal error occurred. Please try again later.", "request_id": "uuid"}` (no stack trace exposed)

9. **Error Handling - Missing Content-Type Header**
   - **Given** `POST /api/{user_id}/tasks` without Content-Type header, **When** request sent, **Then** response returns 400 Bad Request with error "Content-Type header must be application/json"

10. **Error Handling - Malformed JSON**
    - **Given** request with malformed JSON payload `{"title": "Test"` (missing closing brace), **When** request sent, **Then** response returns 400 Bad Request with error code "INVALID_JSON", detail "Request body contains invalid JSON"

11. **Error Handling - Extra Unknown Fields**
    - **Given** request with payload `{"title": "Test", "unknown_field": "value"}`, **When** request sent, **Then** system accepts request (permissive parsing), ignores unknown_field, processes title normally (does not reject for extra fields)

12. **API Versioning - Version Display**
    - **Given** API documentation, **When** developer views Swagger UI header, **Then** system displays API version (e.g., "v1.0.0") and schema version (e.g., "OpenAPI 3.0.3")

---

### User Story 5 - Task Organization (Priorities, Categories, Tags) (Priority: P5)

Users must be able to assign priority levels (Low, Medium, High, Urgent) to tasks for importance ranking, assign one predefined category per task for broad classification (Work, Personal, Shopping, Health), create custom tags and assign multiple tags per task for flexible organization, and view tasks grouped by priority or category.

**Why this priority**: Enhances task management beyond basic CRUD (P2). Provides organizational capabilities critical for productivity workflows. Depends on core task infrastructure.

**Independent Test**: User creates task "Prepare presentation" → assigns priority "High" → selects category "Work" → creates tags "meeting", "urgent", "q1-goals" → assigns all 3 tags to task → views task list filtered by "Work" category showing task → views task list filtered by "urgent" tag showing task → sorts task list by priority showing "High" tasks first.

**Acceptance Scenarios**:

1. **Priority Assignment - Create Task with Priority**
   - **Given** user on create task form, **When** user fills title "Prepare presentation", selects priority "High" from dropdown (Low/Medium/High/Urgent), submits, **Then** system creates task with priority="High", displays task in list with "High" priority badge (red color indicator)

2. **Priority Assignment - Default Priority**
   - **Given** user creates task without selecting priority, **When** task created, **Then** system sets default priority="Medium"

3. **Priority Assignment - Update Task Priority**
   - **Given** existing task with priority="Low", **When** user opens task detail, changes priority to "Urgent", saves, **Then** system updates task.priority="Urgent", updates task.updated_at timestamp, refreshes UI showing "Urgent" badge

4. **Priority Assignment - Invalid Priority**
   - **Given** malicious API request with priority="Critical" (not in enum {Low, Medium, High, Urgent}), **When** request sent, **Then** system returns 422 Validation Error: "Priority must be one of: Low, Medium, High, Urgent"

5. **Category Management - View Predefined Categories**
   - **Given** user on create/edit task form, **When** user clicks category dropdown, **Then** system displays predefined categories: Work, Personal, Shopping, Health, Fitness, Finance, Education, Home (system-provided categories with is_system=true)

6. **Category Management - Assign Category to Task**
   - **Given** user creating task "Buy groceries", **When** user selects category "Shopping", submits, **Then** system creates task with category_id referencing "Shopping" category, displays "Shopping" category badge on task

7. **Category Management - Create Custom Category**
   - **Given** user on categories management page, **When** user clicks "Add Category", enters name "Hobbies", optionally selects color (blue), saves, **Then** system creates new Category (user_id=current_user, name="Hobbies", is_system=false, color="blue"), category appears in dropdown for future tasks

8. **Category Management - Delete Custom Category**
   - **Given** user has custom category "Hobbies" assigned to 3 tasks, **When** user deletes "Hobbies" category, **Then** system shows warning "3 tasks use this category. Tasks will become uncategorized.", if user confirms, sets category_id=null for all 3 tasks, deletes Category record

9. **Category Management - Cannot Delete System Categories**
   - **Given** user attempts to delete system category "Work" (is_system=true), **When** deletion requested, **Then** system returns error "Cannot delete system categories"

10. **Tag Management - Create Tag**
    - **Given** user on tags management page or inline tag creation, **When** user enters tag name "urgent" and saves, **Then** system creates Tag (user_id=current_user, name="urgent"), tag available for assignment to tasks

11. **Tag Management - Tag Name Uniqueness**
    - **Given** user already has tag "urgent", **When** user attempts to create another tag "urgent" (case-insensitive match), **Then** system returns error "Tag 'urgent' already exists. Tags must be unique (case-insensitive)."

12. **Tag Management - Assign Multiple Tags to Task**
    - **Given** user editing task, **When** user selects tags "meeting", "urgent", "q1-goals" from tag picker (multi-select), saves, **Then** system creates 3 TaskTag records (task_id + tag_id associations), displays all 3 tags as badges on task card

13. **Tag Management - Remove Tag from Task**
    - **Given** task has tags ["meeting", "urgent"], **When** user removes "urgent" tag, saves, **Then** system deletes TaskTag record for (task_id, "urgent" tag_id), task now shows only "meeting" tag

14. **Tag Management - Delete Tag Globally**
    - **Given** tag "urgent" is assigned to 5 tasks, **When** user deletes tag from tags management page, **Then** system shows warning "Tag 'urgent' is used by 5 tasks. Remove from all tasks?", if user confirms, deletes all 5 TaskTag associations, deletes Tag record

15. **Tag Management - Rename Tag**
    - **Given** tag "urgent" assigned to 5 tasks, **When** user renames tag to "high-priority", **Then** system updates Tag.name="high-priority", all 5 tasks now show "high-priority" tag (single source of truth)

16. **View Tasks Grouped by Priority**
    - **Given** user has 10 tasks: 2 Urgent, 3 High, 4 Medium, 1 Low, **When** user selects "Group by Priority" view, **Then** system displays tasks in 4 sections (Urgent → High → Medium → Low) with counts, each section sorted by created_at DESC

17. **View Tasks Grouped by Category**
    - **Given** user has tasks across 3 categories (Work: 5 tasks, Personal: 3 tasks, Shopping: 2 tasks), **When** user selects "Group by Category" view, **Then** system displays 3 sections with category names and counts

---

### User Story 6 - Task Discovery (Search, Filter, Sort) (Priority: P6)

Users must be able to find tasks quickly using full-text search across titles and descriptions, filter tasks by status (pending/complete), priority level, category, tags (with AND logic for multiple tags), and date ranges (created/updated/completed), sort tasks by priority (Urgent → Low), alphabetically by title (A-Z or Z-A), or by date fields, and combine multiple filters/search/sort simultaneously for precise task discovery.

**Why this priority**: Critical for usability at scale - users with 100+ tasks need efficient discovery mechanisms. Builds on organization features (P5).

**Independent Test**: User has 50 tasks → enters search query "meeting" → system returns 8 tasks containing "meeting" in title or description → user adds filter "priority=High" → system narrows results to 3 high-priority meeting tasks → user sorts by created_at DESC → system displays 3 tasks newest first → user clears filters → applies tag filter "urgent" AND "q1-goals" → system returns only tasks with both tags.

**Acceptance Scenarios**:

1. **Search - Title Search**
   - **Given** user has tasks with titles "Team meeting", "Weekly meeting notes", "Buy groceries", **When** user enters search query "meeting", **Then** system returns 2 tasks ("Team meeting", "Weekly meeting notes") using case-insensitive substring match

2. **Search - Description Search**
   - **Given** task "Buy groceries" has description "Get milk for morning meeting", **When** user searches "meeting", **Then** system returns "Buy groceries" task (matches description even though title doesn't match)

3. **Search - Title AND Description Search**
   - **Given** search query "project", **When** system executes search, **Then** system searches across both title and description fields using OR logic (matches if keyword in title OR description)

4. **Search - Special Characters Handling**
   - **Given** user searches for "C++ programming", **When** search executed, **Then** system properly escapes special characters (+), returns tasks matching "C++ programming" without treating + as SQL/regex operator

5. **Search - Empty Results**
   - **Given** user searches for "nonexistent keyword", **When** no tasks match, **Then** system displays empty state "No tasks found matching 'nonexistent keyword'. Try different keywords or clear filters."

6. **Filter - Status Filter (Pending)**
   - **Given** user has 10 pending tasks and 5 complete tasks, **When** user selects filter "Status: Pending", **Then** system displays only 10 pending tasks

7. **Filter - Status Filter (Complete)**
   - **Given** user selects filter "Status: Complete", **Then** system displays only 5 complete tasks with [✓] indicators and completed_at timestamps

8. **Filter - Priority Filter (Single)**
   - **Given** user has tasks: 2 Urgent, 3 High, 5 Medium, **When** user selects filter "Priority: Urgent", **Then** system displays only 2 Urgent tasks

9. **Filter - Priority Filter (Multiple)**
   - **Given** user selects filter "Priority: High OR Urgent" (multi-select), **Then** system displays 5 tasks (2 Urgent + 3 High) using OR logic

10. **Filter - Category Filter**
    - **Given** user has tasks: 5 Work, 3 Personal, 2 Shopping, **When** user selects filter "Category: Work", **Then** system displays only 5 Work tasks

11. **Filter - Tag Filter (Single Tag)**
    - **Given** user selects filter "Tag: urgent", **When** filter applied, **Then** system displays all tasks with "urgent" tag

12. **Filter - Tag Filter (Multiple Tags - AND Logic)**
    - **Given** user selects filters "Tag: urgent" AND "Tag: meeting", **When** filters applied, **Then** system displays only tasks that have BOTH "urgent" AND "meeting" tags (intersection, not union)

13. **Filter - Date Range Filter (Created)**
    - **Given** user selects date range filter "Created: 2026-01-01 to 2026-01-07", **When** filter applied, **Then** system displays only tasks where created_at is between start and end dates (inclusive)

14. **Filter - Date Range Filter (Completed)**
    - **Given** user selects "Completed: Last 7 days", **When** filter applied, **Then** system calculates date range (today - 7 days to today), displays tasks where completed_at falls in range

15. **Filter - Combined Filters**
    - **Given** user applies filters: Status=Pending AND Priority=High AND Category=Work, **When** all filters active, **Then** system applies AND logic across all filters, returns only pending high-priority work tasks

16. **Sort - Priority (Descending)**
    - **Given** user selects sort "Priority: High to Low", **When** sort applied, **Then** system orders tasks: Urgent → High → Medium → Low, within same priority sorts by created_at DESC

17. **Sort - Priority (Ascending)**
    - **Given** user selects sort "Priority: Low to High", **When** sort applied, **Then** system orders tasks: Low → Medium → High → Urgent

18. **Sort - Title Alphabetical (A-Z)**
    - **Given** user selects sort "Title: A-Z", **When** sort applied, **Then** system sorts tasks alphabetically by title case-insensitive ("Buy milk" before "Team meeting")

19. **Sort - Title Alphabetical (Z-A)**
    - **Given** user selects sort "Title: Z-A", **When** sort applied, **Then** system sorts tasks reverse alphabetical order

20. **Sort - Created Date (Newest First)**
    - **Given** user selects sort "Created: Newest First" (default), **When** sort applied, **Then** system sorts tasks by created_at DESC

21. **Sort - Created Date (Oldest First)**
    - **Given** user selects sort "Created: Oldest First", **When** sort applied, **Then** system sorts tasks by created_at ASC

22. **Combined Search + Filter + Sort**
    - **Given** user enters search "meeting", applies filters Priority=High AND Status=Pending, selects sort "Created: Newest First", **When** all operations combined, **Then** system executes in order: (1) search filter, (2) status/priority filters, (3) sort, returns matching results

23. **Performance - Search on Large Dataset**
    - **Given** user has 1000+ tasks, **When** user performs full-text search, **Then** system returns results within 2 seconds (p95 latency) using database full-text indexes

24. **Performance - Filter on Large Dataset**
    - **Given** user has 1000+ tasks, **When** user applies multiple filters, **Then** system returns filtered results within 1 second (p95 latency) using indexed columns

25. **URL Query Parameters**
    - **Given** user applies search + filters + sort, **When** page URL updates, **Then** URL contains query params: `/tasks?search=meeting&status=pending&priority=High&sort_by=created_at&order=desc`, URL is shareable and bookmarkable

---

### User Story 7 - Data Persistence & Integrity (Priority: P7)

System must persist all data (tasks, users, categories, tags, associations) in database storage, survive application restarts without data loss, support reversible schema migrations for database changes, enforce data integrity constraints (foreign keys, cascade deletes, unique constraints), and maintain many-to-many relationship integrity for task-tag associations.

**Why this priority**: Infrastructure concern validated through integration tests. Not user-facing but critical for production readiness and data reliability.

**Independent Test**: User creates 5 tasks with priorities, categories, and tags → stops backend server → restarts backend server → refreshes frontend → verifies all 5 tasks present with correct data (titles, descriptions, priorities, categories, tags) → deletes category assigned to 3 tasks → verifies tasks updated (category_id=null) → deletes tag assigned to 5 tasks → verifies all TaskTag associations removed.

**Acceptance Scenarios**:

1. **Data Persistence - Task Survival Across Restarts**
   - **Given** user creates 10 tasks with various attributes, **When** backend server restarts (graceful shutdown), **Then** all 10 tasks remain in database with correct user_id, titles, descriptions, statuses, priorities, category_ids, created_at, updated_at, completed_at

2. **Data Persistence - Tag Associations Survival**
   - **Given** task has 3 tags assigned (3 TaskTag records), **When** backend restarts, **Then** all 3 TaskTag associations persist, task displays all 3 tags after restart

3. **Data Persistence - Connection Retry**
   - **Given** database connection temporarily lost (network blip), **When** backend detects connection failure, **Then** system retries connection 3 times with exponential backoff (1s, 2s, 4s), if all retries fail, returns 503 Service Unavailable "Database connection unavailable"

4. **Migration Safety - Forward Migration**
   - **Given** new feature requires schema change (e.g., add column `task.due_date`), **When** migration applied via migration tool, **Then** schema updated, existing rows have due_date=null, migration recorded in schema_migrations table

5. **Migration Safety - Rollback Migration**
   - **Given** migration applied but needs reversal, **When** rollback executed, **Then** migration tool applies down migration (e.g., DROP COLUMN due_date), schema returns to previous state, data preserved

6. **Migration Safety - Migration Failure Rollback**
   - **Given** migration fails mid-execution (e.g., constraint violation), **When** migration tool detects error, **Then** database transaction rolled back, schema unchanged, error logged, migration marked as failed

7. **Foreign Key Constraint - Task to User**
   - **Given** database schema, **When** task created, **Then** task.user_id has foreign key constraint to users.id, prevents orphaned tasks (task without valid user)

8. **Foreign Key Constraint - Task to Category**
   - **Given** database schema, **When** task.category_id set, **Then** foreign key constraint ensures category exists in categories table (or null allowed)

9. **Cascade Delete - User Deletion**
   - **Given** user has 10 tasks, **When** user account deleted, **Then** database foreign key ON DELETE CASCADE deletes all 10 user's tasks automatically

10. **Cascade Delete - Category Deletion**
    - **Given** category "Work" assigned to 5 tasks, **When** category deleted, **Then** all 5 tasks have category_id set to null (ON DELETE SET NULL), tasks remain but become uncategorized

11. **Cascade Delete - Tag Deletion**
    - **Given** tag "urgent" assigned to 8 tasks (8 TaskTag records), **When** tag deleted, **Then** database ON DELETE CASCADE removes all 8 TaskTag records, tasks remain but lose "urgent" tag

12. **Unique Constraint - Tag Name Per User**
    - **Given** user attempts to create duplicate tag "meeting" (case-insensitive), **When** insert attempted, **Then** database UNIQUE constraint (user_id, LOWER(name)) prevents duplicate, returns error "Tag name must be unique"

13. **Unique Constraint - User Email**
    - **Given** email "user@example.com" already exists, **When** new user attempts registration with same email, **Then** database UNIQUE constraint on users.email prevents duplicate, registration fails with "Email already registered"

14. **Connection Pooling - Pool Exhaustion**
    - **Given** database connection pool configured with max 20 connections, **When** 20 concurrent requests use all connections, **Then** 21st request waits in queue (configurable timeout 30s), connection released when request completes, queued request proceeds

15. **Connection Pooling - Idle Connection Cleanup**
    - **Given** connection pool has 10 idle connections (no activity for 5 minutes), **When** connection pool manager runs cleanup, **Then** idle connections closed to free resources, pool maintains minimum 5 connections

16. **Query Timeout - Long-Running Query**
    - **Given** query executes for > 30 seconds (e.g., full table scan on 100k tasks), **When** timeout threshold exceeded, **Then** database cancels query, connection released, returns 500 Internal Server Error "Query timeout exceeded"

17. **Concurrent Updates - Optimistic Locking**
    - **Given** User A and User B both open same task in edit mode, **When** User A saves first, User B saves second, **Then** last write wins (User B's changes overwrite User A), OR system uses version field for conflict detection

18. **Concurrent Updates - Race Condition Prevention**
    - **Given** two simultaneous task creation requests for same user, **When** both generate UUID4 IDs, **Then** database ensures unique IDs (UUID collision probability negligible: < 1 in 10^36), both tasks created with different IDs

19. **Disk Space Handling - Disk Full**
    - **Given** database disk space full, **When** write operation attempted (INSERT/UPDATE), **Then** database returns error "Insufficient storage", backend catches error, returns 507 Insufficient Storage "Database storage full. Contact administrator."

20. **Data Integrity - Task Status Constraint**
    - **Given** database schema defines CHECK constraint task.status IN ('pending', 'complete'), **When** invalid status value attempted (e.g., 'archived'), **Then** database rejects insert/update, returns constraint violation error

---

### Edge Cases

**Input Boundaries & Validation:**
- Title exactly 200 characters (accept)
- Title 201 characters (reject with validation error)
- Description exactly 2000 characters (accept)
- Description 2001 characters (auto-truncate to 2000 with warning)
- Whitespace-only title "   " (reject after trim: "Title cannot be empty")
- Unicode characters in title/description (café ☕ 你好) (accept and store correctly using UTF-8)
- Email with Unicode domain (user@café.com) (accept if valid according to email RFC)
- Email without TLD (user@localhost) (reject: "Invalid email format")
- Password with 200 characters (accept, no upper limit)
- Password with all special characters (!@#$%^&*()_+-=) (accept if ≥ 8 chars)

**Authentication & Security:**
- Concurrent signup with same email (one succeeds, other fails with "Email already exists")
- Signin with URL-encoded special characters in password (decode and validate correctly)
- JWT token expiration during task list view (frontend detects 401, attempts refresh, redirects to signin if refresh fails)
- CSRF token validation on all POST/PUT/PATCH/DELETE (block if missing/invalid)
- XSS attempt in task title `<script>alert('XSS')</script>` (HTML auto-escaped by frontend framework, displays as text)
- SQL injection attempt `'; DROP TABLE tasks;--` (parameterized queries prevent execution)
- Search injection attempt: search query `"; DELETE FROM tasks; --` (properly escaped in search query, no SQL execution)

**Priority, Category, Tag Edge Cases:**
- Create task without selecting priority (default to "Medium")
- Create task without selecting category (category_id = null, allowed)
- Create task with 0 tags (allowed, empty tags array)
- Assign 20 tags to single task (accept, no hard limit, but UI may warn if > 10 tags)
- Delete category assigned to 100 tasks (show warning "100 tasks will become uncategorized", proceed on confirmation)
- Delete tag assigned to 200 tasks (remove all 200 TaskTag associations)
- Rename tag from "urgent" to "high-priority" (updates Tag.name, all tasks show new name immediately - single source of truth)
- Create tag with name "  urgent  " (trim whitespace to "urgent")
- Create tag with emoji "🔥urgent" (accept if database supports UTF-8)
- Tag name case-insensitivity: "urgent", "Urgent", "URGENT" are duplicates (enforce UNIQUE constraint on LOWER(name))

**Search, Filter, Sort Edge Cases:**
- Search with special regex characters `(project)` (escape properly, treat as literal string)
- Search with SQL wildcards `%test%` (escape, prevent SQL injection)
- Filter by non-existent category ID (return empty results, no error)
- Filter with date range where start > end (return validation error "Start date must be before end date")
- Sort 1000+ tasks by priority then created_at (execute within 500ms using compound index)
- Combine search + 5 filters + sort (execute within 2 seconds using query optimization)
- Empty search query "" (return all tasks, ignore search filter)
- Search query with only whitespace "   " (trim, return all tasks)

**Data Persistence & Concurrency:**
- Create 1000 tasks rapidly (all assigned unique UUID4s)
- Concurrent updates to same task by same user in two browser tabs (last write wins, no data loss)
- Network failure during task creation (frontend retries with idempotency key, prevents duplicate tasks)
- Database connection pool exhaustion (21st request waits max 30s, returns timeout error if connection not available)
- Migration with syntax error (migration fails, transaction rolled back, schema unchanged)
- Delete user with 10,000 tasks (cascade delete completes within reasonable time, or use batch deletion)

---

## Requirements *(mandatory)*

### Functional Requirements

**Authentication & Authorization (FR-001 to FR-010):**

**FR-001**: System MUST provide user registration endpoint accepting email and password with validation rules (email format per RFC 5322, password minimum 8 characters with at least 1 special character from set !@#$%^&*()_+-)

**FR-002**: System MUST send verification email with time-limited token (24-hour expiration) upon successful registration to confirm email ownership

**FR-003**: System MUST require email verification before allowing user signin to prevent fake account creation

**FR-004**: System MUST provide signin endpoint issuing JWT access token (1-hour expiration) and refresh token (7-day expiration) upon successful authentication

**FR-005**: System MUST provide password reset flow with time-limited reset token (1-hour expiration) sent via email for account recovery

**FR-006**: System MUST provide profile management endpoint allowing users to view account details (email, creation date, last signin time) and update display name and password

**FR-007**: System MUST validate JWT token on all protected API endpoints by verifying signature, checking expiration, and extracting user_id from token claims

**FR-008**: System MUST implement CSRF protection for all state-changing operations (POST, PUT, PATCH, DELETE) using secure token validation

**FR-009**: System MUST hash passwords using bcrypt algorithm with minimum 10 salt rounds before storing in database

**FR-010**: System MUST invalidate all refresh tokens on password change to force re-authentication on all devices

**Task Management (FR-011 to FR-020):**

**FR-011**: System MUST provide endpoint to create tasks with user_id (from JWT), title (required, 1-200 chars after trim), description (optional, auto-truncate at 2000 chars), priority (default "Medium"), category_id (optional), preserving all Phase I Task entity invariants

**FR-012**: System MUST provide endpoint to list all tasks for authenticated user, sorted by created_at DESC (newest first) by default, with support for query parameters (search, filters, sort)

**FR-013**: System MUST provide endpoint to retrieve single task details by task_id, enforcing user isolation (task.user_id must match JWT user_id)

**FR-014**: System MUST provide endpoint to update task title and/or description and/or priority and/or category and/or tags, auto-updating updated_at timestamp on any modification

**FR-015**: System MUST provide endpoint to toggle task completion status between "pending" and "complete" (PATCH `/tasks/{id}/complete`), setting/clearing completed_at timestamp accordingly

**FR-016**: System MUST provide endpoint to delete task by task_id (hard delete), cascading from user deletion (when user deleted, all user tasks deleted)

**FR-017**: System MUST preserve Phase I Task domain model attributes: id (UUID4), title, description, status, created_at, updated_at, completed_at

**FR-018**: System MUST enforce Phase I domain invariants: title non-empty after trim, title ≤ 200 chars, description ≤ 2000 chars (auto-truncate), status ∈ {pending, complete}

**FR-019**: System MUST validate all task inputs at API boundary using schema validation before passing to domain layer

**FR-020**: System MUST return task objects in consistent JSON format across all endpoints with ISO 8601 timestamps

**Task Organization (FR-021 to FR-035):**

**FR-021**: System MUST support 4 priority levels: "Low", "Medium", "High", "Urgent" with "Medium" as default when not specified

**FR-022**: System MUST validate priority field to ensure value is one of {Low, Medium, High, Urgent}, rejecting invalid values with 422 Validation Error

**FR-023**: System MUST update task.updated_at timestamp when priority field is modified

**FR-024**: System MUST provide predefined system categories: Work, Personal, Shopping, Health, Fitness, Finance, Education, Home (is_system=true, cannot be deleted)

**FR-025**: System MUST allow users to create custom categories with name (required, max 100 chars) and optional color field

**FR-026**: System MUST enforce category name uniqueness per user (case-insensitive)

**FR-027**: System MUST allow tasks to have zero or one category (category_id nullable foreign key to categories table)

**FR-028**: System MUST set task.category_id to null when assigned category is deleted (ON DELETE SET NULL)

**FR-029**: System MUST prevent deletion of system categories (is_system=true)

**FR-030**: System MUST allow users to create custom tags with name (required, max 50 chars, unique per user case-insensitive)

**FR-031**: System MUST support many-to-many relationship between tasks and tags via TaskTag join table (task_id, tag_id)

**FR-032**: System MUST allow tasks to have zero to unlimited tags assigned

**FR-033**: System MUST remove all TaskTag associations when tag is deleted (ON DELETE CASCADE), affecting all tasks with that tag

**FR-034**: System MUST provide endpoint to rename tag, updating Tag.name and automatically reflecting change on all associated tasks

**FR-035**: System MUST return tasks with tags array populated in response JSON

**Task Discovery (FR-036 to FR-050):**

**FR-036**: System MUST provide full-text search across task title and description fields using case-insensitive substring matching

**FR-037**: System MUST accept query parameter `search` on task list endpoint for full-text search

**FR-038**: System MUST properly escape special characters in search queries to prevent SQL injection and regex injection

**FR-039**: System MUST accept query parameter `status` with values {pending, complete, all} to filter tasks by completion status

**FR-040**: System MUST accept query parameter `priority` with values {Low, Medium, High, Urgent} supporting multiple values (OR logic) to filter tasks by priority level

**FR-041**: System MUST accept query parameter `category` to filter tasks by category ID or name

**FR-042**: System MUST accept query parameter `tags` accepting comma-separated tag names, applying AND logic (only tasks with ALL specified tags)

**FR-043**: System MUST accept date range query parameters: `created_after`, `created_before`, `updated_after`, `updated_before`, `completed_after`, `completed_before` in ISO 8601 format

**FR-044**: System MUST validate date range parameters ensuring start date ≤ end date, returning 400 Bad Request if invalid

**FR-045**: System MUST accept query parameter `sort_by` with values {priority, created_at, updated_at, title} to specify sort field

**FR-046**: System MUST accept query parameter `order` with values {asc, desc} to specify sort direction (default: desc for dates, asc for title)

**FR-047**: System MUST support combining search + multiple filters + sort in single request, applying filters sequentially: search → status/priority/category/tags/date filters → sort

**FR-048**: System MUST return search and filter results within 2 seconds for datasets up to 1000 tasks (p95 latency) using database indexes

**FR-049**: System MUST update URL query parameters when user applies search/filters/sort for bookmarkable and shareable URLs

**FR-050**: System MUST display empty state message "No tasks found" when search/filters return zero results, with option to clear filters

**API Contracts (FR-051 to FR-070):**

**Task Endpoints:**
**FR-051**: System MUST provide `GET /api/{user_id}/tasks` endpoint returning JSON array of task objects with support for query parameters (search, status, priority, category, tags, date ranges, sort_by, order)

**FR-052**: System MUST provide `POST /api/{user_id}/tasks` endpoint accepting JSON payload `{title: string required, description?: string, priority?: string, category_id?: string, tags?: string[]}` returning 201 Created with task object

**FR-053**: System MUST provide `GET /api/{user_id}/tasks/{id}` endpoint returning single task object with populated category and tags, or 404 if not found

**FR-054**: System MUST provide `PUT /api/{user_id}/tasks/{id}` endpoint accepting JSON payload `{title?: string, description?: string, priority?: string, category_id?: string, tags?: string[]}` returning 200 OK with updated task object

**FR-055**: System MUST provide `DELETE /api/{user_id}/tasks/{id}` endpoint returning 204 No Content on successful deletion

**FR-056**: System MUST provide `PATCH /api/{user_id}/tasks/{id}/complete` endpoint toggling completion status, returning 200 OK with updated task object

**Category Endpoints:**
**FR-057**: System MUST provide `GET /api/{user_id}/categories` endpoint returning array of categories (system + user's custom categories)

**FR-058**: System MUST provide `POST /api/{user_id}/categories` endpoint accepting `{name: string, color?: string}` returning 201 Created with category object

**FR-059**: System MUST provide `DELETE /api/{user_id}/categories/{id}` endpoint setting category_id=null for all tasks using that category, returning 204 No Content

**Tag Endpoints:**
**FR-060**: System MUST provide `GET /api/{user_id}/tags` endpoint returning array of user's tags sorted alphabetically

**FR-061**: System MUST provide `POST /api/{user_id}/tags` endpoint accepting `{name: string}` returning 201 Created with tag object

**FR-062**: System MUST provide `PUT /api/{user_id}/tags/{id}` endpoint accepting `{name: string}` for renaming tag, returning 200 OK with updated tag object

**FR-063**: System MUST provide `DELETE /api/{user_id}/tags/{id}` endpoint removing all TaskTag associations and deleting tag, returning 204 No Content

**Security & Validation:**
**FR-064**: System MUST validate URL `{user_id}` parameter matches authenticated user's JWT token user_id claim on all endpoints

**FR-065**: System MUST return 403 Forbidden if URL user_id does not match JWT token user_id

**FR-066**: System MUST return 404 Not Found (not 403) when user attempts to access another user's task to hide task existence for security

**FR-067**: System MUST validate all request payloads against expected schema, returning 422 Unprocessable Entity with field-specific error messages for validation failures

**FR-068**: System MUST return consistent error response format: `{error_code: string, detail: string, field?: string}`

**FR-069**: System MUST serve auto-generated API documentation at `/docs` endpoint using OpenAPI 3.0 specification with request/response examples

**FR-070**: System MUST include request_id in all 500 Internal Server Error responses for troubleshooting

**Data Persistence (FR-071 to FR-078):**

**FR-071**: System MUST persist all entities (users, tasks, categories, tags, task_tag associations) in relational database with proper schema design

**FR-072**: System MUST implement row-level security policies filtering tasks by user_id automatically at database level

**FR-073**: System MUST use database migration tool for all schema changes with rollback capability (up/down migrations)

**FR-074**: System MUST implement connection pooling with configurable pool size (default min 5, max 20 connections)

**FR-075**: System MUST configure database connection timeout (30 seconds) and query timeout (30 seconds) to prevent hung connections

**FR-076**: System MUST define foreign key constraints: task.user_id → users.id (ON DELETE CASCADE), task.category_id → categories.id (ON DELETE SET NULL), task_tag.task_id → tasks.id (ON DELETE CASCADE), task_tag.tag_id → tags.id (ON DELETE CASCADE)

**FR-077**: System MUST define unique constraints: users.email, (tags.user_id, LOWER(tags.name)), (task_tag.task_id, task_tag.tag_id)

**FR-078**: System MUST define check constraints: task.status IN ('pending', 'complete'), task.priority IN ('Low', 'Medium', 'High', 'Urgent')

**Security & Error Handling (FR-079 to FR-087):**

**FR-079**: System MUST implement rate limiting at 100 requests per minute per user, returning 429 Too Many Requests with Retry-After header when exceeded

**FR-080**: System MUST implement account lockout after 5 failed signin attempts within 10 minutes, locking account for 15 minutes

**FR-081**: System MUST return generic error messages to users for authentication failures ("Invalid email or password" instead of "Email not found" or "Incorrect password")

**FR-082**: System MUST log detailed error context server-side (stack trace, user_id, request_id, timestamp, IP address) without exposing to users

**FR-083**: System MUST implement structured JSON logging with fields: timestamp, level (DEBUG/INFO/WARNING/ERROR/CRITICAL), service, user_id, request_id, message, context

**FR-084**: System MUST validate all user inputs at API layer before passing to domain layer

**FR-085**: System MUST use parameterized queries for all database operations to prevent SQL injection

**FR-086**: System MUST implement Content Security Policy (CSP) headers to prevent XSS attacks

**FR-087**: System MUST serve application over HTTPS in production with TLS 1.2+ required

**Frontend Requirements (FR-088 to FR-095):**

**FR-088**: System MUST provide responsive web UI accessible on desktop (≥1024px width), tablet (768-1023px), and mobile (320-767px) browsers

**FR-089**: System MUST implement loading states (spinners, skeleton screens) for all async operations (API calls) to provide user feedback

**FR-090**: System MUST implement error boundaries catching unhandled errors and displaying user-friendly fallback UI instead of blank screen

**FR-091**: System MUST implement client-side form validation (real-time feedback as user types) before submission to improve UX

**FR-092**: System MUST implement optimistic UI updates (task appears immediately in list, rolls back on API error) for create/update/delete operations

**FR-093**: System MUST persist authentication state in secure HTTP-only cookies (not localStorage) to prevent XSS token theft

**FR-094**: System MUST implement WCAG 2.1 AA accessibility compliance (keyboard navigation, screen reader support, ARIA labels, sufficient color contrast)

**FR-095**: System MUST display user-facing timestamps in local timezone with relative time (e.g., "2 hours ago", "Yesterday", "Jan 11, 2026")

**Future Enhancements - Explicitly Deferred to Phase III+ (FR-096 to FR-100):**

**FR-096**: System MUST NOT implement task due dates (deadline tracking) in Phase II - defer to future phase

**FR-097**: System MUST NOT implement recurring tasks (daily, weekly, monthly patterns) in Phase II - defer to future phase

**FR-098**: System MUST NOT implement task attachments (file uploads) in Phase II - defer to future phase

**FR-099**: System MUST NOT implement task collaboration (sharing, assignments, comments) in Phase II - defer to future phase

**FR-100**: System MUST NOT implement real-time sync via WebSockets or push notifications in Phase II - defer to Phase III

---

### Key Entities

**User:**
- `id`: UUID4 (string, unique, immutable, primary key)
- `email`: String (required, unique, validated email format per RFC 5322)
- `password_hash`: String (bcrypt hashed with 10+ salt rounds, never exposed in API responses)
- `email_verified`: Boolean (default false, set true on verification)
- `display_name`: String (optional, max 100 chars, nullable)
- `created_at`: Datetime (ISO 8601, immutable, auto-set on creation)
- `last_signin_at`: Datetime (ISO 8601, updated on successful signin)

**Task (Extended from Phase I):**
- `id`: UUID4 (string, unique, immutable, primary key)
- `user_id`: UUID4 (string, foreign key to User.id, indexed, ON DELETE CASCADE)
- `title`: String (required, 1-200 chars after trim)
- `description`: String (optional, 0-2000 chars, auto-truncated on excess)
- `status`: Enum ("pending" | "complete")
- **`priority`**: Enum ("Low" | "Medium" | "High" | "Urgent", default "Medium") - **NEW**
- **`category_id`**: UUID4 | null (foreign key to Category.id, ON DELETE SET NULL) - **NEW**
- `created_at`: Datetime (ISO 8601, immutable)
- `updated_at`: Datetime (ISO 8601, updated on title/description/priority/category/tags changes)
- `completed_at`: Datetime | null (set when status changes to "complete", null when "pending")

**Category:**
- `id`: UUID4 (string, unique, immutable, primary key)
- `user_id`: UUID4 | null (foreign key to User.id, null for system categories, ON DELETE CASCADE for user categories)
- `name`: String (required, max 100 chars, unique per user case-insensitive)
- `is_system`: Boolean (true for predefined categories like "Work", "Personal", false for user-created)
- `color`: String (optional, hex color code for UI display)
- `created_at`: Datetime (ISO 8601, immutable)

**Tag:**
- `id`: UUID4 (string, unique, immutable, primary key)
- `user_id`: UUID4 (foreign key to User.id, ON DELETE CASCADE)
- `name`: String (required, max 50 chars, unique per user case-insensitive)
- `created_at`: Datetime (ISO 8601, immutable)

**TaskTag (Join Table):**
- `task_id`: UUID4 (foreign key to Task.id, ON DELETE CASCADE)
- `tag_id`: UUID4 (foreign key to Tag.id, ON DELETE CASCADE)
- `created_at`: Datetime (ISO 8601, when tag assigned to task)
- **Composite Primary Key**: (task_id, tag_id)

**Authentication Token (JWT Claims):**
- `sub`: User ID (UUID4 string, identifies token owner)
- `email`: User email (string, for display purposes)
- `iat`: Issued at timestamp (Unix timestamp, when token created)
- `exp`: Expiration timestamp (Unix timestamp, 1 hour for access tokens, 7 days for refresh tokens)
- `token_type`: "access" | "refresh"

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

**SC-001**: 95% of users complete registration flow on first attempt without errors (usability metric, tracked via analytics, measured over first 30 days)

**SC-002**: Users can create a task (with priority, category, and tags) within 5 seconds of clicking "Add Task" button (performance target, p95 latency from button click to task appearing in list)

**SC-003**: 100% of cross-user access attempts blocked by backend (security guarantee, validated via integration tests simulating malicious access patterns)

**SC-004**: Zero data loss across application restarts (data integrity, validated via persistence tests creating tasks before restart and verifying after restart for tasks, categories, tags, and associations)

**SC-005**: Users can complete password reset flow within 2 minutes from clicking "Forgot password" to signing in with new password (usability metric, timed user test)

**SC-006**: API read operations (GET /tasks, GET /tasks/{id}) respond within 500ms for task lists up to 1000 items (p95 latency, load testing)

**SC-007**: API write operations (POST/PUT/DELETE tasks, categories, tags) respond within 1 second including database commits and tag/category associations (p95 latency, load testing)

**SC-008**: Search returns results within 2 seconds for datasets of 1000+ tasks (p95 latency, full-text search performance test using database full-text indexes)

**SC-009**: Filter operations (status, priority, category, tags, date ranges) complete within 1 second for any filter combination on 1000+ tasks (p95 latency, query optimization test)

**SC-010**: Sort operations (by priority, title, dates) complete within 500ms for 1000+ tasks (p95 latency, indexed column sort test)

**SC-011**: System handles 50 concurrent users performing mixed operations (read/write) without degradation (scalability target, load testing with concurrent sessions)

**SC-012**: Frontend achieves Lighthouse score ≥ 90 for Performance, Accessibility, and Best Practices (quality metric, automated Lighthouse CI)

**SC-013**: Backend achieves ≥ 80% unit test coverage for domain/services layers and ≥ 70% integration test coverage for API endpoints (testing rigor, pytest-cov report)

**SC-014**: Frontend achieves ≥ 70% component test coverage (testing rigor, Jest/Vitest coverage report)

**SC-015**: All 15+ API endpoints (6 task, 3 category, 4 tag, 2+ auth) documented in auto-generated Swagger UI at `/docs` with request/response examples and authentication requirements (documentation completeness)

**SC-016**: All critical user flows have end-to-end tests (registration → signin → create task → search → filter → sort → delete → signout) using automated testing framework (regression safety)

**SC-017**: System logs all security events (failed signin attempts, unauthorized access, password changes) with user_id, IP address, and timestamp in structured JSON format (audit trail for compliance)

**SC-018**: Zero unhandled exceptions in production for 30 days after launch (stability metric, error monitoring dashboard shows 0 unhandled errors)

**SC-019**: Users can create a new tag and assign it to a task within 10 seconds (usability metric, timed user test measuring tag creation + assignment workflow)

**SC-020**: Users can find a specific task using search + filters within 15 seconds (task discovery efficiency, timed user test: user given task name, must use search/filters to locate it)

---

**End of Specification**
