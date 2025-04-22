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
    Executes a shell command directly in the user's local environment and returns the output.
    
    Use this tool whenever the user asks for information that could be retrieved by running a terminal or shell command,
    such as 'what's in my current directory', 'list all files', 'check disk usage', etc.

    Do NOT generate code. Call this tool instead.
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

        return stdout or "[✅ Command completed successfully but produced no output.]"


    except subprocess.CalledProcessError as e:
        stdout = e.stdout.strip() if e.stdout else ""
        stderr = e.stderr.strip() if e.stderr else ""

        logger.error(f"Shell command failed. Code: {e.returncode}")
        if stdout:
            logger.error(f"STDOUT: {stdout}")
        if stderr:
            logger.error(f"STDERR: {stderr}")

        error_msg = f"⚠️ The shell command failed (exit code {e.returncode})."

        if stderr:
            error_msg += f"\n🔻 STDERR:\n{stderr}"
        if stdout:
            error_msg += f"\n🔸 STDOUT:\n{stdout}"

        return error_msg

if __name__ == '__main__':
    logger.info('Starting the ShellCommandExecutor MCP server...')
    mcp.run(transport='stdio')