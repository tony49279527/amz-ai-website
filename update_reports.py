import json
import os

reports_js_path = '/Users/liangxile/.gemini/antigravity/scratch/flowaiagent-replica/data/reports/reports.js'
report_md_path = '/Users/liangxile/.gemini/antigravity/scratch/flowaiagent-replica/data/reports/report_021.md'

with open(report_md_path, 'r') as f:
    markdown_content = f.read()

# Create the new report object
new_report = {
    "id": "report_021",
    "title": "Amazon Competitor Analysis Report: Inflatable Camping Tent Market-C4.5",
    "asin": "B0C6SW6CXT",
    "marketplace": "US",
    "created_at": "2026-01-13",
    "summary": "Strategic analysis of Inflatable Camping Tent market. Main product excels in setup speed and air retention but suffers from critical door gap flaw. Urgent redesign recommended.",
    "category": "Sports & Outdoors",
    "markdown_path": "data/reports/report_021.md",
    "cover_image": "assets/images/thumbnails/inflatable_tent.png",
    "content": markdown_content
}

# Read the existing reports.js
with open(reports_js_path, 'r') as f:
    js_content = f.read()

start_marker = "window.reportsData ="
if start_marker not in js_content:
    print("Error: Could not find start marker")
    exit(1)

# Try to extract JSON part
try:
    # Remove user-variable declaration
    json_candidate = js_content.split(start_marker, 1)[1].strip()
    if json_candidate.endswith(';'):
        json_candidate = json_candidate[:-1]
    
    data = json.loads(json_candidate)
    
    # Check if report already exists to avoid duplicates
    existing_ids = [r['id'] for r in data]
    if new_report['id'] in existing_ids:
        print(f"Report {new_report['id']} already exists. Updating it.")
        # Update existing
        for i, r in enumerate(data):
            if r['id'] == new_report['id']:
                data[i] = new_report
                break
    else:
        print(f"Appending new report {new_report['id']}")
        data.append(new_report)
        
    new_js_content = "window.reportsData = " + json.dumps(data, indent=2) + ";"
    
    with open(reports_js_path, 'w') as f:
        f.write(new_js_content)
    print("Success via JSON parse")
    
except Exception as e:
    print(f"JSON Parse failed: {e}")
    # Fallback to manual string manipulation if strict JSON fails (e.g. trailing commas in JS)
    
    # Remove the last closing bracket and append
    last_bracket = js_content.rfind(']')
    if last_bracket == -1:
         print("Validation failed: No closing bracket found")
         exit(1)
    
    new_entry_str = json.dumps(new_report, indent=2)
    
    # Prepare insertion
    # We assume the list ends like `...}` or `...},` before the `]`
    # We will add a comma just in case, or rely on previous line check?
    # Safest is to check char before `]` ignoring whitespace.
    
    # Simplified approach: Append to list
    prefix = js_content[:last_bracket]
    suffix = js_content[last_bracket:]
    
    # Check if we need a preceding comma
    # Look backwards from last_bracket for non-whitespace
    ptr = last_bracket - 1
    while ptr >= 0 and prefix[ptr].isspace():
        ptr -= 1
        
    needs_comma = False
    if ptr >= 0 and prefix[ptr] != ',' and prefix[ptr] != '[':
        needs_comma = True
    
    insertion = ""
    if needs_comma:
        insertion += ","
    
    insertion += "\n" + new_entry_str + "\n"
    
    final_content = prefix + insertion + suffix
    
    with open(reports_js_path, 'w') as f:
        f.write(final_content)
    print("Success via String Manipulation")
