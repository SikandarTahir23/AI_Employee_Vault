import os
import time

# Paths
user_profile = os.environ['USERPROFILE']
path_to_watch = r"C:\Users\Sikandar Tahir\OneDrive\Desktop"
vault_path = r"C:\Users\Sikandar Tahir\OneDrive\Desktop\AI_Employee_Vault"

def read_and_sort(file_name, content):
    content_lower = content.lower()
    
    # Logic to decide folder
    if "task" in content_lower or "todo" in content_lower:
        target_folder = "Tasks"
    else:
        target_folder = "Readings"
        
    file_path = os.path.join(vault_path, target_folder, f"{file_name}.md")
    
    with open(file_path, "w", encoding='utf-8') as f:
        f.write(f"# Processed by AI Employee\n")
        f.write(f"- **Source:** {file_name}\n")
        f.write(f"- **Category:** {target_folder}\n")
        f.write(f"- **Time:** {time.ctime()}\n\n")
        f.write(f"## Content:\n{content}")
    
    return target_folder

try:
    print("--- AI Smart Sorter Starting ---")
    before = dict([(f, None) for f in os.listdir(path_to_watch)])
    print("STATUS: ACTIVE! Sorting files into Readings/Tasks...")
    
    while True:
        time.sleep(5)
        after = dict([(f, None) for f in os.listdir(path_to_watch)])
        added = [f for f in after if not f in before]
        
        for file_name in added:
            if file_name.endswith('.txt'):
                full_path = os.path.join(path_to_watch, file_name)
                content = None
                for attempt in range(5):
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        break
                    except PermissionError:
                        print(f"⏳ '{file_name}' is locked, retrying ({attempt + 1}/5)...")
                        time.sleep(2)

                if content is not None:
                    folder = read_and_sort(file_name, content)
                    print(f"✅ Sorted '{file_name}' into '{folder}' folder.")
                else:
                    print(f"❌ Could not read '{file_name}' after 5 attempts — file may still be in use.")
            
        before = after
except Exception as e:
    print(f"SYSTEM ERROR: {e}")