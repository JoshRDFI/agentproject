import pkg_resources
import sys

def check_crewai_version():
    """Check if the installed crewai version is compatible."""
    try:
        crewai_version = pkg_resources.get_distribution("crewai").version
        print(f"Installed crewai version: {crewai_version}")
        
        # For this project, we're adapting to work with version 0.126.0
        # So we'll return True regardless of version, but print a notice
        if crewai_version != "0.126.0":
            print(f"Note: This project is adapted to work with CrewAI version 0.126.0.")
            print(f"You're using version {crewai_version}, which may cause compatibility issues.")
        
        return True
    except pkg_resources.DistributionNotFound:
        print("Error: crewai package is not installed.")
        print("Please install it with: pip install crewai")
        return False

if __name__ == "__main__":
    if not check_crewai_version():
        sys.exit(1)