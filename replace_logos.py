import os

def replace_logos(root_dir):
    # Old SVG pattern
    old_svg_start = '<!-- SVG Logo placeholder -->'
    old_svg_content_sub = '<path d="M7 12H17M7 8H17M7 16H13" stroke="white" stroke-width="2" stroke-linecap="round" />'
    
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
                    
                    if old_svg_content_sub in content:
                        # Determine relative path to assets
                        rel_path = os.path.relpath(os.path.join(root_dir, 'assets/images/logo.svg'), dirpath)
                        
                        # New IMG tag
                        new_img_tag = f'<img src="{rel_path}" alt="Amz AI Agent Logo" width="32" height="32" class="logo-icon">'
                        
                        # We need to replace the entire SVG block. 
                        # Since it's multi-line, we can try a regex or a simpler block replacement if the formatting is consistent.
                        # The formatting in index.html was:
                        # <!-- SVG Logo placeholder -->
                        # <svg ...>
                        #     <rect ... />
                        #     <path ... />
                        # </svg>
                        
                        # Let's try to find the start and end of the SVG block
                        start_marker = '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
                        end_marker = '</svg>'
                        
                        if start_marker in content:
                            start_idx = content.find(start_marker)
                            end_idx = content.find(end_marker, start_idx)
                            
                            if end_idx != -1:
                                full_end_idx = end_idx + len(end_marker)
                                
                                # Check for comment before it
                                comment = '<!-- SVG Logo placeholder -->'
                                comment_idx = content.rfind(comment, 0, start_idx)
                                
                                replace_start = start_idx
                                if comment_idx != -1 and content[comment_idx:start_idx].strip() == '':
                                    replace_start = comment_idx
                                
                                # Construct new content
                                new_content = content[:replace_start] + new_img_tag + content[full_end_idx:]
                                
                                print(f"Updating logo in {file_path}")
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(new_content)
                                encoded_count += 1
                        
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    print(f"Total files updated: {encoded_count}")

if __name__ == "__main__":
    replace_logos('/Users/liangxile/.gemini/antigravity/scratch/flowaiagent-replica')
