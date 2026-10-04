'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Shield, User, ArrowRight, RefreshCw, UserPlus, LogIn } from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();
  const [selectedRole, setSelectedRole] = useState<'Operator' | 'Admin' | 'Public'>('Operator');
  
  // Sign In / Sign Up toggle exclusively for Public mode
  const [publicMode, setPublicMode] = useState<'signin' | 'signup'>('signin');

  // Form Fields
  const [fullName, setFullName] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [captchaInput, setCaptchaInput] = useState('');
  const [captchaCode, setCaptchaCode] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const generateCaptcha = () => {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789';
    let result = '';
    for (let i = 0; i < 6; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    setCaptchaCode(result);
  };

  useEffect(() => {
    generateCaptcha();
  }, []);

  const handleRoleChange = (role: 'Operator' | 'Admin' | 'Public') => {
    setSelectedRole(role);
    setErrorMsg('');
    if (role !== 'Public') {
      setPublicMode('signin');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');

    if (captchaInput.trim().toLowerCase() !== captchaCode.toLowerCase()) {
      setErrorMsg('Invalid Security Verification (CAPTCHA) code.');
      generateCaptcha();
      setCaptchaInput('');
      return;
    }

    if (selectedRole === 'Public' && publicMode === 'signup') {
      if (!fullName.trim()) {
        setErrorMsg('Please enter your full name.');
        return;
      }
      // Save new public user registration logic
      const savedUsers = JSON.parse(localStorage.getItem('app_users') || '[]');
      const newUser = {
        id: Date.now().toString(),
        name: fullName,
        email: username,
        role: 'Public',
        status: 'Active',
      };
      localStorage.setItem('app_users', JSON.stringify([...savedUsers, newUser]));
      localStorage.setItem('userRole', 'Public');
      localStorage.setItem('username', fullName);
      router.push('/dashboard');
      return;
    }

    try {
      const response = await fetch('http://localhost:8002/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: username,
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok || !data.access_token) {
        setErrorMsg(data.detail || 'Invalid username/email or password.');
        return;
      }

      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('userRole', selectedRole);
      localStorage.setItem(
        'username',
        username.split('@')[0] || username || 'USER'
      );
      router.push('/dashboard');
    } catch {
      setErrorMsg('Unable to connect to the backend.');
    }
  };
  return (
    <div className="min-h-screen bg-[#0f1015] flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md bg-[#181a24] border border-white/10 rounded-2xl p-8 shadow-2xl space-y-6">
        
        {/* Header */}
        <div className="text-center space-y-1">
          <h1 className="text-2xl font-black text-white tracking-wide">TrafficVision AI</h1>
          <p className="text-[11px] font-bold text-gray-400 tracking-wider uppercase">
            SMART TRAFFIC CONTROL & MONITORING SYSTEM
          </p>
        </div>

        {/* Role Selector Tabs */}
        <div className="grid grid-cols-3 gap-1 bg-[#10121a] p-1 rounded-xl border border-white/5">
          {(['Operator', 'Admin', 'Public'] as const).map((role) => (
            <button
              key={role}
              type="button"
              onClick={() => handleRoleChange(role)}
              className={`py-2 text-xs font-bold rounded-lg transition-all ${
                selectedRole === role
                  ? 'bg-[#1d4ed8] text-white shadow-md'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              {role}
            </button>
          ))}
        </div>

        {/* Public-Only Toggle for Sign In / Sign Up */}
        {selectedRole === 'Public' && (
          <div className="flex bg-[#10121a] p-1 rounded-lg border border-white/5 text-xs">
            <button
              type="button"
              onClick={() => setPublicMode('signin')}
              className={`flex-1 py-1.5 rounded-md font-semibold flex items-center justify-center gap-1.5 transition-all ${
                publicMode === 'signin'
                  ? 'bg-white/10 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <LogIn size={13} /> Sign In
            </button>
            <button
              type="button"
              onClick={() => setPublicMode('signup')}
              className={`flex-1 py-1.5 rounded-md font-semibold flex items-center justify-center gap-1.5 transition-all ${
                publicMode === 'signup'
                  ? 'bg-white/10 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <UserPlus size={13} /> Sign Up
            </button>
          </div>
        )}

        {/* Error Message */}
        {errorMsg && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-xs font-medium text-center">
            {errorMsg}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Full Name field appears only during Public Sign Up */}
          {selectedRole === 'Public' && publicMode === 'signup' && (
            <div>
              <label className="block text-xs font-bold text-gray-300 mb-1">Full Name</label>
              <input
                type="text"
                required
                placeholder="Enter your full name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full bg-[#10121a] border border-white/10 text-white px-3.5 py-2.5 rounded-xl text-xs focus:outline-none focus:border-[#1d4ed8]"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-bold text-gray-300 mb-1">
              {selectedRole === 'Public' && publicMode === 'signup' ? 'Email Address' : 'Username or Email'}
            </label>
            <input
              type="text"
              required
              placeholder={
                selectedRole === 'Public' && publicMode === 'signup'
                  ? 'Enter your email'
                  : 'Enter username or email'
              }
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-[#10121a] border border-white/10 text-white px-3.5 py-2.5 rounded-xl text-xs focus:outline-none focus:border-[#1d4ed8]"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-gray-300 mb-1">Password</label>
            <input
              type="password"
              required
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-[#10121a] border border-white/10 text-white px-3.5 py-2.5 rounded-xl text-xs focus:outline-none focus:border-[#1d4ed8]"
            />
          </div>

          {/* CAPTCHA Section */}
          <div className="space-y-2 pt-1">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-gray-300">Security Verification</label>
              <button
                type="button"
                onClick={generateCaptcha}
                className="text-[11px] text-[#00d2ff] hover:underline flex items-center gap-1"
              >
                <RefreshCw size={11} /> Can't read? Change code
              </button>
            </div>

            <div className="bg-[#10121a] border border-white/10 rounded-xl p-3 text-center tracking-[0.3em] font-mono text-lg font-bold text-[#00d2ff] italic select-none shadow-inner">
              {captchaCode}
            </div>

            <input
              type="text"
              required
              placeholder="Enter the CAPTCHA code above"
              value={captchaInput}
              onChange={(e) => setCaptchaInput(e.target.value)}
              className="w-full bg-[#10121a] border border-white/10 text-white px-3.5 py-2.5 rounded-xl text-xs focus:outline-none focus:border-[#1d4ed8]"
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="w-full bg-[#22c55e] hover:bg-[#16a34a] text-white font-bold py-3 rounded-xl text-xs flex items-center justify-center gap-2 transition-all shadow-lg hover:shadow-green-500/20 mt-2"
          >
            {selectedRole === 'Public' && publicMode === 'signup'
              ? 'Create Account'
              : 'Initialize Session'}{' '}
            <ArrowRight size={14} />
          </button>
        </form>
      </div>
    </div>
  );
}
