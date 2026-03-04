import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService, memberService, altarService, guestService } from '../api/services';

const AdminDashboard = () => {
  const [user, setUser] = useState(null);
  const [activeSection, setActiveSection] = useState('overview');
  const [members, setMembers] = useState([]);
  const [altars, setAltars] = useState([]);
  const [loading, setLoading] = useState(false);
  const [attendance, setAttendance] = useState({});
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState(''); // 'member', 'guest', 'offboard'
  const navigate = useNavigate();

  // Form states
  const [memberForm, setMemberForm] = useState({
    full_name: '',
    phone_number: '',
    gender: '',
    home_altar: '',
  });

  const [guestForm, setGuestForm] = useState({
    full_name: '',
    phone_number: '',
    gender: '',
    visiting_from: '',
    home_altar: '',
  });

  const [transferForm, setTransferForm] = useState({
    member_id: null,
    to_altar_id: null,
    reason: '',
    notes: '',
  });

  useEffect(() => {
    const currentUser = authService.getCurrentUser();
    if (!currentUser) {
      navigate('/login');
    } else {
      setUser(currentUser);
      loadData();
    }
  }, [navigate]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [membersData, altarsData] = await Promise.all([
        memberService.list(),
        altarService.list()
      ]);
      setMembers(membersData.results || membersData || []);
      setAltars(altarsData.altars || altarsData.results || altarsData || []);
      
      // Initialize attendance tracking
      const initialAttendance = {};
      (membersData.results || membersData || []).forEach(member => {
        initialAttendance[member.id] = false;
      });
      setAttendance(initialAttendance);
    } catch (error) {
      console.error('Data Load Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) await authService.logout(refreshToken).catch(() => {});
    localStorage.clear();
    navigate('/login');
  };

  const toggleAttendance = (memberId) => {
    setAttendance(prev => ({
      ...prev,
      [memberId]: !prev[memberId]
    }));
  };

  const getPresentCount = () => {
    return Object.values(attendance).filter(present => present).length;
  };

  const getAbsentCount = () => {
    return members.length - getPresentCount();
  };

  const openModal = (type, memberId = null) => {
    setModalType(type);
    setShowModal(true);
    if (type === 'offboard' && memberId) {
      setTransferForm({ ...transferForm, member_id: memberId });
    }
  };

  const closeModal = () => {
    setShowModal(false);
    setModalType('');
    // Reset forms
    setMemberForm({
      full_name: '',
      phone_number: '',
      gender: '',
      home_altar: '',
    });
    setGuestForm({
      full_name: '',
      phone_number: '',
      gender: '',
      visiting_from: '',
      home_altar: '',
    });
    setTransferForm({
      member_id: null,
      to_altar_id: null,
      reason: '',
      notes: '',
    });
  };

  const handleMemberSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await memberService.create(memberForm);
      alert('Member registered successfully!');
      closeModal();
      loadData(); // Reload data
    } catch (error) {
      console.error('Error creating member:', error);
      const errorMsg = error.response?.data?.error || error.response?.data?.home_altar?.[0] || 'Failed to register member. Please try again.';
      alert(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleGuestSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await guestService.create(guestForm);
      alert('Guest registered successfully!');
      closeModal();
    } catch (error) {
      console.error('Error registering guest:', error);
      // Check if it's a 404 error (endpoint not found)
      if (error.response?.status === 404 || error.message.includes('<!DOCTYPE')) {
        alert('Guest registration endpoint is not yet enabled on the backend. Please contact the administrator.');
      } else {
        const errorMsg = error.response?.data?.error || 'Failed to register guest. Please try again.';
        alert(errorMsg);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleOffboard = async () => {
    if (!transferForm.member_id) return;
    
    if (!transferForm.reason) {
      alert('Please select a transfer reason.');
      return;
    }

    if (!confirm('Are you sure you want to offboard this member? This will deactivate their account.')) {
      return;
    }

    setLoading(true);
    try {
      // For offboarding, we send member_id, reason, and optionally to_altar_id (null for offboard)
      const transferData = {
        member_id: transferForm.member_id,
        to_altar_id: transferForm.to_altar_id || null, // null means offboard
        reason: transferForm.reason,
        notes: transferForm.notes || '',
      };
      
      await memberService.transfer(transferData);
      alert('Member offboarded successfully!');
      closeModal();
      loadData(); // Reload data
    } catch (error) {
      console.error('Error offboarding member:', error);
      const errorMsg = error.response?.data?.error || 'Failed to offboard member. Please try again.';
      alert(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  // Get primary altar info
  const primaryAltar = altars.length > 0 ? altars[0] : null;

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Enhanced Navigation Bar */}
      <nav className="bg-white shadow-lg border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-8">
          <div className="flex justify-between items-center h-20">
            {/* Navigation Tabs */}
            <div className="flex space-x-2">
              {['overview', 'attendance', 'members'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveSection(tab)}
                  className={`px-8 py-3 text-base font-semibold rounded-lg transition-all duration-300 transform ${
                    activeSection === tab 
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg scale-105' 
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100 hover:scale-102'
                  }`}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            {/* Sign Out Button */}
            <button 
              onClick={handleLogout}
              className="px-6 py-3 text-base font-semibold text-white bg-gradient-to-r from-red-500 to-red-600 rounded-lg hover:from-red-600 hover:to-red-700 shadow-md hover:shadow-lg transition-all duration-300 transform hover:scale-105"
            >
              Sign Out
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-8 py-12">
        {activeSection === 'overview' && (
          <div className="space-y-8 animate-in fade-in duration-500">
            <div className="text-center mb-12">
              <h1 className="text-4xl font-bold text-slate-900 mb-2">Dashboard Overview</h1>
              <p className="text-lg text-slate-600">Welcome, {user.first_name} {user.last_name}</p>
            </div>

            {/* Altar Information Card */}
            <div className="bg-white rounded-2xl shadow-xl p-10 border border-slate-200">
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center space-x-4">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                    <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-3xl font-bold text-slate-900">
                      {primaryAltar?.name || 'Altar Information'}
                    </h2>
                  </div>
                </div>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-blue-600 uppercase tracking-wide mb-2">Total Members</p>
                      <p className="text-4xl font-bold text-blue-900">{members.length}</p>
                    </div>
                    <div className="w-14 h-14 bg-blue-500 rounded-full flex items-center justify-center">
                      <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-green-600 uppercase tracking-wide mb-2">Active Altars</p>
                      <p className="text-4xl font-bold text-green-900">{altars.length}</p>
                    </div>
                    <div className="w-14 h-14 bg-green-500 rounded-full flex items-center justify-center">
                      <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                      </svg>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-purple-50 to-violet-50 rounded-xl p-6 border border-purple-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-purple-600 uppercase tracking-wide mb-2">Attendance Rate</p>
                      <p className="text-4xl font-bold text-purple-900">
                        {members.length > 0 ? Math.round((getPresentCount() / members.length) * 100) : 0}%
                      </p>
                    </div>
                    <div className="w-14 h-14 bg-purple-500 rounded-full flex items-center justify-center">
                      <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Action Buttons */}
            <div className="bg-white rounded-2xl shadow-xl p-10 border border-slate-200">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">Quick Actions</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Create Member Button */}
                <button
                  onClick={() => openModal('member')}
                  className="group bg-gradient-to-br from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 rounded-xl p-8 text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
                >
                  <div className="flex flex-col items-center space-y-4">
                    <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center group-hover:bg-white/30 transition-colors">
                      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                      </svg>
                    </div>
                    <div className="text-center">
                      <h3 className="text-xl font-bold mb-1">Create Member</h3>
                      <p className="text-sm text-blue-100">Register a new church member</p>
                    </div>
                  </div>
                </button>

                {/* Register Guest Button */}
                <button
                  onClick={() => openModal('guest')}
                  className="group bg-gradient-to-br from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 rounded-xl p-8 text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
                >
                  <div className="flex flex-col items-center space-y-4">
                    <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center group-hover:bg-white/30 transition-colors">
                      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <div className="text-center">
                      <h3 className="text-xl font-bold mb-1">Register Guest</h3>
                      <p className="text-sm text-green-100">Add a visitor to the registry</p>
                    </div>
                  </div>
                </button>

                {/* Offboard Member Button */}
                <button
                  onClick={() => setActiveSection('members')}
                  className="group bg-gradient-to-br from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 rounded-xl p-8 text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
                >
                  <div className="flex flex-col items-center space-y-4">
                    <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center group-hover:bg-white/30 transition-colors">
                      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7a4 4 0 11-8 0 4 4 0 018 0zM9 14a6 6 0 00-6 6v1h12v-1a6 6 0 00-6-6zM21 12h-6" />
                      </svg>
                    </div>
                    <div className="text-center">
                      <h3 className="text-xl font-bold mb-1">Offboard Member</h3>
                      <p className="text-sm text-orange-100">Remove a member from registry</p>
                    </div>
                  </div>
                </button>
              </div>
            </div>
          </div>
        )}

        {activeSection === 'attendance' && (
          <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex justify-between items-center mb-8">
              <div>
                <h1 className="text-4xl font-bold text-slate-900 mb-2">Attendance Register</h1>
                <p className="text-lg text-slate-600">Mark members as present or absent</p>
              </div>
              <div className="flex space-x-4">
                <div className="bg-white rounded-xl px-6 py-3 shadow-md border border-green-200">
                  <p className="text-sm text-slate-600 font-medium">Present</p>
                  <p className="text-2xl font-bold text-green-600">{getPresentCount()}</p>
                </div>
                <div className="bg-white rounded-xl px-6 py-3 shadow-md border border-red-200">
                  <p className="text-sm text-slate-600 font-medium">Absent</p>
                  <p className="text-2xl font-bold text-red-600">{getAbsentCount()}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-200">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-gradient-to-r from-slate-50 to-slate-100 border-b-2 border-slate-200">
                      <th className="px-8 py-5 text-left text-sm font-bold text-slate-700 uppercase tracking-wider">Member Name</th>
                      <th className="px-8 py-5 text-left text-sm font-bold text-slate-700 uppercase tracking-wider">Phone Number</th>
                      <th className="px-8 py-5 text-left text-sm font-bold text-slate-700 uppercase tracking-wider">Altar</th>
                      <th className="px-8 py-5 text-center text-sm font-bold text-slate-700 uppercase tracking-wider">
                        <div className="flex justify-center items-center space-x-8">
                          <div className="flex items-center space-x-2">
                            <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                            </svg>
                            <span className="text-green-600">Present</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                            <span className="text-red-600">Absent</span>
                          </div>
                        </div>
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {members.length > 0 ? (
                      members.map((member) => (
                        <tr key={member.id} className="hover:bg-slate-50 transition-colors duration-200">
                          <td className="px-8 py-5">
                            <div className="flex items-center space-x-4">
                              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white font-bold text-lg shadow-md">
                                {member.full_name?.charAt(0) || '?'}
                              </div>
                              <div className="text-base font-semibold text-slate-900">
                                {member.full_name || 'N/A'}
                              </div>
                            </div>
                          </td>
                          <td className="px-8 py-5 text-base text-slate-600">
                            {member.phone_number || 'N/A'}
                          </td>
                          <td className="px-8 py-5 text-base text-slate-600">
                            {member.home_altar || 'N/A'}
                          </td>
                          <td className="px-8 py-5">
                            <div className="flex justify-center">
                              <button
                                onClick={() => toggleAttendance(member.id)}
                                className={`w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300 transform hover:scale-110 shadow-lg ${
                                  attendance[member.id]
                                    ? 'bg-gradient-to-br from-green-400 to-green-600 text-white'
                                    : 'bg-gradient-to-br from-red-400 to-red-600 text-white'
                                }`}
                              >
                                {attendance[member.id] ? (
                                  <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                  </svg>
                                ) : (
                                  <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
                                  </svg>
                                )}
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="4" className="px-8 py-12 text-center text-slate-500 text-lg">
                          No members found
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeSection === 'members' && (
          <div className="space-y-6 animate-in fade-in duration-500">
            <div className="mb-8">
              <h1 className="text-4xl font-bold text-slate-900 mb-2">Members Directory</h1>
              <p className="text-lg text-slate-600">View all registered members</p>
            </div>

            <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-200">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-gradient-to-r from-slate-50 to-slate-100 border-b-2 border-slate-200">
                      <th className="px-8 py-5 text-left text-sm font-bold text-slate-700 uppercase tracking-wider">Member</th>
                      <th className="px-8 py-5 text-left text-sm font-bold text-slate-700 uppercase tracking-wider">Contact</th>
                      <th className="px-8 py-5 text-left text-sm font-bold text-slate-700 uppercase tracking-wider">Altar</th>
                      <th className="px-8 py-5 text-left text-sm font-bold text-slate-700 uppercase tracking-wider">Status</th>
                      <th className="px-8 py-5 text-center text-sm font-bold text-slate-700 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {members.length > 0 ? (
                      members.map((member) => (
                        <tr key={member.id} className="hover:bg-slate-50 transition-colors duration-200">
                          <td className="px-8 py-5">
                            <div className="flex items-center space-x-4">
                              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white font-bold text-lg shadow-md">
                                {member.full_name?.charAt(0) || '?'}
                              </div>
                              <div>
                                <div className="text-base font-semibold text-slate-900">
                                  {member.full_name || 'N/A'}
                                </div>
                                <div className="text-sm text-slate-500">
                                  ID: {member.id}
                                </div>
                              </div>
                            </div>
                          </td>
                          <td className="px-8 py-5">
                            <div className="text-base text-slate-900">{member.phone_number || 'N/A'}</div>
                            <div className="text-sm text-slate-500">{member.email || 'N/A'}</div>
                          </td>
                          <td className="px-8 py-5 text-base text-slate-600">
                            {member.home_altar || 'Unassigned'}
                          </td>
                          <td className="px-8 py-5">
                            <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold bg-green-100 text-green-800 border border-green-200">
                              Active
                            </span>
                          </td>
                          <td className="px-8 py-5">
                            <div className="flex justify-center">
                              <button
                                onClick={() => openModal('offboard', member.id)}
                                className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg text-sm font-semibold transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105"
                              >
                                Offboard
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="5" className="px-8 py-16">
                          <div className="text-center">
                            <div className="mb-4">
                              <svg className="w-16 h-16 mx-auto text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                              </svg>
                            </div>
                            <h3 className="text-xl font-semibold text-slate-700 mb-2">Welcome to Your New Altar!</h3>
                            <p className="text-slate-500 mb-4">No members yet. Click "Add Member" above to start building your community.</p>
                            <button
                              onClick={() => openModal('member')}
                              className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105"
                            >
                              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                              </svg>
                              Add Your First Member
                            </button>
                          </div>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Modals */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 animate-in fade-in duration-300">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
            <div className="px-8 py-6 border-b border-slate-200 flex justify-between items-center sticky top-0 bg-white">
              <h3 className="text-2xl font-bold text-slate-900">
                {modalType === 'member' && 'Register New Member'}
                {modalType === 'guest' && 'Register Guest'}
                {modalType === 'offboard' && 'Offboard Member'}
              </h3>
              <button onClick={closeModal} className="text-slate-400 hover:text-slate-600 transition-colors">
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="px-8 py-6">
              {modalType === 'member' && (
                <form onSubmit={handleMemberSubmit} className="space-y-5">
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Full Name *</label>
                    <input
                      type="text"
                      required
                      value={memberForm.full_name}
                      onChange={(e) => setMemberForm({...memberForm, full_name: e.target.value})}
                      className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                      placeholder="e.g. John Doe"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Phone Number *</label>
                    <input
                      type="tel"
                      required
                      value={memberForm.phone_number}
                      onChange={(e) => setMemberForm({...memberForm, phone_number: e.target.value})}
                      className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                      placeholder="e.g. 0708872179"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Gender *</label>
                    <select
                      required
                      value={memberForm.gender}
                      onChange={(e) => setMemberForm({...memberForm, gender: e.target.value})}
                      className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                    >
                      <option value="">Select gender</option>
                      <option value="MALE">Male</option>
                      <option value="FEMALE">Female</option>
                      <option value="OTHER">Other</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Home Altar *</label>
                    <input
                      type="text"
                      required
                      value={memberForm.home_altar}
                      onChange={(e) => setMemberForm({...memberForm, home_altar: e.target.value})}
                      className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                      placeholder="e.g. Nyeri Main Altar"
                    />
                  </div>

                  <div className="flex justify-end space-x-3 pt-4 border-t border-slate-200">
                    <button
                      type="button"
                      onClick={closeModal}
                      className="px-6 py-3 border border-slate-300 rounded-lg text-sm font-semibold text-slate-700 hover:bg-slate-50 transition-all"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={loading}
                      className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-sm font-semibold rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
                    >
                      {loading ? 'Registering...' : 'Register Member'}
                    </button>
                  </div>
                </form>
              )}

              {modalType === 'guest' && (
                <form onSubmit={handleGuestSubmit} className="space-y-5">
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Full Name *</label>
                    <input
                      type="text"
                      required
                      value={guestForm.full_name}
                      onChange={(e) => setGuestForm({...guestForm, full_name: e.target.value})}
                      className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
                      placeholder="e.g. Malik Omondi"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Phone Number *</label>
                    <input
                      type="tel"
                      required
                      value={guestForm.phone_number}
                      onChange={(e) => setGuestForm({...guestForm, phone_number: e.target.value})}
                      className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
                      placeholder="e.g. 0723410565"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Gender *</label>
                    <select
                      required
                      value={guestForm.gender}
                      onChange={(e) => setGuestForm({...guestForm, gender: e.target.value})}
                      className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
                    >
                      <option value="">Select gender</option>
                      <option value="MALE">Male</option>
                      <option value="FEMALE">Female</option>
                      <option value="OTHER">Other</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Visiting From *</label>
                    <input
                      type="text"
                      required
                      value={guestForm.visiting_from}
                      onChange={(e) => setGuestForm({...guestForm, visiting_from: e.target.value})}
                      className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
                      placeholder="e.g. Nyeri, Nairobi, etc."
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Home Altar *</label>
                    <input
                      type="text"
                      required
                      value={guestForm.home_altar}
                      onChange={(e) => setGuestForm({...guestForm, home_altar: e.target.value})}
                      className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
                      placeholder="e.g. Nyeri Main Altar"
                    />
                  </div>

                  <div className="flex justify-end space-x-3 pt-4 border-t border-slate-200">
                    <button
                      type="button"
                      onClick={closeModal}
                      className="px-6 py-3 border border-slate-300 rounded-lg text-sm font-semibold text-slate-700 hover:bg-slate-50 transition-all"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={loading}
                      className="px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white text-sm font-semibold rounded-lg hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
                    >
                      {loading ? 'Registering...' : 'Register Guest'}
                    </button>
                  </div>
                </form>
              )}

              {modalType === 'offboard' && (
                <div className="space-y-6">
                  <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
                    <div className="flex items-start space-x-3">
                      <svg className="w-6 h-6 text-orange-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div>
                        <h4 className="text-lg font-bold text-orange-900 mb-2">Offboard Member</h4>
                        <p className="text-sm text-orange-800">
                          You are about to offboard this member. You can either transfer them to another altar or deactivate their account completely.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2">Transfer Reason *</label>
                      <select
                        required
                        value={transferForm.reason}
                        onChange={(e) => setTransferForm({...transferForm, reason: e.target.value})}
                        className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all"
                      >
                        <option value="">Select reason</option>
                        <option value="job_transfer">Job Transfer</option>
                        <option value="relocation">Relocation</option>
                        <option value="family_reasons">Family Reasons</option>
                        <option value="personal_choice">Personal Choice</option>
                        <option value="offboarding">Offboarding/Leaving</option>
                        <option value="other">Other</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2">
                        Transfer To Altar (Optional - leave empty to deactivate)
                      </label>
                      <select
                        value={transferForm.to_altar_id || ''}
                        onChange={(e) => setTransferForm({...transferForm, to_altar_id: e.target.value ? parseInt(e.target.value) : null})}
                        className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all"
                      >
                        <option value="">Deactivate (No Transfer)</option>
                        {altars.map((altar) => (
                          <option key={altar.id} value={altar.id}>
                            {altar.name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2">Notes (Optional)</label>
                      <textarea
                        rows="3"
                        value={transferForm.notes}
                        onChange={(e) => setTransferForm({...transferForm, notes: e.target.value})}
                        className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all"
                        placeholder="Additional notes about this transfer/offboarding..."
                      ></textarea>
                    </div>
                  </div>

                  <div className="flex justify-end space-x-3 pt-4 border-t border-slate-200">
                    <button
                      type="button"
                      onClick={closeModal}
                      className="px-6 py-3 border border-slate-300 rounded-lg text-sm font-semibold text-slate-700 hover:bg-slate-50 transition-all"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleOffboard}
                      disabled={loading}
                      className="px-6 py-3 bg-gradient-to-r from-orange-600 to-red-600 text-white text-sm font-semibold rounded-lg hover:from-orange-700 hover:to-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
                    >
                      {loading ? 'Processing...' : transferForm.to_altar_id ? 'Transfer Member' : 'Offboard Member'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;