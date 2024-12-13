# Tech Stack Description

## Webapp Tech Stack

### 1. Frontend Framework
- **Framework**: Vue.js 3
  - Utilizes Composition API
  - Implemented with TypeScript for type safety

### 2. Build and Bundling
- **Build Tool**: Vite
  - Provides fast development server and build process
- **Package Manager**: pnpm
  - Efficient dependency management

### 3. State Management
- **Approach**: Custom composable store
  - Located in `src/composables/useStore.ts`
  - Reactive state management
  - Lightweight alternative to Vuex/Pinia

### 4. Routing
- **Implied Router**: Vue Router
  - Multi-component structure suggests routing implementation

### 5. API Interaction
- **HTTP Client**: Custom API service
  - Located in `src/services/api.ts`
  - RESTful API communication
  - Likely using Axios or Fetch API

### 6. Deployment
- **Hosting**: Static site deployment
  - Suitable for Vercel, Netlify, or similar platforms

## Microservice Tech Stack

### 1. Language and Runtime
- **Language**: Python 3.x
- **Paradigm**: Asynchronous programming
- **Key Libraries**:
  - Telethon (Telegram API client)
  - Requests (HTTP interactions)
  - python-dotenv (Environment management)

### 2. API Integrations
- **Primary APIs**:
  - Telegram API
  - Teable API
  - n8n Webhooks

### 3. Authentication
- **Security Mechanisms**:
  - API token-based authentication
  - Environment-based configuration
  - Telegram 2FA support

### 4. Data Management
- **Persistence**:
  - JSON-based tracking (`processed_ids.json`)
  - Environment variable configuration

### 5. Architectural Patterns
- Microservice architecture
- Event-driven design
- Configuration-driven workflow

### 6. Deployment Considerations
- Containerization ready
- Serverless deployment potential
- CI/CD compatible

## Interconnection Strategy
- Webhook-driven communication
- Modular, loosely coupled design
- Flexible configuration management
