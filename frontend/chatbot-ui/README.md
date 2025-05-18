# AI Chatbot UI

A state-of-the-art React-based user interface for an LLM chatbot with dynamic character creation and tool capabilities.

## Features

- **Multiple Characters:** Chat with different AI personalities, each with their own expertise and style
- **Dynamic Tools:** Use specialized tools during conversations for information retrieval, data analysis, and more
- **Custom Creation:** Create your own characters and tools to build the perfect AI assistant
- **Responsive Design:** Works seamlessly on desktop and mobile devices
- **Modern UI/UX:** Clean, intuitive interface with animations and visual feedback

## Technologies Used

- React 18 with Hooks
- React Router for navigation
- Material UI for components
- Tailwind CSS for styling
- Framer Motion for animations
- Zustand for state management
- Axios for API communication

## Getting Started

### Prerequisites

- Node.js (v14.0.0 or higher)
- npm or yarn

### Installation

1. Clone the repository
2. Navigate to the project directory

```bash
cd chatbot-ui
```

3. Install dependencies

```bash
npm install
# or
yarn install
```

4. Start the development server

```bash
npm start
# or
yarn start
```

5. Open your browser and visit `http://localhost:3000`

## Project Structure

```
chatbot-ui/
├── public/                  # Static files
├── src/                     # Source code
│   ├── components/          # React components
│   │   ├── characters/      # Character-related components
│   │   ├── chat/            # Chat-related components
│   │   ├── layout/          # Layout components
│   │   └── tools/           # Tool-related components
│   ├── contexts/            # React Context providers
│   ├── hooks/               # Custom React hooks
│   ├── pages/               # Page components
│   ├── services/            # API services
│   ├── utils/               # Utility functions
│   ├── App.js               # Main App component
│   ├── index.js             # Entry point
│   └── index.css            # Global styles
├── .gitignore
├── package.json
├── README.md                # This file
├── tailwind.config.js       # Tailwind CSS configuration
└── postcss.config.js        # PostCSS configuration
```

## Connecting to Backend

This UI is designed to be connected to a backend API that provides:

1. User authentication
2. Character creation and management
3. Tool creation and management
4. Chat functionality

To connect to your backend API:

1. Update the API endpoints in the context files:
   - `src/contexts/AuthContext.js`
   - `src/contexts/CharacterContext.js`
   - `src/contexts/ToolContext.js`
   - `src/contexts/ChatContext.js`

2. Uncomment the API calls and remove the mock data functions

## Deployment

### Building for Production

```bash
npm run build
# or
yarn build
```

This will create an optimized build in the `build` folder that can be deployed to any static hosting service.

## License

This project is licensed under the MIT License

## Acknowledgements

- [React](https://reactjs.org/)
- [Material UI](https://mui.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Framer Motion](https://www.framer.com/motion/)
