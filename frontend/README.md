# DevMetrics AI - Frontend

Modern, responsive Next.js 14 dashboard for the DevMetrics AI platform.

## Features

- 🔐 **Authentication** - Secure JWT-based authentication
- 📊 **Analytics Dashboard** - Real-time productivity metrics and insights
- 🎯 **Multi-dimensional Scoring** - 6-component productivity evaluation
- 🤖 **AI Insights** - Personalized recommendations and pattern detection
- 📈 **Historical Trends** - Track progress over time
- 👥 **Role-Based Access** - Developer, Manager, and Admin views
- 🎨 **Modern UI** - Built with TailwindCSS and shadcn/ui components
- ⚡ **Performance** - Optimized with Next.js 14 App Router

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** TailwindCSS
- **UI Components:** Radix UI primitives
- **State Management:** Zustand
- **API Client:** Axios
- **Charts:** Recharts
- **Animations:** Framer Motion
- **Date Handling:** date-fns

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Running DevMetrics AI backend (see `../backend/README.md`)

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env.local
   ```

   Edit `.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Run development server:**
   ```bash
   npm run dev
   ```

4. **Open browser:**
   Navigate to http://localhost:3000

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── login/             # Login page
│   │   ├── register/          # Registration page (TODO)
│   │   ├── dashboard/         # Developer dashboard
│   │   ├── manager/           # Manager dashboard (TODO)
│   │   └── layout.tsx         # Root layout
│   ├── components/
│   │   ├── ui/                # Reusable UI components
│   │   ├── charts/            # Chart components (TODO)
│   │   ├── developer/         # Developer-specific components (TODO)
│   │   └── manager/           # Manager-specific components (TODO)
│   ├── lib/
│   │   ├── api.ts             # API client and methods
│   │   └── utils.ts           # Utility functions
│   ├── store/
│   │   └── auth.ts            # Authentication state management
│   └── types/
│       └── index.ts           # TypeScript type definitions
├── public/                     # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript compiler check

## Features Implemented

### ✅ Session 1: Authentication
- [x] Login page with form validation
- [x] JWT token management
- [x] Protected routes
- [x] Auth state management (Zustand)
- [x] Auto-redirect on unauthorized access
- [ ] Registration page (TODO)
- [ ] Password reset (TODO)

### ✅ Session 2: Dashboard
- [x] Developer dashboard layout
- [x] Productivity score display
- [x] Score breakdown (6 components)
- [x] Work distribution visualization
- [x] AI insights display
- [x] Activity summary
- [x] Team comparison
- [ ] Historical trends chart (TODO)
- [ ] Work activities timeline (TODO)

### ❌ Session 3: Manager View (TODO)
- [ ] Manager dashboard
- [ ] Team overview
- [ ] Top performers list
- [ ] Team comparison charts
- [ ] Individual developer drill-down
- [ ] Export reports

### ❌ Session 4: Integrations (TODO)
- [ ] Integration management page
- [ ] GitHub configuration
- [ ] Jira configuration
- [ ] Sync status monitoring
- [ ] Manual sync triggers

### ❌ Session 5: Advanced Features (TODO)
- [ ] Real-time notifications
- [ ] Dark mode toggle
- [ ] Custom date range picker
- [ ] Export to PDF/CSV
- [ ] Goal setting
- [ ] Skill tracking

## API Integration

The frontend communicates with the backend API using Axios. All API methods are defined in `src/lib/api.ts`:

### Authentication
```typescript
authAPI.login(email, password)
authAPI.register(data)
authAPI.me()
```

### Developers
```typescript
developersAPI.list()
developersAPI.get(id)
developersAPI.create(data)
developersAPI.update(id, data)
```

### Analytics
```typescript
analyticsAPI.getOverview(id, params)
analyticsAPI.getProductivity(id, params)
analyticsAPI.getTrends(id, periods)
analyticsAPI.getWorkBreakdown(id, params)
analyticsAPI.getInsights(id, params)
analyticsAPI.getTeamOverview(team, params)
analyticsAPI.calculateScore(data)
```

### Integrations
```typescript
integrationsAPI.list()
integrationsAPI.configureGitHub(data)
integrationsAPI.configureJira(data)
integrationsAPI.sync(id, days_back)
integrationsAPI.getStatus(id)
integrationsAPI.test(id)
```

