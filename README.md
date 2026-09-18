# ISIRI 2.0 - Intelligent Speech Interface for Regional Interaction

A voice-controlled intelligent assistant that supports regional languages (including Tulu) and integrates with various services and hardware devices.

## Features

- **Voice Control**: Natural language processing for voice commands
- **Multi-language Support**: English and Tulu language support with translation capabilities
- **Hardware Integration**: Raspberry Pi GPIO control for door locks and other devices
- **Service Integration**: 
  - Weather information
  - Spotify music control
  - YouTube video playback
  - Browser automation
  - Alarm scheduling
  - Calculator
  - Search functionality
- **AI/ML Pipeline**: Custom intent detection, entity extraction, and translation models
- **Web Interface**: React-based frontend for visual interaction
- **Real-time Processing**: Whisper-based speech recognition with fast response times

## Architecture

```
ISIRI 2.0/
├── backend/           # FastAPI backend with plugins
├── frontend/          # React frontend interface
├── ai_engine/         # AI/ML components (intent, entities, translation)
├── hardware/          # Raspberry Pi GPIO service
├── training/          # ML model training and evaluation
├── datasets/          # Training datasets and vocabulary
└── tools/             # Utility scripts
```

## Prerequisites

- Python 3.8+
- Node.js 18+
- Raspberry Pi (for hardware integration)
- Git

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/shravya-sk/ISIRI-2.0.git
cd ISIRI-2.0
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Environment Configuration
Create a `.env` file in the project root or backend directory:

```env
# Raspberry Pi Configuration
RPI_HOST=http://isiri.local:5000
RPI_IPV6_FALLBACK=http://[fe80::1]:5000
HARDWARE_SIMULATION=false

# Other configuration as needed
```

## Quick Start

### 1. Start Raspberry Pi Service (Hardware)
Connect to your Raspberry Pi via SSH:
```bash
ssh -6 isiri@isiri.local
```

After providing the password, start the GPIO service:
```bash
python3 rpi_gpio_service.py --port 5000
```

### 2. Start Backend Server
```bash
# From project root
uvicorn backend.app.main:app --reload
```

The backend will be available at `http://localhost:8000`

### 3. Start Frontend Development Server
```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

### Voice Commands

#### Door Lock Control
- "Lock the door" / "Baakil lock malpule"
- "Unlock the door" / "Baakil unlock malpule"

#### Weather
- "Weather in Mangalore"
- "What's the weather today?"

#### Music
- "Play music on Spotify"
- "Open Spotify"

#### Videos
- "Open YouTube"
- "Play video on YouTube"

#### Alarms
- "Set an alarm for 7 AM"
- "Wake me up at 8:30"

#### Web Browsing
- "Open Google"
- "Search for Python tutorials"

#### Calculations
- "Calculate 25 * 4"
- "What's 100 divided by 5?"

### API Endpoints

#### Backend API
- `GET /` - Welcome message
- `POST /upload-audio` - Upload audio for voice processing
- `GET /alarms` - List scheduled alarms
- `GET /health` - Health check with build info
- `GET /device/lock/status` - Get current lock state
- `POST /device/lock/{state}` - Set lock state (locked/unlocked)
- `GET /device/lock/diag` - Hardware diagnostics

#### Hardware Service (Raspberry Pi)
- `GET /status` - Service status and current lock state
- `POST /device/lock/{state}` - Control lock (state = 'locked' or 'unlocked')

## Hardware Setup

### Raspberry Pi Configuration

The system uses a Raspberry Pi with an SG90 servo for door lock control. The hardware service runs as a standalone daemon on the Pi.

#### Pin Mapping
- GPIO 18 (Pin 12): Door Lock Servo (PWM signal)

#### Servo Calibration
The servo angles need calibration based on your 3D-printed mechanism:
```python
LOCK_ANGLE = 180      # servo angle when locked
UNLOCK_ANGLE = 0      # servo angle when unlocked
```

#### IPv6 Configuration
If your Raspberry Pi uses IPv6, configure the environment variables:
```bash
export RPI_HOST="http://isiri.local:5000"
export RPI_IPV6_FALLBACK="http://[fe80::1]:5000"
```

For detailed hardware setup instructions, see the hardware configuration documentation.

## AI/ML Components

### Intent Detection
Identifies the user's intent from voice commands (lock, weather, music, etc.)

### Entity Extraction
Extracts relevant entities from commands (times, locations, quantities)

### Translation
Translates between English and Tulu for regional language support

### Model Training
Custom models can be trained using the training pipeline:
```bash
cd training
python train_model.py
```

## Plugins

The system uses a plugin architecture for extensibility:

- **hardware**: Door lock control via Raspberry Pi
- **weather**: Weather information retrieval
- **spotify**: Music playback control
- **youtube**: Video playback
- **alarm**: Alarm scheduling and management
- **browser**: Web browser automation
- **calculator**: Mathematical calculations
- **search**: Web search functionality
- **translation**: Language translation
- **system**: System commands and information
- **knowledge**: Knowledge base queries
- **movies**: Movie information

## Development

### Adding New Plugins
1. Create a new plugin file in `backend/app/plugins/`
2. Implement the `execute(data: Dict[str, Any]) -> Dict[str, Any]` function
3. Register the plugin in the AI engine

### Training Custom Models
1. Prepare your dataset in `datasets/`
2. Configure training parameters in `training/config.py`
3. Run the training pipeline
4. Evaluate model performance with `training/evaluate.py`

## Troubleshooting

### Hardware Connection Issues
If the door lock doesn't respond:
1. Check the `/device/lock/diag` endpoint for detailed diagnostics
2. Verify Raspberry Pi is accessible via SSH
3. Check the environment variables for correct IPv6 formatting
4. Review backend logs for connection errors

### Voice Recognition Issues
1. Check microphone permissions
2. Verify Whisper model is loaded correctly
3. Check audio file format and quality
4. Review backend logs for transcription errors

### Frontend Connection Issues
1. Ensure backend is running on port 8000
2. Check CORS configuration in backend
3. Verify network connectivity
4. Check browser console for errors

## Project Structure

```
ISIRI 2.0/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── plugins/             # Plugin implementations
│   │   ├── voice/               # Voice processing pipeline
│   │   └── core/                # Core utilities
│   └── requirements.txt
├── frontend/
│   ├── src/                     # React source code
│   └── package.json
├── ai_engine/
│   ├── engine.py                # AI orchestrator
│   ├── intent_detector.py      # Intent classification
│   ├── entity_extractor.py     # Entity extraction
│   ├── translator.py           # Translation models
│   └── planner.py              # Action planning
├── hardware/
│   └── rpi_gpio_service.py     # Raspberry Pi GPIO service
├── training/
│   ├── train_model.py          # Model training
│   ├── evaluate.py             # Model evaluation
│   └── seq2seq_model.py        # Sequence-to-sequence model
└── datasets/
    ├── raw/                     # Raw datasets
    └── vocabulary/              # Vocabulary files
```

## Contributing

Contributions are welcome! Please follow these guidelines:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Specify your license here]

## Acknowledgments

- OpenAI Whisper for speech recognition
- FastAPI for the backend framework
- React for the frontend interface
- Raspberry Pi Foundation for hardware support
- The Tulu language community for translation resources

## Contact

For questions, issues, or contributions, please visit the GitHub repository or contact the development team.

---

**ISIRI 2.0** - Bringing voice intelligence to regional languages and smart home integration.