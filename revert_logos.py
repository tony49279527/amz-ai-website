import os

def revert_logos(root_dir):
    # The new tag we added
    new_tag_start = '<img src="'
    new_tag_end = 'class="logo-icon">'
    
    # The old SVG content to restore
    old_svg_block = '''<!-- SVG Logo placeholder -->
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="2" y="2" width="20" height="20" rx="6" fill="#2563eb" />
                    <path d="M7 12H17M7 8H17M7 16H13" stroke="white" stroke-width="2" stroke-linecap="round" />
                </svg>'''

    encoded_count = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if '.git' in dirpath:
            continue
            
        for filename in filenames:
            if filename.endswith('.html'):
                file_path = os.path.join(dirpath, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if the file contains the new logo tag AND "Amz AI Agent Logo" alt text
                    if 'alt="Amz AI Agent Logo"' in content and 'class="logo-icon"' in content:
                        
                        # We need to find the <img ... class="logo-icon"> tag and replace it.
                        # Since paths are relative, the src attribute varies.
                        # Simple regex-like search
                        
                        start_idx = content.find('<img src=')
                        # Find the specific one for the logo
                        while start_idx != -1:
                            end_idx = content.find('class="logo-icon">', start_idx)
                            if end_idx != -1:
                                full_end_idx = end_idx + len('class="logo-icon">')
                                tag_content = content[start_idx:full_end_idx]
                                
                                if 'alt="Amz AI Agent Logo"' in tag_content:
                                    # Found it. Replace with old block.
                                    # Need to check indentation? The old block assumes some indentation.
                                    # Let's just blindly replace for now, HTML is forgiving.
                                    
                                    new_content = content[:start_idx] + old_svg_block + content[full_end_idx:]
                                    
                                    print(f"Reverting logo in {file_path}")
                                    with open(file_path, 'w', encoding='utf-8') as f:
                                        f.write(new_content)
                                    encoded_count += 1
                                    break # Assume one logo per file
                            
                            start_idx = content.find('<img src=', start_idx + 1)
                        
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    print(f"Total files reverted: {encoded_count}")

if __name__ == "__main__":
    revert_logos('/Users/liangxile/.gemini/antigravity/scratch/flowaiagent-replica')