## State Management

### Auth Store (Zustand)

```typescript
const { user, token, login, logout, fetchUser } = useAuthStore();

// Login
await login({ email, password });

// Logout
logout();

// Get current user
await fetchUser();
```

The auth store persists the token to localStorage and handles automatic token injection into API requests.

## Component Examples

### Using UI Components

```typescript
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';

<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>
    <Input type="text" placeholder="Enter value" />
    <Button>Submit</Button>
  </CardContent>
</Card>
```

### Fetching Analytics Data

```typescript
import { analyticsAPI } from '@/lib/api';
import { DeveloperProductivity } from '@/types';

const [data, setData] = useState<DeveloperProductivity | null>(null);

useEffect(() => {
  const fetchData = async () => {
    const response = await analyticsAPI.getProductivity(developerId, {
      include_comparison: true
    });
    setData(response.data);
  };
  fetchData();
}, [developerId]);
```

## Testing

### Manual Testing

1. **Login Flow:**
   - Navigate to http://localhost:3000/login
   - Use demo credentials:
     - Manager: `manager@devmetrics.ai` / `Manager123!`
     - Developer: `dev@devmetrics.ai` / `Dev123!`
   - Should redirect to /dashboard on success

2. **Dashboard:**
   - Verify productivity score displays
   - Check 6-component breakdown shows
   - Confirm work distribution appears
   - Verify AI insights render
   - Check activity summary

3. **Authorization:**
   - Logout and try to access /dashboard directly
   - Should redirect to /login
   - Login again to restore access

4. **API Integration:**
   - Open browser DevTools Network tab
   - Navigate through dashboard
   - Verify API calls to backend
   - Check authorization headers include Bearer token

### Automated Testing (TODO)

```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e
```

## Deployment

### Build for Production

```bash
npm run build
npm run start
```

### Environment Variables

Production environment variables:

```env
NEXT_PUBLIC_API_URL=https://api.your domain.com
NEXT_PUBLIC_APP_NAME=DevMetrics AI
```

### Docker (TODO)

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## Troubleshooting

### "Failed to fetch" errors

**Problem:** API requests fail with network errors

**Solution:**
1. Ensure backend is running: `cd ../backend && uvicorn app.main:app --reload`
2. Check `NEXT_PUBLIC_API_URL` in `.env.local` matches backend URL
3. Verify CORS is configured on backend (should allow localhost:3000)

### Token expired / 401 errors

**Problem:** Automatic redirects to login

**Solution:**
1. Tokens expire after 30 minutes by default
2. Login again to get fresh token
3. For development, increase `ACCESS_TOKEN_EXPIRE_MINUTES` in backend

### No data showing in dashboard

**Problem:** Dashboard shows "No Data Available"

**Solution:**
1. Ensure GitHub/Jira integrations are configured (backend)
2. Run data sync: `POST /api/integrations/{id}/sync`
3. Wait for AI analysis tasks to complete
4. Verify database has work_activities records
5. Refresh dashboard

### Type errors

**Problem:** TypeScript compilation errors

**Solution:**
1. Run `npm run type-check` to see all errors
2. Update types in `src/types/index.ts` to match backend responses
3. Ensure API responses match expected types

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome)

## Contributing

1. Follow TypeScript strict mode
2. Use functional components with hooks
3. Follow existing code style
4. Add types for all props and state
5. Use existing UI components from `components/ui`
6. Test on multiple browsers

## Roadmap

### Near-term (Next Sprint)
- [ ] Registration page
- [ ] Manager dashboard
- [ ] Historical trends charts (Recharts)
- [ ] Dark mode support
- [ ] Responsive mobile layout improvements

### Mid-term
- [ ] Integration management UI
- [ ] Custom date range picker
- [ ] Export functionality (PDF/CSV)
- [ ] Real-time updates (WebSockets)
- [ ] Notifications system

### Long-term
- [ ] Advanced filtering and search
- [ ] Custom dashboard widgets
- [ ] Goal setting and tracking
- [ ] Team chat/collaboration
- [ ] Mobile app (React Native)

## License

Proprietary - All rights reserved

## Support

For issues or questions:
- Check backend API is running and accessible
- Review browser console for errors
- Check Network tab for failed API calls
- Verify environment variables are set correctly

---

**Built with ❤️ using Next.js 14**
