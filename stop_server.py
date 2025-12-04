import os
import sys

def kill_process_on_port_windows(port=8000):
    """
    Windows-specific method using netstat and taskkill
    """
    import subprocess
    
    try:
        # Find process ID using the port
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0 or not result.stdout:
            print(f"ℹ️ No process found using port {port}")
            return False
        
        # Extract PID from output
        lines = result.stdout.strip().split('\n')
        pids = set()
        
        for line in lines:
            parts = line.split()
            if len(parts) >= 5:
                pid = parts[-1]
                if pid.isdigit():
                    pids.add(pid)
        
        if not pids:
            print(f"ℹ️ No process found using port {port}")
            return False
        
        # Kill each process
        killed = False
        for pid in pids:
            print(f"🔍 Found process using port {port}:")
            print(f"   PID: {pid}")
            print(f"   Killing process...")
            
            kill_result = subprocess.run(
                f'taskkill /F /PID {pid}',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if kill_result.returncode == 0:
                print(f"✅ Process {pid} terminated successfully")
                killed = True
            else:
                print(f"⚠️ Failed to kill PID {pid}: {kill_result.stderr}")
        
        return killed
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def kill_port(port=8000):
    """Kill any process using the specified port on Windows"""
    print(f"🔍 Finding processes on port {port}...")
    
    try:
        # Find PID using netstat
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if not result.stdout.strip():
            print(f"✅ No process found on port {port}")
            return
        
        # Extract PIDs
        pids = set()
        for line in result.stdout.strip().split('\n'):
            parts = line.split()
            if len(parts) >= 5:
                pid = parts[-1]
                if pid.isdigit():
                    pids.add(pid)
        
        # Kill each PID
        for pid in pids:
            print(f"🔪 Killing process {pid}...")
            subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
        
        print(f"✅ Killed {len(pids)} process(es) on port {port}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🛑 STOP SERVER UTILITY")
    print("="*50 + "\n")
    
    if os.name == 'nt':  # Windows
        if kill_process_on_port_windows(8000):
            print("\n✅ Port 8000 is now free")
            print("You can restart the server with: python main.py\n")
        else:
            print("\n⚠️ Could not automatically kill process")
            print("\n📋 Manual Steps:")
            print("1. Press Ctrl+Shift+Esc to open Task Manager")
            print("2. Go to 'Details' tab")
            print("3. Find 'python.exe' processes")
            print("4. Right-click and 'End Task' on any Python processes")
            print("5. Run: python main.py\n")
    else:
        print("❌ This script is designed for Windows only")
        print("On Unix/Linux/Mac, use: lsof -ti:8000 | xargs kill -9\n")

    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    kill_port(port)
