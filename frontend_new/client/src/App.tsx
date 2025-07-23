import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/not-found";

import { Element } from "@/pages/Element";
import { LoginPage } from "@/pages/LoginPage";
import { MainPage } from "@/pages/MainPage";
import { ChatPage } from "@/pages/ChatPage";
import { CalendarPage } from "@/pages/CalendarPage";
import { ProfilePage } from "@/pages/ProfilePage";

function Router() {
  return (
    <Switch>
      {/* Add pages below */}
      <Route path="/" component={Element} />
      <Route path="/login" component={LoginPage} />
      <Route path="/main" component={MainPage} />
      <Route path="/chat" component={ChatPage} />
      <Route path="/calendar" component={CalendarPage} />
      <Route path="/profile" component={ProfilePage} />
      {/* Fallback to 404 */}
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Router />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
