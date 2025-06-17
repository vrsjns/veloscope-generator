# Veloscope Generator

## Overview

Veloscope Generator is an automated system that creates personalized daily horoscopes for cyclists. By combining astrological elements with cycling-specific advice, the system generates unique, encouraging messages tailored to each rider based on their zodiac sign.

## How It Works

The system operates through a three-stage batch processing pipeline:

1. **Batch Preparation**: Generates prompts for each rider based on their personal information and zodiac sign.
2. **Batch Upload**: Submits the prepared prompts to OpenAI's batch processing API.
3. **Batch Download**: Retrieves completed horoscopes and stores them for distribution.

Each stage runs as an independent containerized service, allowing for scalable and reliable operation.

## Key Features

- Personalized horoscopes for cyclists based on their zodiac sign
- Automated batch processing using OpenAI's API
- AWS S3 integration for data storage and retrieval
- Containerized architecture for easy deployment and scaling
- Comprehensive logging and error handling

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- AWS account with S3 access
- OpenAI API key

### Configuration

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Create python virtual environment:

```
# Navigate to the project root
python -m venv venv

# Activate the virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

### Running Individual Packages

#### Prepare a batch input:

```
PYTHONPATH=$PYTHONPATH:. python packages/batch-prepare/src/batch_prepare_input.py
```

#### Upload batches to OpenAI:

```
PYTHONPATH=$PYTHONPATH:. python packages/batch-upload/src/batch_upload_input.py
```

#### Download results:

```
PYTHONPATH=$PYTHONPATH:. python packages/batch-download/src/batch_download_result.py
```

## Deployment

The project uses GitHub Actions for CI/CD. When you push to the main branch, it automatically:

1. Detects which components have changed
2. Builds Docker images for the changed components
3. Pushes the images to AWS ECR

See ```.github/workflows/docker-build.yml for details.```

## Project Structure

- ```packages/```: Contains the main components of the application
  - ```batch-prepare/```: Prepares input data for processing
  - ```batch-upload/```: Uploads prepared data to OpenAI
  - ```batch-download/```: Downloads and processes results
- ```shared/```: Contains shared code used by multiple packages
  - ```config.py```: Configuration settings
  - ```utils/```: Utility functions
- ```.env.example```: Example environment variables
- ```requirements.txt```: Python dependencies

## Contributing

1. Fork the repository
2. Create your feature branch (```git checkout -b feature/amazing-feature```)
3. Commit your changes (```git commit -m 'Add some amazing feature'```)
4. Push to the branch (```git push origin feature/amazing-feature```)
5. Open a Pull Request
