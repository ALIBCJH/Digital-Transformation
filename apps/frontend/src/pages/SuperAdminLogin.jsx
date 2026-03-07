import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../api/services';

const SuperAdminLogin = () => {
  const [formData, setFormData] = useState({
    email_or_phone: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authService.login(formData.email_or_phone, formData.password);
      
      // Verify this is actually a super admin
      if (!response.user.is_superuser && !response.user.is_superadmin) {
        setError('Access Denied: This login is for Super Administrators only. Please use the regular admin login.');
        setLoading(false);
        return;
      }

      // Store tokens and user data
      localStorage.setItem('access_token', response.access);
      localStorage.setItem('refresh_token', response.refresh);
      localStorage.setItem('user', JSON.stringify(response.user));
      
      // Route to admin dashboard
      navigate('/admin');
    } catch (err) {
      setError(err.message || 'Invalid credentials. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-indigo-900 to-slate-900 px-4">
      <div className="max-w-md w-full space-y-8">
        {/* Header with Super Admin Badge */}
        <div className="text-center">
          <div className="inline-block mb-4">
            <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-2 rounded-full font-bold text-sm tracking-wide shadow-lg">
              🛡️ SUPER ADMINISTRATOR
            </div>
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">
            Global Access Portal
          </h1>
          <p className="text-purple-200 text-sm">
            Nationwide oversight and management
          </p>
        </div>

        {/* Login Form */}
        <div className="bg-white/10 backdrop-blur-md rounded-2xl shadow-2xl p-8 border border-purple-500/30">
          <div className="flex items-center justify-center mb-6">
            <div className="h-1 w-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded"></div>
            <h3 className="text-2xl font-semibold text-white mx-4">
              Sign In
            </h3>
            <div className="h-1 w-12 bg-gradient-to-r from-pink-500 to-purple-500 rounded"></div>
          </div>

          {error && (
            <div className="bg-red-500/20 border border-red-400 text-red-200 px-4 py-3 rounded-lg mb-4 backdrop-blur-sm">
              <div className="flex items-start">
                <span className="text-xl mr-2">⚠️</span>
                <span className="text-sm">{error}</span>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email_or_phone" className="block text-sm font-semibold text-purple-200 mb-2">
                Email Address
              </label>
              <input
                id="email_or_phone"
                name="email_or_phone"
                type="email"
                required
                value={formData.email_or_phone}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-white/10 border border-purple-400/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-white placeholder-purple-300/50 transition-all backdrop-blur-sm"
                placeholder="superadmin@example.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-semibold text-purple-200 mb-2">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={formData.password}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-white/10 border border-purple-400/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-white placeholder-purple-300/50 transition-all backdrop-blur-sm"
                placeholder="••••••••"
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-purple-200">
                  Remember me
                </label>
              </div>

              <div className="text-sm">
                <a href="#" className="font-semibold text-purple-300 hover:text-purple-200 transition-colors">
                  Forgot password?
                </a>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-lg text-sm font-semibold text-white bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02]"
            >
              {loading ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Authenticating...
                </span>
              ) : (
                '🔐 Sign in as Super Admin'
              )}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-purple-500/20">
            <div className="bg-purple-500/10 rounded-lg p-4 border border-purple-400/20">
              <p className="text-xs text-purple-200 leading-relaxed">
                <span className="font-semibold">ℹ️ Super Admin Access:</span> This portal is restricted to authorized super administrators only. 
                Your login credentials are provided by the system administrator. 
                Unauthorized access attempts are monitored and logged.
              </p>
            </div>
            
            <div className="mt-4 text-center">
              <p className="text-sm text-purple-300">
                Regular admin?{' '}
                <Link to="/login" className="font-semibold text-purple-200 hover:text-white transition-colors underline">
                  Go to Admin Login
                </Link>
              </p>
            </div>
          </div>
        </div>

        {/* Footer info */}
        <div className="text-center text-purple-300 text-xs">
          <p>🔒 Secured with enterprise-grade encryption</p>
        </div>
      </div>
    </div>
  );
};

export default SuperAdminLogin;
