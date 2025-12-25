'use client';

/**
 * Floating Chat Button Component
 * 
 * A floating action button that opens the ChatKit widget.
 * Provides a persistent chat entry point across the application.
 */

import React, { useState } from 'react';
import dynamic from 'next/dynamic';

// Dynamic import to avoid SSR issues with ChatKit
const ChatKitWidget = dynamic(
    () => import('./ChatKitWidget'),
    { ssr: false }
);

export function FloatingChatButton() {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <>
            {/* Chat Widget */}
            {isOpen && <ChatKitWidget onClose={() => setIsOpen(false)} isOpen={isOpen} />}

            {/* Floating Button */}
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200 flex items-center justify-center group"
                    aria-label="Open chat"
                >
                    <svg
                        className="w-6 h-6 group-hover:scale-110 transition-transform"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                        />
                    </svg>

                    {/* Pulse animation */}
                    <span className="absolute inset-0 rounded-full bg-blue-600 animate-ping opacity-25"></span>
                </button>
            )}
        </>
    );
}

export default FloatingChatButton;
