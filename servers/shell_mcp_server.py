import logging
import subprocess
from mcp.server.fastmcp import FastMCP

# Setup logging
logging.basicConfig(
    format='%(levelname)s %(asctime)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('shell_mcp_server')

# Create the MCP server
mcp = FastMCP('ShellCommandExecutor')

# DISCLAIMER: This is purely for demonstration purposes and NOT to be used in a production environment
@mcp.tool(name="execute_shell_command")
def execute_shell_command(command: str) -> str:
    """
    Executes a real shell command in the user's Mac OS environment and returns the actual output (stdout and stderr).

    Use this tool to perform any task that requires terminal access.

    This is the ONLY way to run shell commands. Do not describe or suggest commands — use this tool to execute them directly.

    Think and reason in bash. Use the tool as many times as needed to fully complete the user’s request.
    """
    logger.info(f'Executing shell command: {command}')
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=True,
            executable="/bin/bash",
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        logger.info(f'Command output: {stdout}')
        if stderr:
            logger.warning(f'Command stderr: {stderr}')
            return f"🔻 STDERR:\n{stderr}"

        return stdout or "Command executed successfully"


    except subprocess.CalledProcessError as e:
        stdout = e.stdout.strip() if e.stdout else ""
        stderr = e.stderr.strip() if e.stderr else ""

        error_msg = f"⚠️ The shell command failed (exit code {e.returncode})."

        if stderr:
            error_msg += f"\n🔻 STDERR:\n{stderr}"
        if stdout:
            error_msg += f"\n🔸 STDOUT:\n{stdout}"

        return error_msg

if __name__ == '__main__':
    logger.info('Starting the ShellCommandExecutor MCP server...')
    mcp.run(transport='stdio')