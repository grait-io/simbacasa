# SimbaCasa Membership Application

## Project Overview

SimbaCasa is a comprehensive membership management application that leverages modern web technologies and a sophisticated microservice architecture to streamline user onboarding and group management.

## Tech Stack

### Frontend
- Vue.js 3 with TypeScript
- Vite build tool
- Composition API
- Custom state management

### Backend Microservice
- Python-based Telegram group management
- Self-hosted Teable for data management
- n8n for workflow automation

## Key Features
- Seamless user registration process
- Multi-step form with validation
- Telegram group integration
- Automated user approval workflow

## Prerequisites

### Frontend
- Node.js (v16+)
- pnpm package manager

### Microservice
- Python 3.8+
- Telegram API credentials
- Teable instance
- n8n automation server

## Setup Instructions

### Frontend Setup
1. Clone the repository
2. Install dependencies:
   ```bash
   pnpm install
   ```
3. Run development server:
   ```bash
   pnpm dev
   ```

### Microservice Setup
1. Navigate to `microservice/` directory
2. Create a `.env` file based on `.env.example`
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure Telegram API credentials
5. Run the microservice:
   ```bash
   python add_to_telegram_group.py
   ```

## Telegram API Setup
1. Visit https://my.telegram.org/
2. Create a new application
3. Obtain API ID and API Hash
4. Add credentials to `.env`

## Environment Configuration
- Use `.env.example` as a template
- Configure Teable, Telegram, and n8n settings
- Keep sensitive information confidential

## Deployment
- Frontend: Vercel, Netlify, or similar static hosting
- Microservice: Docker, serverless platforms
- Ensure secure, isolated environments

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push and create a pull request

## License
[Specify your project's license]

## Support
For issues or questions, please open a GitHub issue.
