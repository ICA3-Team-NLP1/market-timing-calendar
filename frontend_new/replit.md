# CAFFY - Full-Stack Application

## Overview
A full-stack JavaScript application featuring a "CAFFY" branding component imported from Figma. Built with React frontend and Express backend, using modern web development practices with proper client/server separation for security and scalability.

## Project Architecture
- **Frontend**: React 18 with Vite, Wouter for routing, TanStack Query for state management
- **Backend**: Express.js server with TypeScript
- **Database**: In-memory storage (MemStorage) with Drizzle ORM schema definitions
- **UI Framework**: Tailwind CSS with Radix UI components (shadcn/ui)
- **Security**: Proper client/server separation, authenticated sessions with Passport.js

## Technology Stack
- React 18.3 + TypeScript
- Express.js 4.21
- Tailwind CSS 3.4
- Radix UI / shadcn/ui components
- TanStack React Query 5.60
- Wouter routing
- Drizzle ORM + Zod validation
- Vite development server

## Recent Changes
- **2025-01-23**: Migrated from Figma to Replit environment
- **2025-01-23**: Verified full-stack architecture with proper security practices
- **2025-01-23**: Confirmed working development server on port 5000
- **2025-01-23**: Added interactive navigation - CAFFY homepage now clickable
- **2025-01-23**: Integrated login page with Korean text from provided design files
- **2025-01-23**: Created comprehensive home dashboard with FOMC results, recommendations, and upcoming events
- **2025-01-23**: Implemented multi-page navigation flow: CAFFY splash → Login → Home dashboard
- **2025-01-23**: Added interactive chat functionality - clicking recommendations, events, or input launches chat interface
- **2025-01-23**: Created comprehensive chat page with FOMC conversation flow and back navigation
- **2025-01-23**: Route changed from /main-chat to /main (user wants to avoid confusion with /chat)
- **2025-01-23**: Removed 9:30 time display and battery indicator from interface (user request for cleaner UI)
- **2025-01-23**: Created shared AppHeader and ChatInput components for code reuse across /main and /chat pages
- **2025-01-23**: Fixed header and chat input positioning - both now stay visible during scroll
- **2025-01-23**: Created calendar page with Korean date navigation, tabs (전체, 레벨1-3), and event listings
- **2025-01-23**: Added calendar icon to ChatInput component - clicking opens /calendar page
- **2025-01-23**: Implemented calendar functionality with FOMC events, GDP announcements, and today's schedule
- **2025-01-23**: Redesigned calendar page to match Figma design with diamond icons, star ratings, and "자세히 보기" buttons
- **2025-01-23**: Added difficulty levels with gem icons (💎) and stock impact ratings (⭐⭐⭐)
- **2025-01-23**: Implemented grouped date layout with financial event titles and descriptions
- **2025-01-23**: Created Level Up popup modal - clicking CAFFY logo triggers modal with dark overlay
- **2025-01-23**: Added interactive CAFFY header button with Level 3 achievement popup display
- **2025-01-23**: Created Interest page (관심러) with user level card, progress bars, and menu items
- **2025-01-23**: Added clickable 관심러 button in header navigation to /profile route
- **2025-01-23**: Fixed profile page layout - prevented content overlap with fixed header
- **2025-01-23**: Added menu navigation - 챗봇 대화 → /main, 증권 캘린더 → /calendar
- **2025-01-23**: Renamed HomePage to MainPage and InterestPage to ProfilePage for clarity
- **2025-01-23**: Added logout functionality - clicking logout button redirects to /login page

## User Preferences
- Follow fullstack_js development guidelines
- Maintain modern web application patterns
- Use client/server separation for security
- Prefer in-memory storage over databases unless specifically requested

## Development
- Run `npm run dev` to start the development server
- Frontend and backend served on port 5000 (not firewalled)
- Hot reload enabled for both client and server code
- Server uses `0.0.0.0` binding for Replit compatibility