import gzip
import re
import sys
import os

# Mapping VCF "Number" spec to descriptions for tooltips
NUMBER_TOOLTIPS = {
    "0": "0: Field is a Flag (no values follow, its presence means true).",
    "1": "1: Exactly one value is expected.",
    "A": "A: One value per ALTERNATE allele.",
    "R": "R: One value per allele, including the REFERENCE allele.",
    "G": "G: One value for each possible genotype.",
    ".": ".: Unknown, unbounded, or variable number of values."
}

def detect_caller(filename):
    """Checks if the filename contains specific caller names (case-sensitive)."""
    # Define the callers you want to check for
    callers = ["mutect2", "strelka2", "vardict", "manta", "lancet", "consensus"]
    
    # If we want to make it case-insensitive:
    # filename_lower = filename.lower()
    
    for caller in callers:
        if caller in filename:
            # Return proper capitalization based on matches
            if caller == "mutect2": return "mutect2"
            if caller == "strelka2": return "strelka2"
            if caller == "vardict": return "vardict"
            if caller == "manta": return "manta"
            if caller == "lancet": return "lancet"
            if caller == "consensus": return "consensus"
            
    return "Generic"

def parse_vcf_header(vcf_path):
    info_fields = []
    format_fields = []
    
    info_regex = re.compile(r'^##INFO=<ID=([^,]+),Number=([^,]+),Type=([^,]+),Description="(.*)"')
    format_regex = re.compile(r'^##FORMAT=<ID=([^,]+),Number=([^,]+),Type=([^,]+),Description="(.*)"')
    
    open_func = gzip.open if vcf_path.endswith('.gz') else open
    mode = 'rt' if vcf_path.endswith('.gz') else 'r'
    
    with open_func(vcf_path, mode) as f:
        for line in f:
            if line.startswith('#CHROM'):
                break
            
            info_match = info_regex.match(line)
            if info_match:
                info_fields.append(info_match.groups())
                
            format_match = format_regex.match(line)
            if format_match:
                format_fields.append(format_match.groups())
                
    return info_fields, format_fields

def get_number_cell(number_val):
    """Generates an HTML cell with a CSS tooltip if a definition exists."""
    tooltip_text = NUMBER_TOOLTIPS.get(number_val)
    if not tooltip_text and number_val.isdigit():
        tooltip_text = f"{number_val}: Exactly {number_val} fixed values expected."
        
    if tooltip_text:
        return f'<td><span class="tooltip-container" data-tooltip="{tooltip_text}">{number_val}</span></td>'
    return f'<td>{number_val}</td>'

def generate_html(info_fields, format_fields, caller_name, output_html_path):
    # Dynamic title string incorporating the caller
    display_title = f"{caller_name} VCF File Legend"
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{display_title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
        h1 {{ color: #111; margin-bottom: 25px; }}
        h2 {{ border-bottom: 2px solid #0056b3; padding-bottom: 5px; color: #0056b3; margin-top: 40px; }}
        
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; table-layout: fixed; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background-color: #f4f4f4; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        code {{ background-color: #eef; padding: 2px 4px; border-radius: 3px; font-family: monospace; }}
        
        th:nth-child(1), td:nth-child(1) {{ width: 25%; }}
        th:nth-child(2), td:nth-child(2) {{ width: 5%; }}
        th:nth-child(3), td:nth-child(3) {{ width: 5%; }}
        th:nth-child(4), td:nth-child(4) {{ width: 65%; }}
        
        td:nth-child(4) {{ 
            word-wrap: break-word; 
            word-break: break-word; 
            overflow-wrap: break-word; 
        }}
        
        .tooltip-container {{
            position: relative;
            border-bottom: 1px dotted #666;
            cursor: help;
            font-weight: bold;
            color: #0056b3;
        }}
        .tooltip-container::after {{
            content: attr(data-tooltip);
            position: absolute;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            background-color: #333;
            color: #fff;
            padding: 6px 10px;
            border-radius: 4px;
            white-space: nowrap;
            font-size: 13px;
            font-family: Arial, sans-serif;
            font-weight: normal;
            visibility: hidden;
            opacity: 0;
            transition: opacity 0.2s;
            z-index: 10;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .tooltip-container:hover::after {{
            visibility: visible;
            opacity: 1;
        }}
    </style>
</head>
<body>
    <h1>{display_title}</h1>
    
    <h2>INFO Fields</h2>
    <table>
        <thead>
            <tr><th>ID</th><th>Number</th><th>Type</th><th>Description</th></tr>
        </thead>
        <tbody>
"""
    for field_id, number, type_val, desc in info_fields:
        num_cell = get_number_cell(number)
        html_content += f"            <tr><td><code>{field_id}</code></td>{num_cell}<td>{type_val}</td><td>{desc}</td></tr>\n"
        
    html_content += """        </tbody>
    </table>
    
    <h2>FORMAT Fields</h2>
    <table>
        <thead>
            <tr><th>ID</th><th>Number</th><th>Type</th><th>Description</th></tr>
        </thead>
        <tbody>
"""
    for field_id, number, type_val, desc in format_fields:
        num_cell = get_number_cell(number)
        html_content += f"            <tr><td><code>{field_id}</code></td>{num_cell}<td>{type_val}</td><td>{desc}</td></tr>\n"
        
    html_content += """        </tbody>
    </table>
</body>
</html>
"""
    with open(output_html_path, 'w') as out:
        out.write(html_content)
    print(f"HTML legend successfully created at: {output_html_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python vcf_legend.py <input.vcf.gz>")
        sys.exit(1)
    
    vcf_input = sys.argv[1]
    #output_arg = sys.argv[2]

    # 1. Detect which variant caller was used
    caller = detect_caller(vcf_input)
    print(f"Detected caller: {caller}")

    # 2. Modify the output file name to include the caller
    # If the user passes an directory path or an existing .html file, build a specific format:
    # if output_arg.endswith('.html'):
        # Insert caller name right before .html (e.g. 'report.html' becomes 'report_Mutect2.html')
    #    base, _ = os.path.splitext(output_arg)
    #    final_output_path = f"{base}_{caller}.html"
    #else:
        # If a folder path or simple string is passed, generate name dynamically
    #final_output_path = os.path.join(output_arg, f"vcf_legend_{caller}.html") if os.path.isdir(output_arg) else f"{output_arg}_{caller}.html"
    
    final_output_path = f"{caller}_vcf_legend.html"

    # 3. Parse and generate
    inf, fmt = parse_vcf_header(vcf_input)
    generate_html(inf, fmt, caller, final_output_path)
