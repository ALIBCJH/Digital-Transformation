"""
Middleware for Django Admin access control.
Enforces that only the 3 authorized super admins can access the admin site.
"""

from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse

# Hardcoded list of authorized super admin emails (must match admin.py)
ALLOWED_SUPERADMIN_EMAILS = [
    "superadmin1@example.com",  # Replace with actual email
    "superadmin2@example.com",  # Replace with actual email
    "superadmin3@example.com",  # Replace with actual email
]


class SuperAdminAccessMiddleware:
    """
    Middleware to restrict Django Admin access to only authorized super admins.
    
    This middleware checks every request to the /admin/ path and ensures only
    users with emails in the ALLOWED_SUPERADMIN_EMAILS list can proceed.
    
    All other users (including regular staff) are blocked with a 403 Forbidden.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if this is an admin request
        if request.path.startswith('/admin/'):
            # Allow login page and logout
            if request.path in ['/admin/login/', '/admin/logout/']:
                return self.get_response(request)
            
            # Check if user is authenticated
            if not request.user.is_authenticated:
                # Let Django's auth redirect to login
                return self.get_response(request)
            
            # Check if user is in the allowed list
            if request.user.email not in ALLOWED_SUPERADMIN_EMAILS:
                # Block access with a clear message
                messages.error(
                    request,
                    "🚫 Access Denied: You are not authorized to access the Django Admin. "
                    "Only designated Super Administrators can access this area."
                )
                
                # Return 403 Forbidden
                return HttpResponseForbidden(
                    """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Access Denied</title>
                        <style>
                            body {
                                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                height: 100vh;
                                margin: 0;
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            }
                            .container {
                                text-align: center;
                                background: white;
                                padding: 3rem;
                                border-radius: 10px;
                                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                                max-width: 500px;
                            }
                            h1 {
                                color: #dc3545;
                                margin: 0 0 1rem 0;
                                font-size: 2.5rem;
                            }
                            p {
                                color: #6c757d;
                                margin: 1rem 0;
                                line-height: 1.6;
                            }
                            .icon {
                                font-size: 5rem;
                                margin-bottom: 1rem;
                            }
                            .details {
                                background: #f8f9fa;
                                padding: 1rem;
                                border-radius: 5px;
                                margin-top: 1.5rem;
                                font-size: 0.9rem;
                            }
                            a {
                                color: #667eea;
                                text-decoration: none;
                                font-weight: bold;
                            }
                            a:hover {
                                text-decoration: underline;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="icon">🚫</div>
                            <h1>Access Denied</h1>
                            <p>
                                <strong>You are not authorized to access the Django Admin panel.</strong>
                            </p>
                            <p>
                                Only designated Super Administrators have access to this area.
                                If you believe you should have access, please contact your system administrator.
                            </p>
                            <div class="details">
                                <strong>Your Account:</strong><br>
                                """ + f"{request.user.username} ({request.user.email})" + """<br><br>
                                <strong>Reason:</strong> Your email is not in the authorized list.
                            </div>
                            <p style="margin-top: 2rem;">
                                <a href="/">← Return to Home</a>
                            </p>
                        </div>
                    </body>
                    </html>
                    """
                )
        
        # Process the request normally
        response = self.get_response(request)
        return response
