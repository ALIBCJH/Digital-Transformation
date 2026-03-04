import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService, altarService } from '../api/services';

const Signup = () => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email_or_phone: '',
    altar: '',
    password: '',
    password2: '',
  });
  const [altars, setAltars] = useState([]);
  const [loadingAltars, setLoadingAltars] = useState(true);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Fetch altars on component mount
  useEffect(() => {
    const fetchAltars = async () => {
      try {
        const response = await altarService.list();
        setAltars(response.altars || response.results || response || []);
      } catch (err) {
        console.error('Failed to load altars:', err);
        // Altars require authentication, so we'll let users type the altar name
        setAltars([]);
      } finally {
        setLoadingAltars(false);
      }
    };
    fetchAltars();
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.password2) {
      setError('Passwords do not match');
      return;
    }

    if (!formData.altar) {
      setError('Please select an altar');
      return;
    }

    setLoading(true);

    try {
      const response = await authService.register(formData);
      
      // Store tokens and user data
      localStorage.setItem('access_token', response.access);
      localStorage.setItem('refresh_token', response.refresh);
      localStorage.setItem('user', JSON.stringify(response.user));
      
      // Route to admin dashboard for regular admins
      navigate('/admin');
    } catch (err) {
      setError(err.message || 'Failed to create account. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-gray-50 to-blue-100 px-4 py-12">
      <div className="max-w-md w-full space-y-8">
    

        {/* Signup Form */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-blue-100">
          <h3 className="text-2xl font-semibold text-gray-800 mb-6 text-center">
            Create Your Account
          </h3>

          {error && (
            <div className="bg-red-50 border border-red-300 text-red-700 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="first_name" className="block text-sm font-semibold text-gray-700 mb-2">
                  First Name
                </label>
                <input
                  id="first_name"
                  name="first_name"
                  type="text"
                  required
                  value={formData.first_name}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-400 transition-all"
                  placeholder="John"
                />
              </div>

              <div>
                <label htmlFor="last_name" className="block text-sm font-semibold text-gray-700 mb-2">
                  Last Name
                </label>
                <input
                  id="last_name"
                  name="last_name"
                  type="text"
                  required
                  value={formData.last_name}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-400 transition-all"
                  placeholder="Doe"
                />
              </div>
            </div>

            <div>
              <label htmlFor="email_or_phone" className="block text-sm font-semibold text-gray-700 mb-2">
                Email or Phone Number
              </label>
              <input
                id="email_or_phone"
                name="email_or_phone"
                type="text"
                required
                value={formData.email_or_phone}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-400 transition-all"
                placeholder="you@example.com or +254700123456"
              />
            </div>

            <div>
              <label htmlFor="altar" className="block text-sm font-semibold text-gray-700 mb-2">
                Altar
              </label>
              {altars.length > 0 ? (
                <select
                  id="altar"
                  name="altar"
                  required
                  value={formData.altar}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 transition-all"
                  disabled={loadingAltars}
                >
                  <option value="">Select an altar...</option>
                  {altars.map((altar) => (
                    <option key={altar.id} value={altar.name}>
                      {altar.name} - {altar.city}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  id="altar"
                  name="altar"
                  type="text"
                  required
                  value={formData.altar}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-400 transition-all"
                  placeholder="e.g., Nairobi Central Church, Mombasa Fellowship..."
                  disabled={loadingAltars}
                />
              )}
              {!loadingAltars && altars.length === 0 && (
                <p className="text-xs text-blue-600 mt-2 bg-blue-50 p-2 rounded border border-blue-200">
                  ✨ Enter the name of your altar - it will be created automatically if it doesn't exist yet!
                </p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-semibold text-gray-700 mb-2">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={formData.password}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-400 transition-all"
                placeholder="••••••••"
              />
            </div>

            <div>
              <label htmlFor="password2" className="block text-sm font-semibold text-gray-700 mb-2">
                Confirm Password
              </label>
              <input
                id="password2"
                name="password2"
                type="password"
                required
                value={formData.password2}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-400 transition-all"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-lg text-sm font-semibold text-white bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02]"
            >
              {loading ? 'Creating account...' : 'Sign up'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <Link to="/login" className="font-semibold text-blue-600 hover:text-blue-700 transition-colors">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Signup;
