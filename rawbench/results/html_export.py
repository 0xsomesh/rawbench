import os
from datetime import datetime
from jinja2 import Template

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>RawBench Results</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .summary {
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .result {
            margin-bottom: 20px;
            padding: 20px;
            border: 1px solid #dee2e6;
            border-radius: 8px;
        }
        .result:hover {
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .messages {
            margin-left: 20px;
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
        }
        .metadata {
            color: #6c757d;
            font-size: 0.9em;
        }
        pre {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>RawBench Results</h1>
        <div class="summary">
            <h2>Summary</h2>
            <p><strong>Total Results:</strong> {{ summary.total_results }}</p>
            <p><strong>Total Tokens:</strong> {{ summary.total_tokens }}</p>
            <p><strong>Average Latency:</strong> {{ "%.2f"|format(summary.avg_latency) }}ms</p>
            <p><strong>Generated:</strong> {{ generated_at }}</p>
        </div>

        <h2>Results</h2>
        {% for result in results %}
        <div class="result">
            <h3>Result #{{ loop.index }}</h3>
            <div class="metadata">
                <p><strong>ID:</strong> {{ result.id }}</p>
                <p><strong>Model:</strong> {{ result.model_id }}</p>
                <p><strong>Test:</strong> {{ result.test_id }}</p>
                <p><strong>Created:</strong> {{ result.created_at }}</p>
                <p><strong>Tokens:</strong> {{ result.total_tokens }} (Prompt: {{ result.prompt_tokens }}, Completion: {{ result.completion_tokens }})</p>
                {% if result.latency_ms is not none %}
                <p><strong>Latency:</strong> {{ result.latency_ms }}ms</p>
                {% endif %}
            </div>

            <h4>Input Messages</h4>
            <div class="messages">
                {% for msg in result.input_messages %}
                <div class="message">
                    <strong>{{ msg.role }}:</strong>
                    <pre>{{ msg.content }}</pre>
                </div>
                {% endfor %}
            </div>

            <h4>Output Message</h4>
            <div class="messages">
                <div class="message">
                    <strong>{{ result.output_message.role }}:</strong>
                    <pre>{{ result.output_message.content }}</pre>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

def export_results_to_html(data, output_path: str) -> None:
    """
    Export results to an HTML file.
    
    Args:
        collector: ResultCollector containing the results to export
        output_path: Path where the HTML file should be saved
    """
    template = Template(HTML_TEMPLATE)
    
    
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
