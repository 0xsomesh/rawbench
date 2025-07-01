import os
from datetime import datetime
from jinja2 import Template

def export_results_to_html(data, output_path: str) -> None:
    """
    Export results to an HTML file.
    
    Args:
        collector: ResultCollector containing the results to export
        output_path: Path where the HTML file should be saved
    """
    # Load template from file
    template_path = os.path.join(os.path.dirname(__file__), 'template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    template = Template(template_content)
    
    
    # Render HTML
    html_content = template.render(
        results=data['results'],
        summary=data['summary'],
        generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Write the HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
