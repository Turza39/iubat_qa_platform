# IUBAT Q&A Platform - React Frontend

A modern React.js frontend for the IUBAT Q&A Platform, providing an intuitive interface for asking questions, writing answers, and engaging with the community.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm/yarn

### Installation

```bash
# Navigate to frontend directory
cd react_frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
npm run preview  # Preview the production build locally
```

## 📋 Features

### Authentication
- User registration and login
- JWT token-based authentication
- Protected routes and API calls
- Automatic token refresh

### Questions & Answers
- Browse and search all questions
- Ask new questions with dynamic tags
- View detailed question pages with all answers
- Filter by tags and search keywords
- Real-time answer count and upvote display

### Voting System
- Upvote/downvote questions and answers
- Visual vote counters
- Toggle votes without page reload

### User Profiles
- Public user profiles with reputation
- User verification badges
- Question history and activity

### Responsive Design
- Mobile-first design with Tailwind CSS
- Works on all device sizes
- Optimized performance

## 📁 Project Structure

```
src/
├── main.jsx                    # React entry point
├── App.jsx                     # Main router and layout
├── index.css                   # Global styles
├── context/
│   └── AuthContext.jsx        # Authentication state management
├── hooks/
│   └── useRedirectIfAuthenticated.js
├── services/                   # API service modules
│   ├── authService.js         # User auth API calls
│   ├── questionService.js     # Question API calls
│   ├── answerService.js       # Answer API calls
│   └── voteService.js         # Vote API calls
├── lib/
│   └── axios.js               # Axios instance with interceptors
├── pages/                      # Page components
│   ├── HomePage.jsx
│   ├── LoginPage.jsx
│   ├── RegisterPage.jsx
│   ├── AskPage.jsx            # Create new question
│   ├── QuestionDetailPage.jsx
│   ├── ProfilePage.jsx
│   └── VerifyPage.jsx         # ID verification
└── components/                 # Reusable components
    ├── layout/
    │   └── Navbar.jsx         # Navigation header
    ├── ui/                     # UI primitives
    │   ├── Button.jsx
    │   ├── Input.jsx
    │   ├── Badge.jsx
    │   └── Spinner.jsx
    └── common/
        └── VerificationBadge.jsx
```

## 🔌 API Integration

The frontend connects to the FastAPI backend through the same origin using the `/api` prefix.

In Docker production, Nginx proxies `/api` to the internal backend service, so the browser never connects to port `8000` directly.

Update the API URL in `src/lib/axios.js` for different environments:

```javascript
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api'
})
```

For local development with Vite, the proxy in `vite.config.js` forwards `/api` to `http://localhost:8000`.

### Key API Endpoints Used
- `POST /users/register/` - User registration
- `POST /users/login/` - User login
- `GET /questions/` - List questions with search
- `POST /questions/` - Create new question
- `GET /questions/{id}/` - Get question details
- `POST /answers/questions/{id}/` - Create answer
- `POST /votes/questions/{id}/` - Vote on question

## 🎨 Styling

The project uses **Tailwind CSS** for styling:
- Utility-first CSS framework
- Dark mode support
- Custom configuration in `tailwind.config.js`

### Customization
Edit `tailwind.config.js` to modify colors, spacing, and other design tokens.

## 📦 Tech Stack

- **React 19** - UI library
- **React Router v6** - Client-side routing
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **React Hot Toast** - Toast notifications
- **Lucide React** - Icon library

## 🔐 Authentication Flow

1. User registers or logs in
2. Backend returns JWT token
3. Token stored in localStorage
4. All API requests include `Authorization: Bearer {token}` header
5. Axios interceptor automatically handles token refresh

## 🧪 Development Tips

### Hot Reload
Vite provides instant hot module replacement (HMR) for fast development iteration.

### Debug API Calls
Check browser's Network tab or use `axios.interceptors` to log all API calls.

### Environment Variables
Create `.env` file for environment-specific variables:
```env
REACT_APP_API_URL=http://127.0.0.1:8000/api
REACT_APP_APP_NAME=IUBAT Q&A Platform
```

## 📱 Pages Overview

| Page | Route | Description |
|------|-------|-------------|
| Home | `/` | Browse all questions |
| Login | `/login` | User login |
| Register | `/register` | New user registration |
| Ask | `/ask` | Create new question |
| Question Detail | `/question/:id` | View question with answers |
| Profile | `/profile/:id` | User public profile |
| Verify | `/verify` | ID verification submission |

## 🚀 Deployment

### Vercel (Recommended)
```bash
npm install -g vercel
vercel
```

### Netlify
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## 📞 Support

For issues or feature requests, please open an issue in the repository.

## 📄 License

This project is part of the IUBAT Q&A Platform initiative.


- **Authentication**: Login, Register, Profile management
- **Questions**: Browse, search, filter by tags, create questions
- **Answers**: View answers on questions
- **Voting**: Upvote questions and answers
- **Student Verification**: Submit and track verification status
- **Responsive Design**: Mobile-first approach with Tailwind CSS

## Routing

The app uses React Router v6 for client-side routing:

- `/` - Home page (all questions)
- `/login` - Login page
- `/register` - Registration page
- `/ask` - Create a new question
- `/questions/:id` - Question detail page
- `/profile` - User profile page
- `/verify` - Student verification page

## API Integration

The frontend communicates with the FastAPI backend. The Axios instance in `src/lib/axios.js` automatically:

- Attaches JWT tokens to all requests
- Handles 401 errors (token expiration)
- Redirects to login on authentication failure

## Styling

The project uses Tailwind CSS for styling. The configuration is in `tailwind.config.js`.

To customize colors and theme, modify the `theme` section in `tailwind.config.js`.

## Development Tips

- Use React DevTools browser extension for debugging
- Use the `useAuth()` hook to access authentication state in any component
- Services are located in `src/services/` for easy API calls
- Reusable UI components are in `src/components/ui/`

## Troubleshooting

### Port Already in Use

If port 3000 is already in use, Vite will automatically use the next available port.

### CORS Issues

If you see CORS errors, ensure your FastAPI backend has proper CORS configuration and is running on `http://127.0.0.1:8000`.

### Token Expiration

The app will automatically redirect to login if the JWT token expires. Clear localStorage and log in again if needed.

## Contributing

When adding new features:

1. Create components in appropriate folders under `src/components/`
2. Create services in `src/services/`
3. Create pages in `src/pages/`
4. Use React Router hooks (`useNavigate`, `useParams`) instead of Next.js router

## Migration Notes

This frontend was converted from Next.js to React.js. Key changes:

- **Router**: Next.js `useRouter()` → React Router `useNavigate()`
- **File-based routing**: Next.js pages → React Router with explicit routes
- **Build tool**: Next.js → Vite
- **Syntax**: All Next.js imports replaced with React equivalents

All functionality remains the same as the original Next.js version.
