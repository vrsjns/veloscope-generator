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

- Docker
- AWS account with S3 access
- OpenAI API key

### Configuration

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```
