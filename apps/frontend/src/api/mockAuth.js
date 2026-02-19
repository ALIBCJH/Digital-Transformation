// Mock users database
const MOCK_USERS = [
  {
    id: 1,
    email: 'demo@example.com',
    password: 'password123',
    firstName: 'Simon',
    lastName: 'Juma',
    role: 'superadmin',
  },
  {
    id: 2,
    email: 'admin@example.com',
    password: 'admin123',
    firstName: 'Admin',
    lastName: 'User',
    role: 'admin',
  },
];

// Mock authentication service
export const mockAuth = {
  login: (email, password) => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const user = MOCK_USERS.find(
          (u) => u.email === email && u.password === password
        );

        if (user) {
          const { password: _, ...userWithoutPassword } = user;
          const mockToken = btoa(JSON.stringify(userWithoutPassword));
          
          resolve({
            access: mockToken,
            refresh: mockToken,
            user: userWithoutPassword,
          });
        } else {
          reject(new Error('Invalid email or password'));
        }
      }, 500); // Simulate network delay
    });
  },

  signup: (userData) => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        // Check if email already exists
        const existingUser = MOCK_USERS.find((u) => u.email === userData.email);
        
        if (existingUser) {
          reject(new Error('Email already exists'));
          return;
        }

        // Create new user
        const newUser = {
          id: MOCK_USERS.length + 1,
          ...userData,
        };

        MOCK_USERS.push(newUser);

        const { password: _, ...userWithoutPassword } = newUser;
        const mockToken = btoa(JSON.stringify(userWithoutPassword));

        resolve({
          access: mockToken,
          refresh: mockToken,
          user: userWithoutPassword,
        });
      }, 500); // Simulate network delay
    });
  },

  getCurrentUser: () => {
    const token = localStorage.getItem('access_token');
    if (!token) return null;

    try {
      const userData = JSON.parse(atob(token));
      return userData;
    } catch (e) {
      return null;
    }
  },
};
