# Institute Timetable Generator 

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/flask-2.0%2B-lightgrey)
![Pandas](https://img.shields.io/badge/pandas-1.3%2B-orange)
![License](https://img.shields.io/badge/license-MIT-green)

An intelligent timetable scheduling system that automates course allocation while respecting faculty availability, batch constraints, and room requirements.

## Features 

- **Automated Scheduling**: AI-powered algorithm for conflict-free timetables
- **Interactive Adjustments**: Drag-and-drop interface for manual refinements
- **Multi-Format Export**: Excel reports and web views
- **Batch-Specific Views**: Separate timetables for each academic batch
- **Smart Conflict Detection**: Real-time validation of constraints

## Technology Stack 

| Component       | Technology |
|----------------|------------|
| Frontend       | HTML5, CSS3, JavaScript (Drag-and-Drop API) |
| Backend        | Python 3.8+, Flask |
| Data Processing| Pandas, NumPy |
| Deployment     | Docker-ready, Heroku-compatible |

## Installation 🛠

### Prerequisites
- Python 3.8+
- pip package manager

### Setup
```bash
# Clone repository
git clone https://github.com/yourusername/timetable-generator.git
cd timetable-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
