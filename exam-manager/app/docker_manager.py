"""
Docker container management for student environments
"""
import docker
import os
import secrets
import asyncio
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Port range for student Jupyter instances
PORT_START = 8900
PORT_END = 8999
used_ports = set()


def get_docker_client():
    """Get Docker client (works from inside container)"""
    try:
        # Use from_env which automatically detects the socket
        client = docker.from_env()
        client.ping()
        logger.info("Successfully connected to Docker daemon")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Docker: {e}")
        raise Exception(f"Cannot connect to Docker daemon: {e}")


def get_available_port() -> int:
    """Get an available port for Jupyter"""
    for port in range(PORT_START, PORT_END):
        if port not in used_ports:
            used_ports.add(port)
            return port
    raise Exception("No available ports for student containers")


def release_port(port: int):
    """Release a port back to the pool"""
    used_ports.discard(port)


async def create_student_container(
    student_id: str,
    exam_name: str,
    num_questions: int,
    requirements_file: Optional[str] = None,
    materials_folder: Optional[str] = None,
    template_folder: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create and start a student container with JupyterLab
    """
    client = get_docker_client()
    
    # Generate unique token and get port
    jupyter_token = secrets.token_hex(16)
    jupyter_port = get_available_port()
    
    # Base paths - use Windows path format for Docker Desktop
    # HOST_DATA_PATH should be like: C:/Users/SERGIO/Documents/docker_ipd/data
    host_base_path = os.getenv("HOST_DATA_PATH", "C:/Users/SERGIO/Documents/docker_ipd/data")
    
    # Container name - sanitize student_id
    safe_student_id = student_id.lower().replace(' ', '-').replace('/', '-')
    container_name = f"exambox-student-{safe_student_id}"
    
    # Remove existing container if any
    try:
        existing = client.containers.get(container_name)
        existing.remove(force=True)
        logger.info(f"Removed existing container: {container_name}")
    except docker.errors.NotFound:
        pass
    
    # Environment variables for the student container
    environment = {
        "STUDENT_ID": student_id,
        "EXAM_NAME": exam_name,
        "NUM_QUESTIONS": str(num_questions),
        "JUPYTER_TOKEN": jupyter_token,
        "EXAM_MANAGER_URL": os.getenv("EXAM_MANAGER_URL", "http://exam-manager:8000"),
    }
    
    # Volume mounts using host paths
    volumes = {
        f"{host_base_path}/work/{safe_student_id}": {"bind": "/home/student/work", "mode": "rw"},
    }
    
    # Mount materials read-only if specified
    if materials_folder:
        volumes[f"{host_base_path}/materials/{materials_folder}"] = {
            "bind": "/home/student/materials",
            "mode": "ro"
        }
    
    # Mount exam template
    if template_folder:
        volumes[f"{host_base_path}/exams/{template_folder}"] = {
            "bind": "/home/student/exam_template",
            "mode": "ro"
        }
    
    try:
        # Create the container
        container = client.containers.run(
            "exambox-student:latest",
            name=container_name,
            detach=True,
            environment=environment,
            ports={"8888/tcp": jupyter_port},
            volumes=volumes,
            network="docker_ipd_exam_network",
            mem_limit="1g",
            cpu_period=100000,
            cpu_quota=50000,  # 50% CPU limit
            restart_policy={"Name": "unless-stopped"},
        )
        
        logger.info(f"Created container {container_name} on port {jupyter_port}")
        
        return {
            "container_id": container.id,
            "container_name": container_name,
            "jupyter_port": jupyter_port,
            "jupyter_token": jupyter_token,
        }
        
    except Exception as e:
        release_port(jupyter_port)
        logger.error(f"Failed to create container: {e}")
        raise


async def stop_student_container(container_id: str, jupyter_port: int):
    """Stop and remove a student container"""
    client = get_docker_client()
    
    try:
        container = client.containers.get(container_id)
        container.stop(timeout=10)
        container.remove()
        release_port(jupyter_port)
        logger.info(f"Stopped and removed container: {container_id}")
    except docker.errors.NotFound:
        logger.warning(f"Container not found: {container_id}")
    except Exception as e:
        logger.error(f"Failed to stop container: {e}")


async def get_container_status(container_id: str) -> Optional[str]:
    """Get the status of a container"""
    client = get_docker_client()
    
    try:
        container = client.containers.get(container_id)
        return container.status
    except docker.errors.NotFound:
        return None
    except Exception as e:
        logger.error(f"Failed to get container status: {e}")
        return None


async def unlock_question_in_container(
    student_id: str,
    question_number: int,
    template_folder: str
):
    """
    Copy a question to the student's workspace
    This is done by copying from the exam template
    """
    import shutil
    
    # Use the internal container path for file operations
    base_path = os.getenv("DATA_PATH", "/app/data")
    safe_student_id = student_id.lower().replace(' ', '-').replace('/', '-')
    source = f"{base_path}/exams/{template_folder}/Q{question_number}"
    dest = f"{base_path}/work/{safe_student_id}/Q{question_number}"
    
    if os.path.exists(source) and not os.path.exists(dest):
        shutil.copytree(source, dest)
        logger.info(f"Unlocked Q{question_number} for student {student_id}")
        return True
    return False
