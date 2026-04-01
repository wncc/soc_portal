import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export default function URLGuard() {
  const navigate = useNavigate();
  const location = useLocation();
  const role = localStorage.getItem('role');

  useEffect(() => {
    if (!role) return;

    const path = location.pathname;
    
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
    
    // Allow legacy routes
    const mentorRoutes = ['/mentor/home', '/mentor/add-project', '/mentor/edit-project'];
    const menteeRoutes = ['/PreferenceFormFilled', '/current_projects', '/wishlist', '/PreferenceForm'];
    const authRoutes = ['/login', '/p23logad', '/loading'];
    const publicRoutes = ['/', '/manager', '/become-manager'];
    
    const normalizedPath = path.replace(/\/+$/, '');
    const isProjectDetailsRoute = /^\/current_projects\/[^/]+$/.test(path) || /^\/[a-z]+\/current_projects\/[^/]+$/.test(path);
    const isBecomeManagerRoute = /^\/become-manager\/.+$/.test(path);
    
    // Allow public routes
    if (publicRoutes.includes(normalizedPath) || isBecomeManagerRoute) return;
    
    // Allow auth routes
    if (authRoutes.includes(normalizedPath)) return;
    
    // Allow project details
    if (isProjectDetailsRoute) return;
    
    // Check role-based access for legacy routes
    if (role === 'mentee' && mentorRoutes.includes(normalizedPath)) {
      navigate('/', { replace: true });
    } else if (role === 'mentor' && menteeRoutes.includes(normalizedPath)) {
      navigate('/', { replace: true });
    }
  }, [location.pathname, role, navigate]);

  return null;
}
