import json
import logging
import os
import subprocess

from framework.utils.config_utils import read_config
from framework.utils.logging_utils import setup_logging

setup_logging("dev")
logger = logging.getLogger("application")

def stop_all_processes(pids):
    """
    Stops all processes specified by a list of process IDs (PIDs).

    This function sends a SIGKILL signal to each PID provided to forcefully
    terminate the corresponding running processes, if they exist. If a process
    does not exist or is already terminated, it handles the exception silently.
    It also logs the termination of processes and indicates once all provided
    processes have been stopped.

    Parameters:
        pids (list[int]): A list of process IDs to be terminated.

    Raises:
        None

    Returns:
        None
    """
    for pid in pids:
        try:
            os.kill(pid, 9)  # Send SIGKILL
            logger.debug(f"Terminated process with PID: {pid}")
        except ProcessLookupError:
            pass  # Process already terminated
    logger.debug("All processes have been stopped.")


def start_observability_process(module_name, virtual_env_path):
    """
    Starts the observability process for a given module by executing a predefined Python script
    within the specified virtual environment. The process is logged, and its PID is stored
    for monitoring purposes. This function ensures the necessary directory structures exist
    before initiating the process.

    Parameters:
        module_name (str): Name of the module for which to start observability.
        virtual_env_path (str): Path to the virtual environment to be used.

    Raises:
        Exception: If there is an error while attempting to start the observability process.
    """
    # Ensure necessary directories exist
    os.makedirs("pids", exist_ok=True)  # Ensure 'pids' directory exists

    observability_config_path = f"config/observability/{module_name}-config.json"
    observability_log = f"logs/observability_{module_name}.log"
    pid_file = os.path.join("pids", f"observability_{module_name}.pid")  # Updated path

    cmd = f"PYTHONPATH=. {virtual_env_path}/bin/python observability/observability_init.py {observability_config_path}"

    try:
        # Start the process and capture its PID
        with open(observability_log, "w") as log:
            process = subprocess.Popen(cmd, stdout=log, stderr=log, shell=True, executable="/bin/bash")

        # Ensure the process started successfully
        if process and process.pid:
            with open(pid_file, "w") as pid_f:
                pid_f.write(str(process.pid))
            logger.debug(
                f"Started observability for module '{module_name}' (PID: {process.pid}). Logs: {observability_log}")
        else:
            logger.error(f"Failed to start observability for module '{module_name}'. Command: {cmd}")

    except Exception as e:
        logger.error(f"Error starting observability for module '{module_name}': {e}")
        raise


def start_module_process(module_name, config, instance_index, virtual_env_path):
    """
    Starts a module process in a specified virtual environment while ensuring logging
    and process ID tracking. This function manages directory creation for logs and PIDs,
    prepares the required command based on the provided configuration, and executes
    the process in a subprocess. It records the process ID into a file and redirects
    output to a log file. Handles configurations specified either as a file path or
    a JSON object.

    Parameters:
        module_name (str): The name of the module to be executed.
        config (Union[str, dict]): The module configuration, either as a file path (str)
            or as a JSON object (dict).
        instance_index (int): The index of the module instance being started.
        virtual_env_path (str): The path to the Python virtual environment where
            the module should be executed.

    Returns:
        Optional[int]: The process ID (PID) of the started module instance, or None if
            the process could not be started.

    Raises:
        ValueError: If the provided `config` is neither a string nor a dictionary.
        Exception: For other errors encountered during subprocess creation or execution.
    """
    # Ensure necessary directories exist
    os.makedirs("pids", exist_ok=True)  # Create pids directory
    os.makedirs("logs", exist_ok=True)  # Create logs directory

    log_file = f"logs/{module_name}_{instance_index}.log"
    pid_file = os.path.join("pids", f"{module_name}_{instance_index}.pid")

    # Prepare the command based on config type
    if isinstance(config, str):  # Config is a file path
        cmd = f"PYTHONPATH=. {virtual_env_path}/bin/python {module_name}/{module_name}_init.py {config}"
    elif isinstance(config, dict):  # Config is JSON
        cmd = f"PYTHONPATH=. {virtual_env_path}/bin/python {module_name}/{module_name}_init.py '{json.dumps(config)}'"
    else:  # Handle invalid config
        raise ValueError("Invalid config type. Must be a string (file path) or a JSON object.")

    try:
        # Launch process and capture PID
        with open(log_file, "w") as log:
            process = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, shell=True, executable="/bin/bash")

        # Write the PID to the correct `.pid` file
        if process.pid:
            with open(pid_file, "w") as pid_f:
                pid_f.write(str(process.pid))
            logger.debug(
                f"Started module '{module_name}' instance {instance_index} (PID: {process.pid}). Logs: {log_file}")
            return process.pid
        else:
            logger.error(f"Failed to start module '{module_name}' instance {instance_index}. Command: {cmd}")
            return None

    except Exception as e:
        logger.error(f"Error starting module '{module_name}' instance {instance_index}: {e}")
        raise

def main():
    """
    Executes the main workflow to read configuration, start required module
    processes, handle observability processes, and manage replication. Handles
    unexpected exceptions by cleaning up started processes to ensure no orphaned
    processes remain.

    Raises:
        Exception: Raised during process startup or any unexpected issues during
        execution.

    Returns:
        None
    """
    logger.debug("Reading configuration...")

    # Load JSON input (this part should be adjusted based on your implementation)
    try:
        config = read_config()  # Replace with your JSON loading function
        virtual_env_path = os.environ.get("VIRTUAL_ENV", ".venv")  # Get virtual environment from runtime or default
    except ValueError as e:
        logger.debug(f"Error reading configuration: {e}")
        return

    # To track all processes for potential cleanup
    process_pids = []

    try:
        # A set to track whether observability has already been started for a module type
        processed_observability_modules = set()

        # Start processes for each module
        for module in config:
            module_name = module["name"]
            replication_factor = module.get("replication-factor", 1)  # Default replication to 1
            module_observability = module.get("observability", False)  # Default observability to False
            module_config = module["config"]  # Config: file path as string or inline JSON

            # Start one observability process per module type if required
            if module_observability and module_name not in processed_observability_modules:
                observability_pid = start_observability_process(module_name, virtual_env_path)
                process_pids.append(observability_pid)
                processed_observability_modules.add(module_name)

            # Start the replicated instances of the module
            for instance_index in range(1, replication_factor + 1):
                module_instance_pid = start_module_process(module_name, module_config, instance_index,virtual_env_path)
                process_pids.append(module_instance_pid)

        # Confirm successful startup
        logger.debug("All processes started successfully.")

    except Exception as e:
        # Stop all started processes in case of an error
        logger.debug(f"Error during startup: {e}. Stopping all processes...")
        stop_all_processes(process_pids)
        return

    # Exit Program
    logger.debug("Exiting start.py. All processes are running in the background.")


if __name__ == "__main__":
    main()
