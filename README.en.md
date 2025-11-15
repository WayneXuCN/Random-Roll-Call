# Random Roll Call

[English](README.en.md) | [中文](README.md)

A classroom-oriented random roll call application supporting Excel import, fair random selection, history tracking, and simple management.

## Features

- **Excel Import**: Import student name lists from `.xlsx` or `.xls`
- **Fair Random Draw**: PRNG based selection
- **Multiple Selection**: Pick 1–20 students at once
- **Duplicate Control**: Toggle to allow or prevent repeats within a round
- **Animation**: Smooth rolling animation during selection
- **Clean UI**: Professional blue-themed interface for teaching scenarios
- **Local Data Storage**: Persists students and roll call history
- **History & Stats**: Full record of all selections with statistics
- **Data Validation**: Format checking, duplicate detection, and anomaly handling on import
- **Robust Error Handling**: Comprehensive exception capture and user-friendly messages
- **Manual Management**: Add / remove students manually, smart handling of duplicate names
- **Menu Utilities**: Includes clearing student list and other advanced actions

## Requirements

- Python 3.9+
- `uv` package manager

## Installation & Run

### Using `uv` to manage the virtual environment

1. Clone or download the repository
1. Install dependencies:

```bash
uv sync
```

1. Run the application:

```bash
uv run python -m src.main
```

## Usage

1. Prepare an Excel template file with student names in the first column
2. Launch the application and click "Import List"
3. Set number of students to draw (1–20) and choose whether to prevent repeats
4. Click "Start" then later "Stop" to finalize the selection
5. View history and statistics in the history panel

## Project Structure

```text
random_roll_call/
├── src/
│   ├── main.py          # GUI entry point and core logic
│   └── excel_importer.py # Excel import module
├── data/                # Local data storage
│   ├── students.json    # Student list
│   ├── history.json     # Roll call history
│   └── config.json      # App configuration
├── docs/                # Documentation
│   └── user_guide.md    # User guide
├── template.xlsx        # Excel template
├── pyproject.toml       # Project configuration
├── requirements.txt     # Dependency list
├── README.md            # Chinese README
├── README.en.md         # English README
├── build.py             # Packaging script
└── uv.lock              # Dependency lock file
```

## Packaging (Executable)

Use PyInstaller:

```bash
# Install PyInstaller
uv add pyinstaller

# Build via script
uv run python build.py
# Or directly
pyinstaller --onefile --windowed --name "Random Roll Call" src/main.py
```

## License

MIT License. See [LICENSE](LICENSE) for details.
