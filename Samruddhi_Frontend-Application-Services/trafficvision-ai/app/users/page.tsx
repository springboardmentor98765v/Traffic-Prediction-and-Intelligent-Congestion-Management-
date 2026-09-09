'use client';

import React, { useEffect, useState } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { Header } from '@/components/Header';
import { UserPlus, Shield, Trash2, Edit, X } from 'lucide-react';

interface UserItem {
  id: string;
  name: string;
  email: string;
  role: 'Admin' | 'Traffic Operator' | 'Public';
  status: 'Active' | 'Inactive';
}

const defaultUsers: UserItem[] = [
  {
    id: '1',
    name: 'Samriddhi',
    email: 'samruddhiphadkule@gmail.com',
    role: 'Admin',
    status: 'Active',
  },
  {
    id: '2',
    name: 'Maskan',
    email: 'maskan.operator@trafficvision.ai',
    role: 'Traffic Operator',
    status: 'Active',
  },
  {
    id: '3',
    name: 'Gargi',
    email: 'gargi.public@gmail.com',
    role: 'Public',
    status: 'Inactive',
  },
];

export default function UsersPage() {
  const [role, setRole] = useState('Admin');
  const [username, setUsername] = useState('USER');
  const [usersList, setUsersList] = useState<UserItem[]>([]);

  // Modal states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<UserItem | null>(null);

  // Form states
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [userRole, setUserRole] = useState<'Admin' | 'Traffic Operator' | 'Public'>('Public');
  const [userStatus, setUserStatus] = useState<'Active' | 'Inactive'>('Active');

  useEffect(() => {
    setRole(localStorage.getItem('userRole') || 'Admin');
    setUsername(localStorage.getItem('username') || 'USER');

    const savedUsers = localStorage.getItem('app_users');
    if (savedUsers && !savedUsers.includes('Maskan')) {
      localStorage.setItem('app_users', JSON.stringify(defaultUsers));
      setUsersList(defaultUsers);
    } else if (savedUsers) {
      setUsersList(JSON.parse(savedUsers));
    } else {
      setUsersList(defaultUsers);
      localStorage.setItem('app_users', JSON.stringify(defaultUsers));
    }
  }, []);

  const saveToLocalStorage = (updated: UserItem[]) => {
    setUsersList(updated);
    localStorage.setItem('app_users', JSON.stringify(updated));
  };

  const handleOpenAddModal = () => {
    setEditingUser(null);
    setName('');
    setEmail('');
    setUserRole('Public');
    setUserStatus('Active');
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (user: UserItem) => {
    setEditingUser(user);
    setName(user.name);
    setEmail(user.email);
    setUserRole(user.role);
    setUserStatus(user.status);
    setIsModalOpen(true);
  };

  const handleSaveUser = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !email.trim()) return;

    if (editingUser) {
      const updated = usersList.map((u) =>
        u.id === editingUser.id
          ? { ...u, name, email, role: userRole, status: userStatus }
          : u
      );
      saveToLocalStorage(updated);
    } else {
      const newUser: UserItem = {
        id: Date.now().toString(),
        name,
        email,
        role: userRole,
        status: userStatus,
      };
      saveToLocalStorage([...usersList, newUser]);
    }

    setIsModalOpen(false);
  };

  const handleDeleteUser = (id: string) => {
    if (confirm('Are you sure you want to delete this user?')) {
      const updated = usersList.filter((u) => u.id !== id);
      saveToLocalStorage(updated);
    }
  };

  return (
    <div className="flex min-h-screen bg-[#1c1d28] text-white">
      <Sidebar role={role} />

      <main className="flex-1 p-8 overflow-y-auto">
        <Header username={username} role={role} />

        <div className="space-y-6 max-w-6xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">System User Management</h1>
              <p className="text-xs text-gray-400 mt-1">
                Manage platform administrative roles, operator access rights, and active user accounts.
              </p>
            </div>
            <button
              onClick={handleOpenAddModal}
              className="bg-[#a855f7] hover:bg-[#9333ea] text-white text-xs font-bold px-4 py-2.5 rounded-xl flex items-center gap-2 transition-all shadow-lg hover:shadow-purple-500/20"
            >
              <UserPlus size={16} /> + Add New User
            </button>
          </div>

          <div className="bg-[#25283c] border border-white/5 rounded-2xl p-6 shadow-xl space-y-4">
            <h2 className="text-base font-bold text-white">Registered Accounts</h2>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-white/10 text-xs font-semibold text-gray-400 uppercase">
                    <th className="py-3 px-4">User</th>
                    <th className="py-3 px-4">Role</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {usersList.map((user) => (
                    <tr key={user.id} className="hover:bg-white/5 transition-colors">
                      <td className="py-4 px-4">
                        <p className="font-bold text-white text-sm">{user.name}</p>
                        <p className="text-xs text-gray-400">{user.email}</p>
                      </td>
                      <td className="py-4 px-4">
                        <span className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1 rounded-full bg-white/5 text-gray-200 border border-white/10">
                          <Shield size={12} className="text-[#00d2ff]" /> {user.role}
                        </span>
                      </td>
                      <td className="py-4 px-4">
                        <span
                          className={`text-xs px-2.5 py-0.5 rounded-full font-semibold ${
                            user.status === 'Active'
                              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                              : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          }`}
                        >
                          {user.status}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleOpenEditModal(user)}
                            className="p-2 hover:bg-white/10 rounded-lg text-gray-300 hover:text-white transition-colors"
                            title="Edit User"
                          >
                            <Edit size={16} />
                          </button>
                          <button
                            onClick={() => handleDeleteUser(user.id)}
                            className="p-2 hover:bg-rose-500/20 rounded-lg text-rose-400 transition-colors"
                            title="Delete User"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {usersList.length === 0 && (
                    <tr>
                      <td colSpan={4} className="text-center py-8 text-xs text-gray-400">
                        No users registered in system.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>

      {/* Add / Edit User Modal Overlay */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-[#25283c] border border-white/10 w-full max-w-md rounded-2xl p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h3 className="font-bold text-lg text-white">
                {editingUser ? 'Edit System User' : 'Add New User'}
              </h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSaveUser} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                  Full Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. John Doe"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-[#1c1d28] border border-white/10 text-white p-3 rounded-xl text-sm focus:outline-none focus:border-[#a855f7]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                  Email Address
                </label>
                <input
                  type="email"
                  required
                  placeholder="user@trafficvision.ai"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-[#1c1d28] border border-white/10 text-white p-3 rounded-xl text-sm focus:outline-none focus:border-[#a855f7]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                  Role
                </label>
                <select
                  value={userRole}
                  onChange={(e) => setUserRole(e.target.value as any)}
                  className="w-full bg-[#1c1d28] border border-white/10 text-white p-3 rounded-xl text-sm focus:outline-none focus:border-[#a855f7]"
                >
                  <option value="Admin">Admin</option>
                  <option value="Traffic Operator">Traffic Operator</option>
                  <option value="Public">Public</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                  Account Status
                </label>
                <select
                  value={userStatus}
                  onChange={(e) => setUserStatus(e.target.value as any)}
                  className="w-full bg-[#1c1d28] border border-white/10 text-white p-3 rounded-xl text-sm focus:outline-none focus:border-[#a855f7]"
                >
                  <option value="Active">Active</option>
                  <option value="Inactive">Inactive</option>
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-white/10">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2.5 rounded-xl text-xs font-semibold bg-white/5 hover:bg-white/10 text-gray-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2.5 rounded-xl text-xs font-bold bg-[#a855f7] hover:bg-[#9333ea] text-white transition-colors"
                >
                  {editingUser ? 'Update User' : 'Create User'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
