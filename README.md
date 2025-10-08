# 🌿 Sustineo

Sustainability AI Agent specialized in analyzing greenhouse gas emissions inventory, identifying reduction opportunities, and ensuring GHG Protocol compliance.

![Uploading image.png…]()


## 🎯 Features

- **📊 Emissions analysis**: Scope 1, 2, and 3 with summaries and totals
- **💬 Natural language Q&A**: Answers grounded in the GHG Protocol and your data
- **✅ Quality assessment**: Scope 2 validity checks against GHG Protocol guidance
- **📈 Peer benchmarking**: Summarize peer reports and compare against your data
- **🎯 Supplier prioritization**: Identify high-impact suppliers for engagement
- **🖹 OCR for scanned PDFs**: Tesseract-based OCR for image-only pages
- **📝 Automated reporting**: Generate structured summary reports

## 🚀 Quick start

### Requirements

- Python 3.12+
- GOOGLE_API_KEY(Must download service acount key and set it to environment variable first.)
- Tesseract for OCR

### Install

```bash
# Clone the repository
git clone https://github.com/yourusername/Sustineo.git
cd Sustineo

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### Install Tesseract OCR (required for scanned PDFs)

- macOS (Homebrew):
```bash
brew install tesseract
```

- Ubuntu/Debian:
```bash
sudo apt-get update && sudo apt-get install -y tesseract-ocr
```

- Windows:
Download the installer from the [Tesseract OCR releases (UB Mannheim build)](https://github.com/UB-Mannheim/tesseract/wiki) and ensure the installation directory (e.g., `C:\Program Files\Tesseract-OCR`) is on your PATH.

If Tesseract is installed in a non-standard path, you can point `pytesseract` to it:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "/path/to/tesseract"
```

## Run the demo

```bash
python demo.py
```

Outputs will be written to `demo_outputs/`.

## 📁 Project structure

```
sustineo/
├── README.md
├── requirements.txt
├── demo.py
├── data/
│   ├── raw/
│   │   ├── ghg-protocol-revised.pdf
│   │   ├── peer1_emissions_report.pdf
│   │   ├── peer2_emissions_report.pdf
│   │   ├── scope1.csv
│   │   ├── scope2.csv
│   │   └── scope3.csv
│   └── processed/
│       ├── peer1_text.txt
│       └── peer2_text.txt
├── demo_outputs/
│   └── answer*.txt
└── src/
    ├── agent.py
    ├── data_loader.py
    ├── document_processor.py
    ├── emissions_analyzer.py
    ├── quality_assessor.py
    └── utils.py
```
