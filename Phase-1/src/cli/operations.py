"""
CLI operation handlers for CRUD functionality.

Implements:
- create_task_operation (User Story 1)
- view_all_tasks_operation (User Story 2)
- view_task_details_operation (User Story 2)
- update_task_operation (User Story 3)
- mark_complete_operation (User Story 4)
- delete_task_operation (User Story 5)

All operations depend on RepositoryInterface abstraction (dependency injection).
"""

from src.domain.exceptions import DomainStateError, DomainValidationError
from src.domain.task import Task
from src.storage.repository_interface import RepositoryInterface


def create_task_operation(repository: RepositoryInterface) -> None:
    """
    Create a new task with user input (User Story 1 - P1).

    Workflow:
    1. Prompt for task title (required, max 200 chars)
    2. Prompt for task description (optional, max 2000 chars auto-truncate)
    3. Create Task entity (validates invariants)
    4. Add task to repository
    5. Display success message with first 8 chars of UUID

    Args:
        repository: Repository implementation for task storage

    User Story: P1 - User wants to add a new task to track work
    Acceptance Scenarios: P1.1-P1.6 (spec.md lines 27-38)
    """
    print("\n--- Create New Task ---\n")

    # Prompt for title with retry on validation error
    while True:
        title = input("Enter task title (required, max 200 chars): ").strip()

        try:
            # Prompt for description
            description = input("Enter task description (optional, max 2000 chars): ").strip()

            # Create task entity (validates title/description)
            task = Task(title=title, description=description)

            # Add to repository
            repository.add(task)

            # Display success message with UUID prefix
            task_id_short = task.id[:8]
            print(f"\n✓ Task created successfully! ID: {task_id_short}\n")
            break

        except DomainValidationError as e:
            # Display validation error and retry
            print(f"\n✗ Error: {e}\n")
            # Continue loop to re-prompt for title


def view_all_tasks_operation(repository: RepositoryInterface) -> None:
    """
    View all tasks in compact list format (User Story 2 - P2).

    Workflow:
    1. Retrieve all tasks from repository (sorted newest first)
    2. If empty, display "No tasks found"
    3. Display summary: Total tasks (X pending, Y complete)
    4. Display table: ID | Status | Title | Created
    5. Optionally prompt for task ID to view details

    Args:
        repository: Repository implementation for task storage

    User Story: P2 - User wants to see all tasks or view specific task details
    Acceptance Scenarios: P2.1-P2.6 (spec.md lines 47-57)
    """
    print("\n--- All Tasks ---\n")

    # Retrieve all tasks (sorted by created_at DESC)
    all_tasks = repository.get_all()

    # Handle empty list
    if not all_tasks:
        print("No tasks found. Create your first task!\n")
        return

    # Calculate summary statistics
    total_count = len(all_tasks)
    pending_count = sum(1 for t in all_tasks if t.status == "pending")
    complete_count = sum(1 for t in all_tasks if t.status == "complete")

    # Display summary
    print(f"Total: {total_count} tasks ({pending_count} pending, {complete_count} complete)\n")

    # Display table header
    print(f"{'ID':<10} | {'Status':<8} | {'Title':<50} | {'Created':<20}")
    print("-" * 100)

    # Display each task
    for task in all_tasks:
        task_id_short = task.id[:8]
        status_icon = "[✓]" if task.status == "complete" else "[ ]"
        title_truncated = task.title[:50] if len(task.title) > 50 else task.title
        created_str = task.created_at.strftime("%Y-%m-%d %H:%M")

        print(f"{task_id_short:<10} | {status_icon:<8} | {title_truncated:<50} | {created_str:<20}")

    print()

    # Optional: Prompt for task ID to view details
    view_details = input("Enter task ID to view details (or press Enter to skip): ").strip()
    if view_details:
        view_task_details_operation(repository, view_details)


