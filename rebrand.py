import os

def rebrand_files(root_dir):
    # Replacements map
    replacements = {
        "FlowAIAgent": "Amz AI Agent",
        "flowaiagent.com": "amzaiagent.com"
    }
    
    extensions = ['.html', '.js', '.json', '.xml', '.txt', '.py']
    
    encoded_count = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip hidden directories and brain/scratch if needed, but we are in scratch
        if '.git' in dirpath:
            continue
            
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                file_path = os.path.join(dirpath, filename)
                
                # Skip the script itself if it's in the dir
                if filename == 'rebrand.py':
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content = content
                    for old, new in replacements.items():
                        new_content = new_content.replace(old, new)
                    
                    if new_content != content:
                        print(f"Updating {file_path}")
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        encoded_count += 1
                        
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    print(f"Total files updated: {encoded_count}")

if __name__ == "__main__":
    rebrand_files('/Users/liangxile/.gemini/antigravity/scratch/flowaiagent-replica')
