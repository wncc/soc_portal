import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export default function URLGuard() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const authToken = localStorage.getItem('authToken');
    const role = localStorage.getItem('role');
    const path = location.pathname;
    
    // Define public paths that don't require auth
    const publicPaths = ['/', '/login', '/loading', '/p23logad'];
    const isBecomeManagerPath = /^\/become-manager\/.+$/.test(path);
    const isPublicPath = publicPaths.includes(path) || isBecomeManagerPath;
    
    // Redirect to login if no auth token on protected route
    if (!authToken && !isPublicPath) {
      console.log('[URLGuard] No auth token - redirecting to login');
      navigate('/login', { replace: true });
      return;
    }
    
    // Still loading role
    if (!role && authToken) return;
    
    // Extract domain from path if it's a domain-scoped route
    const domainMatch = path.match(/^\/([a-z]+)\/(mentor|current_projects|wishlist|PreferenceForm|PreferenceFormFilled)/);
    
    if (domainMatch) {
      const domain = domainMatch[1];
      const routeType = domainMatch[2];
      
      // Check if user has access to this domain
      const membershipsStr = localStorage.getItem('memberships');
      console.log('URLGuard - Checking access for domain:', domain);
      console.log('URLGuard - Memberships from localStorage:', membershipsStr);
      
      const memberships = JSON.parse(membershipsStr || '[]');
      console.log('URLGuard - Parsed memberships:', memberships);
      
      // Check role-based access
      const isMentorRoute = routeType === 'mentor';
      const isMenteeRoute = ['current_projects', 'wishlist', 'PreferenceForm', 'PreferenceFormFilled'].includes(routeType);
      
      // Find the appropriate membership based on route type
      let domainMembership;
      if (isMentorRoute) {
        // For mentor routes, look for mentor role specifically
        domainMembership = memberships.find(m => m.domain === domain && m.role === 'mentor');
      } else if (isMenteeRoute) {
        // For mentee routes, look for mentee role specifically
        domainMembership = memberships.find(m => m.domain === domain && m.role === 'mentee');
      } else {
        // For other routes, just check domain membership
        domainMembership = memberships.find(m => m.domain === domain);
      }
      
      console.log('URLGuard - Found membership for', domain, ':', domainMembership);
      
      if (!domainMembership) {
        // User is not a member of this domain with the required role
        console.warn('URLGuard - No', isMentorRoute ? 'mentor' : isMenteeRoute ? 'mentee' : '', 'membership found for domain:', domain, '- Redirecting to home');
        navigate('/', { replace: true });
        return;
      }
      
      console.log('URLGuard - Access granted for', domain, 'as', domainMembership.role);
      return; // Allow access
    }
    
    // Legacy routes
    const mentorRoutes = ['/mentor/home', '/mentor/add-project', '/mentor/edit-project'];
    const menteeRoutes = ['/PreferenceFormFilled', '/current_projects', '/wishlist', '/PreferenceForm'];
    const authRoutes = ['/login', '/p23logad', '/loading'];
    const managerRoutes = ['/', '/manager', '/become-manager'];
    
    const normalizedPath = path.replace(/\/+$/, '');
    const isProjectDetails = /^\/current_projects\/[^/]+$/.test(path) || /^\/[a-z]+\/current_projects\/[^/]+$/.test(path);
    const isBecomeManagerPath2 = /^\/become-manager\/.+$/.test(path);
    
    // Allow manager and public routes
    if (managerRoutes.includes(normalizedPath) || isBecomeManagerPath2) return;
    
    // Allow auth routes
    if (authRoutes.includes(normalizedPath)) return;
    
    // Allow project details
    if (isProjectDetails) return;
    
    // Check role-based access for legacy routes
    if (role === 'mentee' && mentorRoutes.includes(normalizedPath)) {
      navigate('/', { replace: true });
    } else if (role === 'mentor' && menteeRoutes.includes(normalizedPath)) {
      navigate('/', { replace: true });
    }
  }, [location.pathname, navigate]);

  return null;
}
