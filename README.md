# 🌍 Agent Green

An AI Agent specialized in analyzing greenhouse gas emissions inventory, identifying reduction opportunities, and ensuring GHG Protocol compliance.

## 🎯 Features

- **📊 Emissions Analysis**: Comprehensive analysis of Scope 1, 2, and 3 emissions
- **💬 Natural Language Q&A**: Answer questions about emissions using GHG Protocol knowledge
- **✅ Quality Assessment**: Validate emissions calculations against GHG Protocol standards
- **📈 Peer Benchmarking**: Compare emissions performance with industry peers
- **🎯 Supplier Prioritization**: Identify key suppliers for engagement
- **📝 Automated Reporting**: Generate comprehensive emissions reports with insights

## 🚀 Quick Start

### Specs used

- Python 3.13.5
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/emissions-insights-agent.git
cd emissions-insights-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### Project structure
```
emissions-insights-agent/
├── README.md
├── requirements.txt
├── setup.py
├── .env
├── .gitignore
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_emissions_analysis.ipynb
│   └── 03_agent_demo.ipynb
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── emissions_analyzer.py
│   ├── document_processor.py
│   ├── quality_assessor.py
│   ├── insight_generator.py
│   └── agent.py
├── config/
│   └── config.yaml
├── tests/
│   ├── test_analyzer.py
│   └── test_agent.py
└── docs/
    ├── technical_overview.md
    └── user_guide.md
```