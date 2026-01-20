import json
import os

def generate_reports_js():
    base_dir = '/Users/liangxile/.gemini/antigravity/scratch/flowaiagent-replica'
    index_path = os.path.join(base_dir, 'data/reports/index.json')
    output_path = os.path.join(base_dir, 'data/reports/reports.js')

    with open(index_path, 'r', encoding='utf-8') as f:
        reports = json.load(f)

    for report in reports:
        md_path = os.path.join(base_dir, report['markdown_path'])
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                report['content'] = f.read()
        except Exception as e:
            print(f"Error reading {md_path}: {e}")
            report['content'] = "# Error Loading Content"

    js_content = f"window.reportsData = {json.dumps(reports, indent=2)};"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"Generated {output_path} with {len(reports)} reports.")

if __name__ == "__main__":
    generate_reports_js()
