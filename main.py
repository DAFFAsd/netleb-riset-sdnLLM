from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import paramiko

app = FastAPI()

HOST = "192.168.56.101"   # IP Mininet VM
USER = "mininet"
PASSWORD = "mininet"
SSH_TIMEOUT = 10  # seconds
CMD_TIMEOUT = 30  # seconds

class CommandRequest(BaseModel):
    cmd: str = Field(..., min_length=1, description="Command to execute on remote server")

def ssh_run(cmd: str):
    client = None
    try:
        client = paramiko.SSHClient()
        # WARNING: AutoAddPolicy is not secure for production
        # Consider using: client.load_system_host_keys() or client.load_host_keys('known_hosts')
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect with timeout
        client.connect(
            HOST, 
            username=USER, 
            password=PASSWORD,
            timeout=SSH_TIMEOUT,
            banner_timeout=SSH_TIMEOUT
        )
        
        # Execute command with timeout
        stdin, stdout, stderr = client.exec_command(cmd, timeout=CMD_TIMEOUT)
        
        # Read output with proper error handling
        stdout_data = stdout.read().decode('utf-8', errors='replace')
        stderr_data = stderr.read().decode('utf-8', errors='replace')
        exit_status = stdout.channel.recv_exit_status()
        
        result = {
            "stdout": stdout_data,
            "stderr": stderr_data,
            "exit_status": exit_status,
            "success": exit_status == 0
        }
        
        return result
        
    except paramiko.AuthenticationException:
        raise HTTPException(status_code=401, detail="Authentication failed")
    except paramiko.SSHException as e:
        raise HTTPException(status_code=500, detail=f"SSH error: {str(e)}")
    except TimeoutError:
        raise HTTPException(status_code=408, detail="Connection timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        # Ensure connection is always closed
        if client:
            client.close()

@app.post("/run")
def run_command(request: CommandRequest):
    """
    Execute a command on the remote Mininet VM via SSH
    """
    return ssh_run(request.cmd)
