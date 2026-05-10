import urllib.request
import time
import sys

def verify_live_server():
    url = "http://127.0.0.1:8000"
    max_retries = 10
    for i in range(max_retries):
        try:
            print(f"Attempt {i+1}: Connecting to {url}...")
            with urllib.request.urlopen(url) as response:
                status = response.getcode()
                content = response.read().decode('utf-8')
                
                if status == 200:
                    print("✅ Server is reachable (Status 200)")
                    
                    if "Prince Raj Kiran" in content:
                        print("✅ Content Verified: 'Prince Raj Kiran' found on page")
                    else:
                        print("❌ Content Warning: Name not found on page")
                        
                    if "Skills" in content and "Projects" in content:
                        print("✅ Sections Verified: Skills and Projects sections found")
                    else:
                        print("❌ Content Warning: Sections missing")
                        
                    return True
                else:
                    print(f"❌ Server returned status: {status}")
                    
        except urllib.error.URLError as e:
            print(f"⚠️ Connection failed: {e.reason}")
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            time.sleep(2)
            
    print("❌ Failed to connect to server after multiple attempts.")
    return False

if __name__ == "__main__":
    if verify_live_server():
        print("Verification Successful!")
    else:
        sys.exit(1)
