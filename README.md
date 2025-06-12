# 🧠 WebIntel - Advanced Web Intelligence System

[![PyPI version](https://badge.fury.io/py/webintel.svg)](https://pypi.org/project/webintel/2.0.3/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/JustM3Sunny/webintel.svg)](https://github.com/JustM3Sunny/webintel/stargazers)
[![Downloads](https://pepy.tech/badge/webintel)](https://pepy.tech/project/webintel)
[![Documentation](https://img.shields.io/badge/docs-comprehensive-brightgreen.svg)](https://github.com/JustM3Sunny/webintel#readme)
[![PyPI Package](https://img.shields.io/badge/PyPI-webintel-blue.svg)](https://pypi.org/project/webintel/2.0.3/)

WebIntel is a **superfast AI-powered web intelligence system** that provides real-time web research, comprehensive analysis, and intelligent insights using Google Gemini 2.0 Flash. Get comprehensive research results in **10-20 seconds** with **90%+ success rate**.

## 🚀 Key Features

- **🔍 Multi-Engine Search**: Searches across DuckDuckGo, Bing, and Google simultaneously with intelligent fallback mechanisms
- **🧠 AI-Powered Analysis**: Uses Google Gemini 2.0 Flash for intelligent content analysis, synthesis, and insights generation
- **⚡ Lightning Fast**: Optimized for speed with parallel processing, smart caching, and efficient content extraction (10-20s results)
- **🛡️ Reliable & Robust**: Built-in error handling, retry mechanisms, and fallback strategies ensure consistent performance
- **⚙️ Highly Configurable**: Customizable output formats (JSON, Markdown, Rich), configurable result counts, and flexible API integration
- **📊 Advanced Analytics**: Provides relevance scoring, source credibility analysis, confidence levels, and comprehensive performance metrics

## 📦 Installation

### 🎯 Quick Install (Recommended)
```bash
# Install from PyPI
pip install webintel

# Verify installation
webintel --version
```

### ⚙️ Alternative Installation Methods

#### 🌍 Global Installation (Recommended for CLI usage)
```bash
# Install globally for all users (requires admin/sudo)
pip install --global webintel

# Or install globally with elevated permissions
sudo pip install webintel  # Linux/macOS
# Run as Administrator on Windows, then: pip install webintel
```

#### Using pipx (Isolated CLI installation)
```bash
# Install in isolated environment (best for CLI tools)
pipx install webintel
```

#### Using pip with user flag
```bash
# Install for current user only
pip install --user webintel
```

#### From Source (Development)
```bash
git clone https://github.com/JustM3Sunny/webintel.git
cd webintel
pip install -r requirements.txt
pip install -e .
```

### 📋 System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, Linux
- **Internet**: Stable connection required
- **Memory**: 512MB RAM minimum

### 📦 Package Information
- **PyPI Package**: [webintel](https://pypi.org/project/webintel/2.0.3/)
- **Import Name**: `webintel` (use `from webintel import DataProcessor`)
- **CLI Command**: `webintel` (after installation)

## 🔑 API Key Setup

WebIntel requires a Google Gemini API key for AI-powered analysis:

1. Get your free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set your API key:

```bash
# Linux/macOS
export GEMINI_API_KEY="your-api-key-here"

# Windows
set GEMINI_API_KEY=your-api-key-here
```

## 🚀 Quick Start

### 1️⃣ Install WebIntel
```bash
# Standard installation
pip install webintel

# Global installation (recommended for CLI usage)
pip install --global webintel

# Or using pipx (isolated environment)
pipx install webintel
```

### 2️⃣ Set up API Key
```bash
# Get your free API key from: https://makersuite.google.com/app/apikey
export GEMINI_API_KEY="your-api-key-here"

# On Windows:
set GEMINI_API_KEY=your-api-key-here
```

### 3️⃣ Start Using WebIntel (Auto-Setup)
WebIntel automatically sets up configuration on first run:

```bash
# Basic search - WebIntel will auto-configure itself
webintel search "artificial intelligence trends 2024"

# Get comprehensive results
webintel search "machine learning frameworks" --max-results 10

# JSON output for integration
webintel search "blockchain technology" --format json

# Save results to file
webintel search "climate change research" --save --output-dir ./results
```

### 🔧 Auto-Configuration
WebIntel automatically creates:
- Configuration directory: `~/.webintel/`
- Default config file: `~/.webintel/config.yaml`
- Cache directory: `~/.webintel/cache/`
- Output directory: `~/.webintel/output/`

### 🔥 Advanced Usage Examples
```bash
# Market research with detailed analysis
webintel search "electric vehicle market 2024" --max-results 15 --format rich

# Technology comparison
webintel search "python vs javascript 2024" --save --format json

# Academic research
webintel search "climate change solutions" --max-results 20 --output-dir ./research

# News and trends
webintel search "latest AI breakthroughs" --format markdown
```

## 💻 Usage Examples

### Command Line Interface

```bash
# Market research
webintel search "electric vehicle market 2024" --max-results 5

# Technology research
webintel search "best python frameworks 2024" --format json

# Academic research
webintel search "climate change impact studies" --save

# News and trends
webintel search "AI breakthrough 2024" --max-results 15
```

### Python API

```python
from webintel import DataProcessor
from webintel.config import get_default_config

# Initialize WebIntel
config = get_default_config()
processor = DataProcessor(config)

# Perform comprehensive search
results = await processor.process_query(
    query="artificial intelligence trends 2024",
    max_results=10
)

# Access AI-generated insights
print("🧠 AI Analysis:")
print(results['synthesis']['executive_summary'])

print(f"\n📊 Statistics:")
print(f"Sources found: {len(results['sources'])}")
print(f"Processing time: {results['processing_time']}s")

print(f"\n🔍 Key Insights:")
for insight in results['synthesis']['key_findings']:
    print(f"• {insight}")

print(f"\n📚 Top Sources:")
for source in results['sources'][:3]:
    print(f"• {source['title']}")
    print(f"  🔗 {source['url']}")
    print(f"  📊 Relevance: {source['relevance_score']:.2f}")
```

## 🎯 Real-World Use Cases

### 📈 Market Research
```bash
webintel search "electric vehicle market trends 2024" --max-results 10
```

### 💻 Technology Research
```bash
webintel search "best AI frameworks comparison" --format json
```

### 🎓 Academic Research
```bash
webintel search "climate change impact studies" --save --output-dir ./research
```

### 📰 News & Trends
```bash
webintel search "latest AI breakthroughs 2024" --max-results 15
```

## ⚙️ Configuration

### Environment Variables
```bash
export GEMINI_API_KEY="your-api-key"
export WEBINTEL_MAX_RESULTS=10
export WEBINTEL_OUTPUT_FORMAT="rich"
export WEBINTEL_TIMEOUT=30
```

### Configuration File
WebIntel uses a YAML configuration file located at `~/.webintel/config.yaml`:

```yaml
# Google Gemini AI Configuration
gemini:
  api_key: "your-api-key-here"
  model_name: "gemini-2.0-flash"
  max_tokens: 8192
  temperature: 0.7

# Web Scraping Configuration
scraping:
  max_concurrent_requests: 10
  request_timeout: 30
  retry_attempts: 3

# Output Configuration
output:
  format: "rich"
  save_to_file: false
  include_sources: true
```

## 📊 Performance Metrics

- **Response Time**: 10-20 seconds average
- **Success Rate**: 90%+ for most queries
- **Search Engines**: 3+ engines with intelligent fallback
- **Concurrent Requests**: Up to 10 parallel requests
- **Cache Hit Rate**: 85%+ for repeated queries

## 📋 Requirements

- **Python**: 3.8 or higher
- **API Key**: Google Gemini API key (free tier available)
- **Internet**: Stable internet connection
- **Memory**: 512MB RAM minimum
- **Storage**: 100MB for installation

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Setup
```bash
git clone https://github.com/JustM3Sunny/webintel.git
cd webintel
pip install -r requirements.txt
pip install -e .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini 2.0 Flash** for AI-powered analysis
- **Multiple Search Engines** for comprehensive web coverage
- **Open Source Community** for inspiration and support

## 🔗 Important Links

### 📦 Package & Repository
- **PyPI Package**: [webintel on PyPI](https://pypi.org/project/webintel/2.0.3/)
- **GitHub Repository**: [JustM3Sunny/webintel](https://github.com/JustM3Sunny/webintel)
- **Documentation**: [Full Documentation](https://github.com/JustM3Sunny/webintel#readme)
- **Releases**: [GitHub Releases](https://github.com/JustM3Sunny/webintel/releases)

### 🛠️ Development & API
- **Google Gemini API**: [Get API Key](https://makersuite.google.com/app/apikey)
- **Python Package Index**: [PyPI Project Page](https://pypi.org/project/webintel/2.0.3/)
- **Issue Tracker**: [Report Bugs](https://github.com/JustM3Sunny/webintel/issues)
- **Feature Requests**: [Request Features](https://github.com/JustM3Sunny/webintel/discussions)

### 📊 Statistics & Monitoring
- **Download Stats**: [Package Downloads](https://pepy.tech/project/webintel)
- **GitHub Stats**: [Repository Statistics](https://github.com/JustM3Sunny/webintel)
- **License**: [MIT License](https://github.com/JustM3Sunny/webintel/blob/main/LICENSE)

## 🆘 Support & Community

- **GitHub Issues**: [Report bugs or request features](https://github.com/JustM3Sunny/webintel/issues)
- **GitHub Discussions**: [Community discussions](https://github.com/JustM3Sunny/webintel/discussions)
- **PyPI Package**: [webintel on PyPI](https://pypi.org/project/webintel/2.0.3/)
- **Email Support**: justm3sunny@gmail.com

## 🔗 Quick Links

| Resource | Link |
|----------|------|
| 📦 **Install** | `pip install webintel` or `pip install --global webintel` |
| 📚 **Documentation** | [GitHub README](https://github.com/JustM3Sunny/webintel#readme) |
| 🐛 **Bug Reports** | [GitHub Issues](https://github.com/JustM3Sunny/webintel/issues) |
| 💡 **Feature Requests** | [GitHub Discussions](https://github.com/JustM3Sunny/webintel/discussions) |
| 📊 **Download Stats** | [PyPI Stats](https://pepy.tech/project/webintel) |
| ⭐ **Star on GitHub** | [JustM3Sunny/webintel](https://github.com/JustM3Sunny/webintel) |

## 🚀 Version Information

- **Current Version**: 2.0.3
- **Python Support**: 3.8+
- **Package Name**: webintel
- **Import Name**: webintel
- **CLI Command**: webintel

---

**Made with ❤️ by JustM3Sunny. Star ⭐ this repo if you find it useful!**

**🔗 Connect with me:**
- GitHub: [@JustM3Sunny](https://github.com/JustM3Sunny)
- Email: justm3sunny@gmail.com
