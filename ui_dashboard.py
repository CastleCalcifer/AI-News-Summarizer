"""
Simple web UI dashboard served on a separate port for testing the pipeline.
Run this alongside the other services to get a clickable interface.

Usage:
  python ui_dashboard.py
  Then open http://localhost:5000/ui
"""
from flask import Flask, render_template_string
import os

app = Flask(__name__)

# Get service URLs from env or use defaults
# When running locally (not in Docker), use localhost:<mapped_port>
# When running in Docker, service names resolve internally
COLLECTOR_URL = os.getenv("COLLECTOR_URL", "http://localhost:5001")
SUMMARIZER_URL = os.getenv("SUMMARIZER_URL", "http://localhost:5002")
SENTIMENT_URL = os.getenv("SENTIMENT_URL", "http://localhost:5003")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI News Summarizer - Test Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: white; text-align: center; margin-bottom: 30px; font-size: 2.5em; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }
        
        .nav-bar {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
            justify-content: center;
        }
        .nav-bar a {
            padding: 12px 24px;
            background: white;
            color: #667eea;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }
        .nav-bar a:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transition: all 0.3s;
        }
        .card:hover { transform: translateY(-4px); box-shadow: 0 6px 16px rgba(0,0,0,0.2); }
        
        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .card p { color: #666; margin-bottom: 15px; line-height: 1.5; }
        
        input, textarea, select {
            width: 100%;
            padding: 10px;
            margin: 8px 0;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            font-family: inherit;
            transition: border-color 0.3s;
        }
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
            background: #f8f9ff;
        }
        
        button {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        button:hover { transform: scale(1.02); box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4); }
        button:active { transform: scale(0.98); }
        
        .output {
            background: #f5f5f5;
            border: 2px solid #ddd;
            border-radius: 6px;
            padding: 12px;
            margin-top: 15px;
            max-height: 250px;
            overflow-y: auto;
            white-space: pre-wrap;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 12px;
            color: #333;
            display: none;
            line-height: 1.4;
        }
        .output.error { border-color: #e74c3c; background: #fadbd8; color: #c0392b; }
        .output.success { border-color: #27ae60; background: #d5f4e6; color: #229954; }
        
        .full-width {
            grid-column: 1 / -1;
        }
        
        .status { font-size: 12px; color: #999; margin-top: 10px; }
        
        .emoji { font-size: 1.2em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI News Summarizer</h1>
        
        <div class="nav-bar">
            <a href="http://localhost:5001/ui">📰 Collector</a>
            <a href="http://localhost:5002/">✍️ Summarizer</a>
            <a href="http://localhost:5003/summarizer?topic=ai">💭 Sentiment</a>
            <a href="http://localhost:5000/">🏠 Dashboard (Refresh)</a>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2><span class="emoji">📰</span> Step 1: Collect News</h2>
                <p>Enter a topic to fetch and collect news articles.</p>
                <input type="text" id="topic" placeholder="e.g., ai, technology, science, health" value="ai" />
                <button onclick="runCollect()">🔍 Collect Articles</button>
                <div id="collectOutput" class="output"></div>
            </div>
            
            <div class="card">
                <h2><span class="emoji">✍️</span> Step 2: Summarize</h2>
                <p>Articles are summarized by the LLM running on port 11434.</p>
                <textarea id="articlesInput" placeholder="Paste collected articles JSON (optional)" style="height: 80px;"></textarea>
                <button onclick="runSummarize()">📝 Summarize Articles</button>
                <div id="summarizeOutput" class="output"></div>
            </div>
            
            <div class="card">
                <h2><span class="emoji">💭</span> Step 3: Analyze Sentiment</h2>
                <p>Analyze the sentiment and tone of summaries.</p>
                <textarea id="summariesInput" placeholder="Paste summaries JSON (optional)" style="height: 80px;"></textarea>
                <button onclick="runAnalyze()">🎯 Analyze Sentiment</button>
                <div id="analyzeOutput" class="output"></div>
            </div>
            
            <div class="card full-width">
                <h2><span class="emoji">🚀</span> Full Pipeline</h2>
                <p>Run the complete pipeline: collect → summarize → analyze sentiment.</p>
                <input type="text" id="pipelineTopic" placeholder="Enter topic (e.g., ai, science)" value="ai" />
                <button onclick="runPipeline()">▶️ Run Full Pipeline</button>
                <div id="pipelineOutput" class="output"></div>
            </div>
        </div>
    </div>
    
    <script>
        let lastCollected = null;
        let lastSummarized = null;
        
        function showOutput(elementId, text, isError = false) {
            const el = document.getElementById(elementId);
            el.textContent = text;
            el.style.display = 'block';
            el.classList.remove('error', 'success');
            el.classList.add(isError ? 'error' : 'success');
        }
        
        async function runCollect() {
            const topic = document.getElementById('topic').value;
            showOutput('collectOutput', '⏳ Loading...');
            try {
                const resp = await fetch('{{ collector_url }}/collect', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic })
                });
                const data = await resp.json();
                lastCollected = data;
                showOutput('collectOutput', JSON.stringify(data, null, 2));
            } catch (e) {
                showOutput('collectOutput', '❌ Error: ' + e.message, true);
            }
        }
        
        async function runSummarize() {
            showOutput('summarizeOutput', '⏳ Loading...');
            let articles = null;
            const custom = document.getElementById('articlesInput').value.trim();
            if (custom) {
                try {
                    articles = JSON.parse(custom);
                } catch (e) {
                    showOutput('summarizeOutput', '❌ Invalid JSON: ' + e.message, true);
                    return;
                }
            } else if (lastCollected) {
                articles = lastCollected;
            } else {
                showOutput('summarizeOutput', '⚠️ No articles. Collect first or paste JSON.', true);
                return;
            }
            // Ensure articles is an array
            if (!Array.isArray(articles)) {
                showOutput('summarizeOutput', '❌ Articles must be an array (starting with [).', true);
                return;
            }
            try {
                const resp = await fetch('{{ summarizer_url }}/summarize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ articles })
                });
                const data = await resp.json();
                lastSummarized = data;
                showOutput('summarizeOutput', JSON.stringify(data, null, 2));
            } catch (e) {
                showOutput('summarizeOutput', '❌ Error: ' + e.message, true);
            }
        }
        
        async function runAnalyze() {
            showOutput('analyzeOutput', '⏳ Loading...');
            let summaries = null;
            const custom = document.getElementById('summariesInput').value.trim();
            if (custom) {
                try {
                    summaries = JSON.parse(custom);
                } catch (e) {
                    showOutput('analyzeOutput', '❌ Invalid JSON: ' + e.message, true);
                    return;
                }
            } else if (lastSummarized && Array.isArray(lastSummarized)) {
                summaries = lastSummarized;
            } else if (lastSummarized && lastSummarized.analysis) {
                summaries = lastSummarized.analysis;
            } else {
                showOutput('analyzeOutput', '⚠️ No summaries. Summarize first or paste JSON.', true);
                return;
            }
            // Ensure summaries is an array
            if (!Array.isArray(summaries)) {
                showOutput('analyzeOutput', '❌ Summaries must be an array (starting with [).', true);
                return;
            }
            try {
                const resp = await fetch('{{ sentiment_url }}/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ summaries })
                });
                const data = await resp.json();
                showOutput('analyzeOutput', JSON.stringify(data, null, 2));
            } catch (e) {
                showOutput('analyzeOutput', '❌ Error: ' + e.message, true);
            }
        }
        
        async function runPipeline() {
            const topic = document.getElementById('pipelineTopic').value;
            showOutput('pipelineOutput', '📰 Step 1: Collecting articles...');
            try {
                const cResp = await fetch('{{ collector_url }}/collect', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic })
                });
                const articles = await cResp.json();
                showOutput('pipelineOutput', '📰 Collected ' + articles.length + ' articles\\n✍️ Step 2: Summarizing...');
                
                const sResp = await fetch('{{ summarizer_url }}/summarize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ articles })
                });
                const summaries = await sResp.json();
                
                let finalResult = summaries;
                if (!summaries.overall_tone) {
                    showOutput('pipelineOutput', '📰 Collected ' + articles.length + ' articles\\n✍️ Summarized ' + summaries.length + ' articles\\n💭 Step 3: Analyzing sentiment...');
                    const aResp = await fetch('{{ sentiment_url }}/analyze', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ summaries })
                    });
                    finalResult = await aResp.json();
                }
                
                showOutput('pipelineOutput', '✅ Pipeline Complete!\\n\\n' + JSON.stringify(finalResult, null, 2));
            } catch (e) {
                showOutput('pipelineOutput', '❌ Error: ' + e.message, true);
            }
        }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def dashboard():
    return render_template_string(
        HTML_TEMPLATE,
        collector_url=COLLECTOR_URL,
        summarizer_url=SUMMARIZER_URL,
        sentiment_url=SENTIMENT_URL
    )

@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok", "service": "ui_dashboard"}

if __name__ == "__main__":
    # Run on port 5000 by default (or use PORT env var)
    port = int(os.getenv("PORT", 5000))
    print(f"UI Dashboard running on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
