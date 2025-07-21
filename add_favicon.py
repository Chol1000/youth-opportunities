import os
import re

def add_favicon_to_html_files(directory_path):
    """
    Add favicon link to all HTML files in the given directory and its subdirectories
    """
    favicon_tag = '<link rel="icon" href="../../static/images/youthopps-logo.png" type="image/png">'
    login_favicon_tag = '<link rel="icon" href="../static/images/youthopps-logo.png" type="image/png">'
    
    # Walk through all directories and files
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                
                # Read the file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if favicon is already added
                if 'rel="icon"' in content:
                    print(f"Favicon already exists in {file_path}")
                    continue
                
                # Determine which favicon tag to use based on file location
                if 'user_dashboard' in file_path or 'admin_dashboard' in file_path:
                    tag_to_add = favicon_tag
                else:
                    tag_to_add = login_favicon_tag
                
                # Add favicon tag after the last link tag or before the closing head tag
                if '</head>' in content:
                    # Try to find the last link tag
                    last_link_pos = content.rfind('</link>')
                    if last_link_pos == -1:
                        last_link_pos = content.rfind('</style>')
                    
                    if last_link_pos != -1:
                        # Insert after the last link or style tag
                        insert_pos = last_link_pos + 8  # Length of '</link>' or '</style>'
                        new_content = content[:insert_pos] + '\n    ' + tag_to_add + content[insert_pos:]
                    else:
                        # Insert before closing head tag
                        head_close_pos = content.find('</head>')
                        new_content = content[:head_close_pos] + '    ' + tag_to_add + '\n' + content[head_close_pos:]
                    
                    # Write the modified content back to the file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print(f"Added favicon to {file_path}")
                else:
                    print(f"Could not find </head> tag in {file_path}")

if __name__ == "__main__":
    # Path to the templates directory
    templates_dir = os.path.join('frontend', 'templates')
    
    # Check if the directory exists
    if os.path.exists(templates_dir):
        add_favicon_to_html_files(templates_dir)
        print("Favicon added to all HTML files successfully!")
    else:
        print(f"Directory {templates_dir} does not exist!")
