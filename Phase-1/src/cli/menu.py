"""
Main menu orchestration for Todo CLI application.

Implements:
- Menu display loop
- User choice validation
- Operation routing
- Error handling (never crash)

Menu options:
1. Create Task
2. View All Tasks
3. Update Task
4. Mark Task Complete
5. Delete Task
6. Exit
"""

from src.cli.operations import (
    create_task_operation,
    delete_task_operation,
    mark_complete_operation,
    update_task_operation,
    view_all_tasks_operation,
)
from src.storage.repository_interface import RepositoryInterface


def display_menu(repository: RepositoryInterface) -> None:
    """
    Display main menu and handle user interactions.

    Workflow:
    1. Display menu options (1-6)
    2. Capture user choice
    3. Validate choice (must be 1-6)
    4. Route to appropriate operation
    5. Repeat until user selects Exit (6)

    Error Handling:
    - Invalid choices: Display error and re-prompt
    - KeyboardInterrupt (Ctrl+C): Exit gracefully
    - Operation exceptions: Display error, continue to menu

    Args:
        repository: Repository implementation for task storage

    Never crashes - always returns to menu after errors
    """
    print("\n" + "=" * 50)
    print("         Todo Application - Phase I")
    print("=" * 50)

    while True:
        try:
            # Display menu options
            print("\n--- Main Menu ---\n")
            print("1. Create Task")
            print("2. View All Tasks")
            print("3. Update Task")
            print("4. Mark Task Complete")
            print("5. Delete Task")
            print("6. Exit")

            # Capture user choice
            choice = input("\nChoose an option (1-6): ").strip()

            # Route to appropriate operation
            if choice == "1":
                create_task_operation(repository)
            elif choice == "2":
                view_all_tasks_operation(repository)
            elif choice == "3":
                update_task_operation(repository)
            elif choice == "4":
                mark_complete_operation(repository)
            elif choice == "5":
                delete_task_operation(repository)
            elif choice == "6":
                print("\nExiting Todo Application. Goodbye!\n")
                break
            else:
                # Invalid choice
                print(f"\n✗ Invalid choice: '{choice}'. Please enter a number between 1-6.\n")

        except KeyboardInterrupt:
            # User pressed Ctrl+C
            print("\n\nExiting Todo Application. Goodbye!\n")
            break

        except Exception as e:
            # Catch any unexpected errors to prevent crashes
            print(f"\n✗ An unexpected error occurred: {e}\n")
            print("Returning to main menu...\n")
            # Continue to menu (never crash)