def view_task_details_operation(repository: RepositoryInterface, task_id: str) -> None:
    """
    View full task details by ID (User Story 2 - P2).

    Workflow:
    1. Retrieve task by ID
    2. If not found, display "Task not found"
    3. Display all 7 task attributes with labels

    Args:
        repository: Repository implementation for task storage
        task_id: Task UUID4 string (can be partial - first 8 chars)

    Acceptance Scenarios: P2.3 (spec.md line 53-54)
    """
    print(f"\n--- Task Details: {task_id} ---\n")

    # Find task by full or partial ID
    all_tasks = repository.get_all()
    task = None
    for t in all_tasks:
        if t.id.startswith(task_id):
            task = t
            break

    if not task:
        print(f"✗ Task not found: {task_id}\n")
        return

    # Display full task details
    print(f"ID: {task.id}")
    print(f"Title: {task.title}")
    print(f"Description: {task.description if task.description else '(none)'}")
    print(f"Status: {task.status}")
    print(f"Created: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Updated: {task.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    if task.completed_at:
        print(f"Completed: {task.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("Completed: (not completed)")
    print()


def update_task_operation(repository: RepositoryInterface) -> None:
    """
    Update task title and/or description (User Story 3 - P3).

    Workflow:
    1. Prompt for task ID
    2. Retrieve task, handle not found
    3. Display current title and description
    4. Prompt for new title (Enter to keep current)
    5. Prompt for new description (Enter to keep current)
    6. Update task entity if values changed
    7. Save updated task to repository
    8. Display success message

    Args:
        repository: Repository implementation for task storage

    User Story: P3 - User wants to edit task title or description
    Acceptance Scenarios: P3.1-P3.8 (spec.md lines 69-78)
    """
    print("\n--- Update Task ---\n")

    # Prompt for task ID
    task_id = input("Enter task ID to update: ").strip()

    # Find task by full or partial ID
    all_tasks = repository.get_all()
    task = None
    for t in all_tasks:
        if t.id.startswith(task_id):
            task = t
            break

    if not task:
        print(f"\n✗ Task not found: {task_id}\n")
        return

    # Display current values
    print(f"\nCurrent Title: {task.title}")
    print(f"Current Description: {task.description if task.description else '(none)'}\n")

    try:
        # Prompt for new title (Enter to keep current)
        new_title_input = input("Enter new title (or press Enter to keep current): ").strip()
        if new_title_input:
            task.update_title(new_title_input)

        # Prompt for new description (Enter to keep current)
        new_description_input = input(
            "Enter new description (or press Enter to keep current): "
        ).strip()
        if new_description_input:
            task.update_description(new_description_input)

        # Save updated task
        repository.update(task)

        print("\n✓ Task updated successfully!\n")

    except DomainValidationError as e:
        print(f"\n✗ Error: {e}\n")

    except KeyboardInterrupt:
        print("\n\n✗ Operation cancelled.\n")


def mark_complete_operation(repository: RepositoryInterface) -> None:
    """
    Mark a task as complete (User Story 4 - P4).

    Workflow:
    1. Prompt for task ID
    2. Retrieve task, handle not found
    3. Call task.mark_complete() (validates state transition)
    4. Save updated task to repository
    5. Display success message with completion timestamp

    Args:
        repository: Repository implementation for task storage

    User Story: P4 - User wants to mark tasks as done
    Acceptance Scenarios: P4.1-P4.5 (spec.md lines 90-96)
    """
    print("\n--- Mark Task Complete ---\n")

    # Prompt for task ID
    task_id = input("Enter task ID to mark complete: ").strip()

    # Find task by full or partial ID
    all_tasks = repository.get_all()
    task = None
    for t in all_tasks:
        if t.id.startswith(task_id):
            task = t
            break

    if not task:
        print(f"\n✗ Task not found: {task_id}\n")
        return

    try:
        # Mark task as complete (validates state)
        task.mark_complete()

        # Save updated task
        repository.update(task)

        # Display success message with timestamp
        completed_time = (
            task.completed_at.strftime("%Y-%m-%d %H:%M:%S") if task.completed_at else "now"
        )
        print(f'\n✓ Task "{task.title}" marked as complete!' f" Completed at: {completed_time}\n")

    except DomainStateError as e:
        print(f"\n✗ Error: {e}\n")


def delete_task_operation(repository: RepositoryInterface) -> None:
    """
    Delete a task permanently with confirmation (User Story 5 - P5).

    Workflow:
    1. Prompt for task ID
    2. Retrieve task, handle not found
    3. Display task details (ID, title, status)
    4. Prompt for confirmation: "Are you sure? (y/n)"
    5. If 'y', delete task from repository
    6. If 'n', cancel operation

    Args:
        repository: Repository implementation for task storage

    User Story: P5 - User wants to remove tasks permanently
    Acceptance Scenarios: P5.1-P5.5 (spec.md lines 105-115)
    """
    print("\n--- Delete Task ---\n")

    # Prompt for task ID
    task_id = input("Enter task ID to delete: ").strip()

    # Find task by full or partial ID
    all_tasks = repository.get_all()
    task = None
    for t in all_tasks:
        if t.id.startswith(task_id):
            task = t
            break

    if not task:
        print(f"\n✗ Task not found: {task_id}\n")
        return

    # Display task details for confirmation
    print("\nTask to delete:")
    print(f"  ID: {task.id[:8]}")
    print(f"  Title: {task.title}")
    print(f"  Status: {task.status}\n")

    # Prompt for confirmation
    confirmation = input("⚠ Are you sure you want to delete this task? (y/n): ").strip().lower()

    if confirmation == "y":
        # Delete task
        repository.delete(task.id)
        print(f'\n✓ Task "{task.title}" deleted successfully!\n')
    else:
        print("\n✗ Deletion cancelled.\n")
