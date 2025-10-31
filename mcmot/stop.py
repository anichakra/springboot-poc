import logging
import os
import psutil  # Add 'psutil' for process validation (install with pip if not available)

from framework.utils.logging_utils import setup_logging

setup_logging("dev")
logger = logging.getLogger("application")

def stop_processes_from_pid_files(pid_directory="./pids"):
    """
    Stops processes specified in PID files contained within a directory and removes the
    corresponding PID files after termination. The function attempts to gracefully terminate
    each process, forcing termination if necessary, and logs the status of each operation.

    Parameters:
    pid_directory: str
        The directory containing `.pid` files. Each file should contain the PID of a running process.
        Defaults to "./pids".

    Raises:
    ValueError
        Raised if a `.pid` file contains invalid PID or corrupted data.
    FileNotFoundError
        Raised if a `.pid` file cannot be found during the operation.
    Exception
        Raised if an unexpected error occurs while handling a PID file.

    """
    if not os.path.exists(pid_directory):
        logger.debug(f"The PID directory '{pid_directory}' does not exist. Nothing to stop.")
        return

    # Get a list of all `.pid` files
    pid_files = [f for f in os.listdir(pid_directory) if f.endswith(".pid")]
    if not pid_files:
        logger.debug(f"No PID files found in '{pid_directory}'. Nothing to stop.")
        return

    # Iterate over all PID files
    for pid_file in pid_files:
        try:
            # Read the PID
            pid_file_path = os.path.join(pid_directory, pid_file)
            with open(pid_file_path, "r") as file:
                pid = int(file.read().strip())

            # Validate PID using psutil to ensure it is a running process
            if psutil.pid_exists(pid):
                try:
                    psutil.Process(pid).terminate()  # Send SIGTERM
                    psutil.Process(pid).wait(timeout=5)  # Wait for termination
                    logger.debug(f"Successfully terminated process with PID: {pid} (from {pid_file}).")
                except psutil.TimeoutExpired:
                    psutil.Process(pid).kill()  # Force termination with SIGKILL if grace period fails
                    logger.warning(f"Process with PID {pid} (from {pid_file}) terminated forcefully.")
                except Exception as ex:
                    logger.error(f"Failed to terminate process with PID {pid} (from {pid_file}): {ex}")
                logger.debug(f"Terminated process with PID: {pid} (from {pid_file}).")
            else:
                logger.debug(f"PID {pid} (from {pid_file}) does not exist. Skipping termination.")

            # Remove the PID file after attempting termination
            os.remove(pid_file_path)
            logger.debug(f"Removed PID file: {pid_file}")

        except ValueError:  # Handle invalid PID values
            logger.warning(f"Invalid PID or corrupted data found in {pid_file}. Skipping...")
        except FileNotFoundError:  # Handle missing PID file
            logger.warning(f"PID file {pid_file} no longer exists. Skipping...")
        except Exception as e:  # Catch unexpected exceptions
            logger.error(f"Unexpected error handling PID file '{pid_file}': {e}")

    logger.debug("All processes from PID files have been stopped.")


def stop_matching_processes(process_name_keywords):
    """
    Stops all running processes that match specified keywords in their command-line arguments.

    This function iterates through currently running processes to identify those whose command-line
    arguments match any of the provided keywords. It attempts to terminate each matching process
    gracefully by first sending a termination signal. If the process does not terminate within the
    grace period, it forcefully kills the process. It also verifies that the process has been
    successfully stopped and logs the outcome.

    Parameters:
        process_name_keywords (List[str]): A list of keywords to search for in the command-line
        arguments of running processes.

    Raises:
        None
    """
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = " ".join(proc.info['cmdline'] or [])
            if any(keyword in cmdline for keyword in process_name_keywords):
                logger.debug(f"Attempting to terminate process (PID {proc.pid}) matching: {cmdline}")

                # grace period: Try to terminate gracefully first
                try:
                    proc.terminate()
                    proc.wait(timeout=5)  # Wait to confirm termination
                    logger.debug(f"Graceful termination succeeded for process (PID {proc.pid}).")
                except psutil.TimeoutExpired:
                    logger.warning(f"Grace period exceeded for process (PID {proc.pid}). Forcing termination...")
                    proc.kill()  # Forcefully kill the process
                except Exception as ex:
                    logger.error(f"Error during forceful termination of process (PID {proc.pid}): {ex}")

                # Double-check if the process still exists
                if psutil.pid_exists(proc.pid):  # Double-check before reporting
                    logger.error(f"Process (PID {proc.pid}) is still running after kill! Check manually.")
                else:
                    logger.debug(f"Confirmed process (PID {proc.pid}) has stopped.")

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            logger.debug(f"Process (PID {proc.pid}) no longer exists or cannot be accessed.")
        except Exception as e:
            logger.error(f"Error stopping process (PID {proc.pid}): {e}")

if __name__ == "__main__":
    # Stop processes tracked in PID files
    stop_processes_from_pid_files(pid_directory="./pids")

    # Stop processes matching certain names (fallback)
    process_keywords = ["_init.py"]
    stop_matching_processes(process_keywords)
