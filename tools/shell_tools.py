
from subprocess import Popen, PIPE
from typing import List, Optional
import os
import shlex
import signal
import time
import subprocess
from langchain_core.tools import tool

@tool
def run_shell_command(command: str, cwd: Optional[str] = None, timeout: Optional[int] = None, run_in_bg: bool = False) -> str:
    """
    Run a shell command and return its output.

    Args:
        command (str): The shell command to run.
        cwd (Optional[str]): The working directory to run the command in.
        timeout (Optional[int]): Timeout for the command in seconds.
    """
    print("Running shell command:", command, "in", cwd or os.getcwd(), "with timeout =", timeout, "run_in_bg =", run_in_bg)
    try:
        if run_in_bg:
            process = Popen(command, cwd=cwd, stdout=PIPE, stderr=PIPE, text=True, shell=True, preexec_fn=os.setsid)
            return f"Process started in background with PID {process.pid}"
        else:
            result = subprocess.run(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
                shell=True,
                check=True
            )
            return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed: {e.stderr.strip()}") from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError("Command timed out") from e

@tool
def grep(
    pattern: str,
    path: Optional[str] = None,
    glob: Optional[str] = None,
    type: Optional[str] = None,
    output_mode: Optional[str] = None,
    i: Optional[bool] = None,
    n: Optional[bool] = None,
    B: Optional[int] = None,
    A: Optional[int] = None,
    C: Optional[int] = None,
    head_limit: Optional[int] = None,
    multiline: Optional[bool] = None
) -> str:
    """
    Perform a grep search with various options.

    Args:
        pattern (str): The regular expression pattern to search for.
        path (Optional[str]): File or directory to search in.
        glob (Optional[str]): Glob pattern to filter files.
        type (Optional[str]): File type to search (e.g., 'f' for files, 'd' for directories).
        output_mode (Optional[str]): "content", "files_with_matches", or "count".
        i (Optional[bool]): Case insensitive search.
        n (Optional[bool]): Show line numbers.
        B (Optional[int]): Lines to show before each match.
        A (Optional[int]): Lines to show after each match.
        C (Optional[int]): Lines to show before and after each match.
        head_limit (Optional[int]): Limit output to first N lines/entries.
        multiline (Optional[bool]): Enable multiline mode.

    Returns:
        str: The grep command output.
"""
    print("Running grep with pattern =", pattern, "in", path or "current directory")
    command = ["grep", shlex.quote(pattern)]

    if path:
        command.append(shlex.quote(path))
    if glob:
        command.extend(["-g", shlex.quote(glob)])
    if type:
        command.extend(["-t", shlex.quote(type)])
    if output_mode == "files_with_matches":
        command.append("-l")
    elif output_mode == "count":
        command.append("-c")
    if i:
        command.append("-i")
    if n:
        command.append("-n")
    if B is not None:
        command.extend(["-B", str(B)])
    if A is not None:
        command.extend(["-A", str(A)])
    if C is not None:
        command.extend(["-C", str(C)])
    if head_limit is not None:
        command.extend(["|", "head", "-n", str(head_limit)])
    if multiline:
        command.append("--multiline")

    full_command = " ".join(command)
    
    # Execute the command directly instead of using run_shell_command to avoid circular dependency
    try:
        result = subprocess.run(
            full_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Grep command failed: {e.stderr.strip()}") from e

@tool
def edit(
        file_path: str,
        old_string: str,
        new_string: str,
        replace_all: bool = False
) -> str:
    """
    Edit a file by replacing occurrences of old_string with new_string.

    Args:
        file_path (str): The absolute path to the file to modify.
        old_string (str): The text to replace.
        new_string (str): The text to replace it with.
        replace_all (bool): Replace all occurrences if True, else only the first occurrence.

    Returns:
        str: Success message or error.
    """
    print("Running edit on file:", file_path, "replacing", old_string, "with", new_string, "replace_all =", replace_all)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(file_path, 'r') as file:
            content = file.read()

        if replace_all:
            new_content = content.replace(old_string, new_string)
        else:
            new_content = content.replace(old_string, new_string, 1)

        with open(file_path, 'w') as file:
            file.write(new_content)

        return f"Successfully edited {file_path}"
    except Exception as e:
        raise RuntimeError(f"Failed to edit file: {str(e)}") from e

@tool
def multi_edit(
        file_path: str,
        edits: List[dict]
) -> str:
    """
    Edit a file by applying multiple edit operations.

    Args:
        file_path (str): The absolute path to the file to modify.
        edits (List[dict]): List of edit operations.

    Returns:
        str: Success message or error.
    """
    print("Running multi_edit on file:", file_path, "with edits:", edits)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(file_path, 'r') as file:
            content = file.read()

        for edit in edits:
            old_string = edit.get("old_string")
            new_string = edit.get("new_string")
            replace_all = edit.get("replace_all", False)

            if old_string is None or new_string is None:
                continue

            if replace_all:
                content = content.replace(old_string, new_string)
            else:
                content = content.replace(old_string, new_string, 1)

        with open(file_path, 'w') as file:
            file.write(content)

        return f"Successfully applied multiple edits to {file_path}"
    except Exception as e:
        raise RuntimeError(f"Failed to edit file: {str(e)}") from e
    

@tool
def read_file(
        file_path: str,
        offset: Optional[int] = None,
        limit: Optional[int] = None
) -> str:
    """
    Read a file with optional offset and limit.

    Args:
        file_path (str): The absolute path to the file to read.
        offset (Optional[int]): The line number to start reading from (0-indexed).
        limit (Optional[int]): The number of lines to read.

    Returns:
        str: The content read from the file.

    Note:
        For file formats which are usually large, like logs, consider using offset and limit to avoid reading the entire file.
    """
    print("Running read_file on:", file_path, "with offset =", offset, "and limit =", limit)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        if offset is not None:
            lines = lines[offset:]
        if limit is not None:
            lines = lines[:limit]

        return ''.join(lines)
    except Exception as e:
        raise RuntimeError(f"Failed to read file: {str(e)}") from e

shell_tools = [
    run_shell_command,
    grep,
    edit,
    multi_edit,
    read_file,
    # install_python_package_uv
]

