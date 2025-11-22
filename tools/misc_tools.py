from langchain_core.tools import tool

todos = []
@tool
def add_todo(content: str):
    """
    Add a new todo item.

    Args:
        content (str): The content of the todo item. 
    """
    print("Adding todo:", content)
    todos.append({
        "content": content,
        "status": "pending",
        "activeForm": content
    })
    return todos[-1]

@tool
def list_todos(status: str = None):
    """
    List all todo items, optionally filtered by status.

    Args:
        status (str): Filter todos by status ("pending", "in_progress", "completed"). 
    """
    print("Listing todos with status =", status)
    if status:
        return [todo for todo in todos if todo["status"] == status]
    return todos

@tool
def update_todo(index: int, status: str = None, activeForm: str = None):
    """
    Update the status or active form of a todo item.

    Args:
        index (int): The index of the todo item to update.
        status (str): New status ("pending", "in_progress", "completed").
        activeForm (str): New active form of the description.
    """
    print("Updating todo at index:", index, "with status =", status, "and activeForm =", activeForm)
    if index < 0 or index >= len(todos):
        raise IndexError("Todo index out of range")
    
    if status:
        todos[index]["status"] = status
    if activeForm:
        todos[index]["activeForm"] = activeForm
    
    return todos[index]

@tool
def clear_todos():
    """
    Clear all todo items.
    """
    print("Clearing all todos")
    todos.clear()
    return "All todos cleared."

misc_tools = [
    add_todo,
    list_todos,
    update_todo,
    clear_todos,
]