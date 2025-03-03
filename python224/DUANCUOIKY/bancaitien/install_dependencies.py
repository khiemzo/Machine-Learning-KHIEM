import subprocess
import sys
import os

def install_dependencies():
    """
    Install all libraries from requirements.txt file
    with longer timeout to avoid timeout errors.
    """
    print("Starting installation of libraries...")
    
    # List of libraries from requirements.txt
    with open('requirements.txt', 'r') as f:
        packages = [line.strip() for line in f.readlines() if line.strip()]
    
    # List of successfully installed libraries
    installed = []
    # List of failed installations
    failed = []
    
    for package in packages:
        print(f"\nInstalling {package}...")
        try:
            # Use subprocess to install package with longer timeout (300 seconds)
            if package.lower() == 'tkinter':
                print("tkinter is usually included with Python. Skipping.")
                installed.append(package)
                continue
                
            cmd = [sys.executable, "-m", "pip", "install", package, "--default-timeout=300"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Successfully installed: {package}")
                installed.append(package)
            else:
                print(f"Could not install {package}. Error: {result.stderr}")
                failed.append(package)
                
        except Exception as e:
            print(f"Error while installing {package}: {str(e)}")
            failed.append(package)
    
    # Show summary
    print("\n=== INSTALLATION RESULTS ===")
    print(f"Total libraries: {len(packages)}")
    print(f"Successfully installed: {len(installed)}")
    print(f"Failed installations: {len(failed)}")
    
    if failed:
        print("\nList of failed installations:")
        for pkg in failed:
            print(f"- {pkg}")
        
        print("\nTroubleshooting suggestions:")
        print("1. Try manual installation: pip install <library_name> --default-timeout=300")
        print("2. Try using a different mirror: pip install <library_name> --index-url https://mirrors.aliyun.com/pypi/simple/")
        print("3. If using conda, try: conda install <library_name>")
    
    return installed, failed

if __name__ == "__main__":
    install_dependencies()
    
    # Keep console open to see results
    input("\nPress Enter to exit...")
