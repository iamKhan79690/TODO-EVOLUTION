'use client';

/**
 * ChatKit Widget Component - Hybrid Integration
 * 
 * Uses OpenAI ChatKit UI components but routes messages through
 * the custom backend API (/api/{user_id}/chat) instead of OpenAI's hosted backend.
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useAuth } from '@/lib/auth-provider';

interface Message {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
    status?: 'sending' | 'sent' | 'error';
    toolCalls?: Array<{
        tool: string;
        params: Record<string, unknown>;
        result?: Record<string, unknown>;
    }>;
}

interface ChatKitWidgetProps {
    onClose?: () => void;
    isOpen?: boolean;
}

export function ChatKitWidget({ onClose, isOpen = true }: ChatKitWidgetProps) {
    const { user, accessToken } = useAuth();
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [conversationId, setConversationId] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const hasLoadedConversation = useRef(false);

    // Load/Save conversation ID
    useEffect(() => {
        if (!hasLoadedConversation.current) {
            const savedId = localStorage.getItem('chat_conversation_id');
            if (savedId) setConversationId(savedId);
            hasLoadedConversation.current = true;
        }
    }, []);

    useEffect(() => {
        if (conversationId) localStorage.setItem('chat_conversation_id', conversationId);
    }, [conversationId]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const getAuthToken = useCallback(async (): Promise<string | null> => {
        if (accessToken) return accessToken;
        try {
            const response = await fetch('/api/auth/session');
            if (response.ok) {
                const data = await response.json();
                return data.accessToken || null;
            }
        } catch { }
        return null;
    }, [accessToken]);

    const sendMessage = useCallback(async (content: string) => {
        if (!content.trim() || isLoading) return;

        const token = await getAuthToken();
        const userId = user?.id;
        if (!token || !userId) {
            setError('Please sign in to use the chat');
            return;
        }

        const userMessage: Message = {
            id: `user-${Date.now()}`,
            role: 'user',
            content: content.trim(),
            timestamp: new Date(),
            status: 'sending',
        };
        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);
        setError(null);

        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

        try {
            const response = await fetch(`${API_BASE_URL}/api/${userId}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    message: content.trim(),
                    conversation_id: conversationId,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }

            const data = await response.json();
            if (data.conversation_id && !conversationId) setConversationId(String(data.conversation_id));

            setMessages(prev => prev.map(msg => msg.id === userMessage.id ? { ...msg, status: 'sent' } : msg));

            const assistantMessage: Message = {
                id: `assistant-${Date.now()}`,
                role: 'assistant',
                content: data.response,
                timestamp: new Date(),
                status: 'sent',
                toolCalls: data.tool_calls,
            };
            setMessages(prev => [...prev, assistantMessage]);

            if (data.tool_calls?.length > 0) {
                window.dispatchEvent(new CustomEvent('tasks-updated'));
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to send message');
            setMessages(prev => prev.map(msg => msg.id === userMessage.id ? { ...msg, status: 'error' } : msg));
        } finally {
            setIsLoading(false);
        }
    }, [conversationId, getAuthToken, isLoading, user?.id]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        sendMessage(inputValue);
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage(inputValue);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="chatkit-widget fixed bottom-4 right-4 z-50 flex flex-col w-[380px] h-[600px] bg-white dark:bg-gray-900 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden text-gray-900 dark:text-white">
            {/* Header */}
            <div className="chatkit-header flex items-center justify-between px-4 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white flex-shrink-0">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                        </svg>
                    </div>
                    <div>
                        <h3 className="font-semibold text-sm">TODO Assistant</h3>
                        <p className="text-xs opacity-80">Online</p>
                    </div>
                </div>
                {onClose && (
                    <button
                        onClick={onClose}
                        className="p-1.5 hover:bg-white/20 rounded-full transition-colors flex items-center gap-1 text-xs"
                        aria-label="Close chat"
                    >
                        <span className="hidden sm:inline">Close</span>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                )}
            </div>

            {/* Messages Area */}
            <div className="chatkit-messages flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-800">
                {messages.length === 0 && (
                    <div className="text-center text-gray-500 dark:text-gray-400 mt-12 px-6">
                        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                            <svg className="w-8 h-8 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                            </svg>
                        </div>
                        <p className="font-medium">Welcome to TODO Assistant!</p>
                        <p className="text-sm mt-1">Try: "Add a task to buy groceries" or "What are my high priority tasks?"</p>
                    </div>
                )}

                {messages.map((msg) => (
                    <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 shadow-sm ${msg.role === 'user'
                                ? 'bg-blue-600 text-white rounded-br-md'
                                : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-bl-md'
                            }`}>
                            <p className="text-sm whitespace-pre-wrap">{msg.content}</p>

                            {msg.toolCalls && msg.toolCalls.length > 0 && (
                                <div className="mt-2 pt-2 border-t border-gray-100 dark:border-gray-600 flex flex-wrap gap-1">
                                    {msg.toolCalls.map((tc, idx) => (
                                        <span key={idx} className="inline-flex items-center gap-1 text-[10px] bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 px-2 py-0.5 rounded-full">
                                            <svg className="w-2.5 h-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                            </svg>
                                            {tc.tool}
                                        </span>
                                    ))}
                                </div>
                            )}

                            {msg.status === 'sending' && <span className="text-[10px] opacity-60 mt-1 block">Sending...</span>}
                            {msg.status === 'error' && <span className="text-[10px] text-red-300 mt-1 block">Failed to send</span>}
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-white dark:bg-gray-700 rounded-2xl px-4 py-3 shadow-sm rounded-bl-md">
                            <div className="flex gap-1">
                                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                            </div>
                        </div>
                    </div>
                )}

                {error && (
                    <div className="text-center text-red-500 text-xs bg-red-50 dark:bg-red-900/20 rounded-lg px-4 py-2 my-2">
                        {error}
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="chatkit-input-container p-3 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 flex-shrink-0">
                <form onSubmit={handleSubmit} className="flex gap-2">
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={handleKeyPress}
                        placeholder="Ask about your tasks..."
                        disabled={isLoading}
                        className="flex-1 px-4 py-2.5 text-sm bg-gray-100 dark:bg-gray-800 border border-transparent focus:bg-white dark:focus:bg-gray-850 focus:border-blue-500 rounded-full focus:outline-none transition-all disabled:opacity-50 text-gray-900 dark:text-white"
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !inputValue.trim()}
                        className="w-10 h-10 flex items-center justify-center bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-md active:scale-95"
                        aria-label="Send message"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                        </svg>
                    </button>
                </form>

                {/* Visual Close Option at bottom */}
                <div className="mt-2 flex justify-center">
                    <button
                        onClick={onClose}
                        className="text-[10px] text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 transition-colors uppercase tracking-wider font-semibold"
                    >
                        Close Assistant Window
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ChatKitWidget;
