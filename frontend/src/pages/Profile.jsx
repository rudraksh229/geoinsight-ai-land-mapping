import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import NotificationToast from '../components/NotificationToast';

const Profile = () => {
  const { user, logout, changePassword, updateProfile } = useAuth();
  
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(user?.name || '');
  const [organization, setOrganization] = useState(user?.organization || '');

  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isUpdatingPassword, setIsUpdatingPassword] = useState(false);

  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');

  const showToast = (message, type = 'success') => {
    setToastMessage(message);
    setToastType(type);
  };

  const handleUpdateProfile = (e) => {
    e.preventDefault();
    if (!name || !organization) {
      showToast('Name and Organization cannot be empty.', 'error');
      return;
    }
    updateProfile({ name, organization });
    setIsEditing(false);
    showToast('Profile information updated successfully.', 'success');
  };

  const handleChangePasswordSubmit = async (e) => {
    e.preventDefault();
    if (!oldPassword || !newPassword || !confirmPassword) {
      showToast('Please fill out all password fields.', 'error');
      return;
    }
    if (newPassword !== confirmPassword) {
      showToast('New passwords do not match.', 'error');
      return;
    }
    if (newPassword.length < 6) {
      showToast('Password must be at least 6 characters.', 'error');
      return;
    }

    setIsUpdatingPassword(true);
    try {
      await changePassword(oldPassword, newPassword);
      showToast('Security credentials updated successfully.', 'success');
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      showToast(err.message || 'Error updating password. Verify old password.', 'error');
    } finally {
      setIsUpdatingPassword(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      {/* User Information Panel */}
      <div className="lg:col-span-1 space-y-6">
        <div className="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl p-6 shadow-xs flex flex-col items-center text-center relative overflow-hidden transition-colors duration-300">
          {/* Top backdrop badge */}
          <div className="absolute top-0 inset-x-0 h-2 bg-green-600" />
          
          {/* Avatar */}
          <div className="w-20 h-20 rounded-full bg-gradient-to-tr from-green-700 to-emerald-600 text-white font-extrabold text-2xl flex items-center justify-center uppercase shadow-md mb-4 mt-2 border-2 border-white dark:border-slate-900 ring-4 ring-green-50 dark:ring-green-950/20">
            {user?.name ? user.name.split(' ').map(n => n[0]).join('').substring(0, 2) : 'NR'}
          </div>

          <h3 className="text-base font-bold text-slate-800 dark:text-slate-100 tracking-tight leading-tight">{user?.name}</h3>
          <p className="text-[10px] font-bold text-green-600 dark:text-green-400 uppercase tracking-widest mt-1.5">{user?.role || 'GIS Specialist'}</p>
          
          <hr className="w-full my-5 border-slate-100 dark:border-slate-800" />

          <div className="w-full text-left space-y-4">
            <div>
              <span className="text-[9px] text-slate-400 dark:text-slate-500 font-bold uppercase tracking-widest block">Official Email</span>
              <span className="text-xs font-bold text-slate-750 dark:text-slate-300 mt-1 block truncate">{user?.email}</span>
            </div>
            <div>
              <span className="text-[9px] text-slate-400 dark:text-slate-500 font-bold uppercase tracking-widest block">Affiliation / Department</span>
              <span className="text-xs font-bold text-slate-755 dark:text-slate-300 mt-1 block">{user?.organization}</span>
            </div>
            <div>
              <span className="text-[9px] text-slate-400 dark:text-slate-500 font-bold uppercase tracking-widest block">Joined Date</span>
              <span className="text-xs font-bold text-slate-755 dark:text-slate-300 mt-1 block">{user?.joinedDate || '2024-03-15'}</span>
            </div>
          </div>

          <button
            onClick={logout}
            className="w-full mt-6 py-2.5 border border-red-200 dark:border-red-900/30 text-red-650 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/25 rounded-xl font-bold uppercase tracking-wider text-xs transition-colors flex items-center justify-center gap-2 cursor-pointer"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
            </svg>
            Sign Out of Portal
          </button>
        </div>
      </div>

      {/* Edit Details & Security Settings Panels */}
      <div className="lg:col-span-2 space-y-6">
        
        {/* Personal Details Panel */}
        <div className="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl p-6 shadow-xs transition-colors duration-300">
          <div className="flex justify-between items-center mb-5">
            <div>
              <h4 className="text-base font-bold text-slate-800 dark:text-slate-200 tracking-tight">Administrative Profile</h4>
              <p className="text-xs text-slate-400 dark:text-slate-500 font-semibold mt-1">Review or update your official officer listings</p>
            </div>
            {!isEditing ? (
              <button
                onClick={() => setIsEditing(true)}
                className="px-4 py-2 border border-slate-200 dark:border-slate-800 hover:border-slate-350 dark:hover:border-slate-650 text-slate-600 dark:text-slate-400 rounded-xl text-xs font-bold uppercase tracking-wider transition-colors cursor-pointer"
              >
                Edit Profile
              </button>
            ) : (
              <div className="flex gap-2">
                <button
                  onClick={() => setIsEditing(false)}
                  className="px-3.5 py-2 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-605 dark:text-slate-400 rounded-xl text-xs font-bold uppercase tracking-wider transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpdateProfile}
                  className="px-3.5 py-2 bg-green-600 hover:bg-green-700 text-white rounded-xl text-xs font-bold uppercase tracking-wider shadow-xs transition-colors cursor-pointer"
                >
                  Save Changes
                </button>
              </div>
            )}
          </div>

          <form onSubmit={handleUpdateProfile} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label htmlFor="profile-name" className="block text-[9px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-1.5">Full Name</label>
                <input
                  id="profile-name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  disabled={!isEditing}
                  className="w-full text-xs font-semibold py-2.5 px-3 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 focus:border-green-600 focus:bg-white dark:focus:bg-slate-950 rounded-xl outline-hidden text-slate-700 dark:text-slate-300 disabled:bg-slate-100/50 dark:disabled:bg-slate-950/50 disabled:text-slate-500 dark:disabled:text-slate-500"
                />
              </div>
              <div>
                <label htmlFor="profile-org" className="block text-[9px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-1.5">Government Department</label>
                <input
                  id="profile-org"
                  type="text"
                  value={organization}
                  onChange={(e) => setOrganization(e.target.value)}
                  disabled={!isEditing}
                  className="w-full text-xs font-semibold py-2.5 px-3 bg-slate-50 dark:bg-slate-955 border border-slate-202 dark:border-slate-808 focus:border-green-600 focus:bg-white dark:focus:bg-slate-950 rounded-xl outline-hidden text-slate-700 dark:text-slate-300 disabled:bg-slate-100/50 dark:disabled:bg-slate-955/50 disabled:text-slate-500 dark:disabled:text-slate-500"
                />
              </div>
            </div>
          </form>
        </div>

        {/* Security Credentials Password Reset */}
        <div className="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl p-6 shadow-xs transition-colors duration-300">
          <div>
            <h4 className="text-base font-bold text-slate-800 dark:text-slate-200 tracking-tight">Security Credentials</h4>
            <p className="text-xs text-slate-400 dark:text-slate-500 font-semibold mt-1">Update your cryptographic access token or portal password</p>
          </div>
          
          <hr className="my-5 border-slate-100 dark:border-slate-800" />

          <form onSubmit={handleChangePasswordSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label htmlFor="old-pass" className="block text-[9px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-1.5">Current Password</label>
                <input
                  id="old-pass"
                  type="password"
                  value={oldPassword}
                  onChange={(e) => setOldPassword(e.target.value)}
                  className="w-full text-xs font-semibold py-2.5 px-3 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 focus:border-green-600 focus:bg-white dark:focus:bg-slate-955 rounded-xl outline-hidden text-slate-705 dark:text-slate-300"
                  placeholder="••••••••"
                  required
                />
              </div>
              
              <div>
                <label htmlFor="new-pass" className="block text-[9px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-1.5">New Password</label>
                <input
                  id="new-pass"
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full text-xs font-semibold py-2.5 px-3 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 focus:border-green-600 focus:bg-white dark:focus:bg-slate-955 rounded-xl outline-hidden text-slate-705 dark:text-slate-300"
                  placeholder="At least 6 chars"
                  required
                />
              </div>

              <div>
                <label htmlFor="confirm-pass" className="block text-[9px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-1.5">Confirm New Password</label>
                <input
                  id="confirm-pass"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full text-xs font-semibold py-2.5 px-3 bg-slate-50 dark:bg-slate-955 border border-slate-202 dark:border-slate-800 focus:border-green-600 focus:bg-white dark:focus:bg-slate-955 rounded-xl outline-hidden text-slate-705 dark:text-slate-300"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <div className="flex justify-end mt-6">
              <button
                type="submit"
                disabled={isUpdatingPassword}
                className="bg-green-650 hover:bg-green-700 disabled:bg-slate-300 dark:disabled:bg-slate-850 text-white font-bold py-2.5 px-5 rounded-xl uppercase tracking-wider text-xs shadow-xs hover:shadow-md transition-all flex items-center gap-1.5 cursor-pointer disabled:cursor-not-allowed"
              >
                {isUpdatingPassword ? (
                  <>
                    <svg className="animate-spin h-3.5 w-3.5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Updating Credentials...
                  </>
                ) : (
                  'Change Password'
                )}
              </button>
            </div>
          </form>
        </div>

      </div>

      {toastMessage && (
        <NotificationToast
          message={toastMessage}
          type={toastType}
          onClose={() => setToastMessage('')}
        />
      )}
    </div>
  );
};

export default Profile;
