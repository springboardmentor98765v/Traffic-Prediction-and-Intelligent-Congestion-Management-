'use client';

import React, { useEffect, useState } from 'react';
import {
  Bell,
  AlertTriangle,
  XCircle,
  Clock,
} from 'lucide-react';

interface Notification {
  id: number;
  type: 'Congestion' | 'Accident' | 'Road Closure' | 'Delay';
  message: string;
  time: string;
  unread: boolean;
}

const mockNotifications: Notification[] = [
  {
    id: 1,
    type: 'Congestion',
    message: 'Heavy traffic reported on JM Road.',
    time: '2 min ago',
    unread: true,
  },
  {
    id: 2,
    type: 'Delay',
    message: 'Travel delay detected on FC Road.',
    time: '10 min ago',
    unread: true,
  },
  {
    id: 3,
    type: 'Road Closure',
    message: 'Road work reported near Baner Main Road.',
    time: '25 min ago',
    unread: false,
  },
];

export const NotificationBell: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  const [notifications, setNotifications] =
    useState<Notification[]>(mockNotifications);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState(false);

  // Simulate loading state
  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  const unreadCount = notifications.filter(
    (notification) => notification.unread
  ).length;

  // Mark notification as read
  const markAsRead = (id: number) => {
    setNotifications((currentNotifications) =>
      currentNotifications.map((notification) =>
        notification.id === id
          ? { ...notification, unread: false }
          : notification
      )
    );
  };

  const getIcon = (type: Notification['type']) => {
    if (type === 'Congestion') {
      return (
        <AlertTriangle
          size={16}
          className="text-amber-400"
        />
      );
    }

    if (type === 'Accident') {
      return (
        <AlertTriangle
          size={16}
          className="text-red-400"
        />
      );
    }

    if (type === 'Road Closure') {
      return (
        <XCircle
          size={16}
          className="text-red-400"
        />
      );
    }

    return (
      <Clock
        size={16}
        className="text-cyan-400"
      />
    );
  };

  return (
    <div className="relative">

      {/* Bell Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2.5 rounded-xl bg-[#161b22] border border-[#30363d] hover:border-[#58a6ff] transition-all"
        aria-label="Notifications"
      >
        <Bell
          size={19}
          className="text-gray-300"
        />

        {/* Unread Badge */}
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 min-w-[18px] h-[18px] px-1 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center">
            {unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute right-0 mt-3 w-80 bg-[#161b22] border border-[#30363d] rounded-xl shadow-2xl z-50 overflow-hidden">

          {/* Loading State */}
          {loading ? (
            <div className="px-4 py-8 text-center">

              <div className="animate-spin mx-auto w-5 h-5 border-2 border-[#30363d] border-t-[#58a6ff] rounded-full"></div>

              <p className="text-xs text-gray-400 mt-3">
                Loading notifications...
              </p>

            </div>
          ) : error ? (

            /* Error State */
            <div className="px-4 py-8 text-center">

              <AlertTriangle
                size={20}
                className="mx-auto text-amber-400"
              />

              <p className="text-xs text-gray-400 mt-3">
                Unable to load notifications.
              </p>

            </div>
          ) : (

            <>
              {/* Header */}
              <div className="flex items-center justify-between px-4 py-3 border-b border-[#30363d]">

                <div>
                  <h3 className="text-sm font-bold text-white">
                    Notifications
                  </h3>

                  <p className="text-[10px] text-gray-500 mt-1">
                    Recent traffic alerts
                  </p>
                </div>

                <span className="text-[10px] text-[#58a6ff] font-semibold">
                  {unreadCount} unread
                </span>

              </div>

              {/* Notifications */}
              <div className="max-h-80 overflow-y-auto">

                {notifications.length === 0 ? (

                  /* Empty State */
                  <div className="px-4 py-8 text-center">

                    <Bell
                      size={20}
                      className="mx-auto text-gray-600"
                    />

                    <p className="text-xs text-gray-400 mt-3">
                      No notifications available.
                    </p>

                  </div>

                ) : (

                  notifications.map((notification) => (
                    <div
                      key={notification.id}
                      onClick={() =>
                        markAsRead(notification.id)
                      }
                      className={`px-4 py-3 border-b border-[#30363d] hover:bg-[#0d1117] transition cursor-pointer ${
                        notification.unread
                          ? 'bg-[#1f6feb]/5'
                          : ''
                      }`}
                    >

                      <div className="flex gap-3">

                        <div className="mt-0.5">
                          {getIcon(notification.type)}
                        </div>

                        <div className="flex-1">

                          <div className="flex items-center justify-between gap-2">

                            <p className="text-xs font-semibold text-gray-200">
                              {notification.type}
                            </p>

                            {/* Unread Dot */}
                            {notification.unread && (
                              <span className="w-2 h-2 rounded-full bg-blue-400"></span>
                            )}

                          </div>

                          <p className="text-xs text-gray-400 mt-1 leading-relaxed">
                            {notification.message}
                          </p>

                          <p className="text-[10px] text-gray-600 mt-2">
                            {notification.time}
                          </p>

                        </div>

                      </div>

                    </div>
                  ))

                )}

              </div>

              {/* Footer */}
              <div className="px-4 py-3">

                <button
                  onClick={() => setIsOpen(false)}
                  className="w-full text-xs text-[#58a6ff] hover:text-white transition"
                >
                  Close Notifications
                </button>

              </div>
            </>
          )}

        </div>
      )}

    </div>
  );
};

export default NotificationBell;
