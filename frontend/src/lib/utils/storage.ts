import {
  Conversation,
  Message,
  UserPreferences,
  UserSession,
  RealtimeUpdate,
  SyncStatus,
  FailedOperation
} from '@/lib/chat-types';

/**
 * Local storage utilities for ChatKit frontend
 * Handles client-side persistence with proper error handling and type safety
 */

// Storage keys with type safety
export const STORAGE_KEYS = {
  CONVERSATION_LIST: 'chatkit_conversations',
  CONVERSATION_PREFIX: 'chatkit_conversation_',
  USER_PREFERENCES: 'chatkit_preferences',
  USER_SESSION: 'chatkit_user_session',
  ACTIVE_CONVERSATION: 'chatkit_active_conversation',
  SYNC_STATUS: 'chatkit_sync_status',
  LAST_UPDATE: 'chatkit_last_update',
} as const;

// Storage manager class with comprehensive CRUD operations
export class StorageManager {
  private static instance: StorageManager;
  private storage: Storage;

  private constructor() {
    this.storage = typeof window !== 'undefined' ? localStorage : ({} as Storage);
  }

  public static getInstance(): StorageManager {
    if (!StorageManager.instance) {
      StorageManager.instance = new StorageManager();
    }
    return StorageManager.instance;
  }

  // Generic storage methods with error handling
  private safeGetItem(key: string): string | null {
    try {
      return this.storage.getItem(key);
    } catch (error) {
      console.warn(`Failed to get item "${key}" from storage:`, error);
      return null;
    }
  }

  private safeSetItem(key: string, value: string): void {
    try {
      this.storage.setItem(key, value);
    } catch (error) {
      console.warn(`Failed to set item "${key}" in storage:`, error);
      // Check if storage is full
      if (error instanceof DOMException && error.name === 'QuotaExceededError') {
        this.handleStorageQuotaExceeded();
      }
    }
  }

  private safeRemoveItem(key: string): void {
    try {
      this.storage.removeItem(key);
    } catch (error) {
      console.warn(`Failed to remove item "${key}" from storage:`, error);
    }
  }

  private handleStorageQuotaExceeded(): void {
    console.warn('Storage quota exceeded, clearing old data...');
    this.clearOldConversations();
    this.clearFailedOperations();
  }

  // Conversation management
  public saveConversation(conversation: Conversation): void {
    const key = `${STORAGE_KEYS.CONVERSATION_PREFIX}${conversation.id}`;
    this.safeSetItem(key, JSON.stringify(conversation));

    // Also update the conversation list
    this.updateConversationList(conversation);
  }

  public getConversation(id: string): Conversation | null {
    const key = `${STORAGE_KEYS.CONVERSATION_PREFIX}${id}`;
    const data = this.safeGetItem(key);
    return data ? JSON.parse(data) : null;
  }

  public deleteConversation(id: string): void {
    const key = `${STORAGE_KEYS.CONVERSATION_PREFIX}${id}`;
    this.safeRemoveItem(key);

    // Remove from conversation list
    this.removeFromConversationList(id);

    // Delete associated messages
    this.deleteMessages(id);
  }

  public getConversationList(): Conversation[] {
    const data = this.safeGetItem(STORAGE_KEYS.CONVERSATION_LIST);
    return data ? JSON.parse(data) : [];
  }

  private updateConversationList(conversation: Conversation): void {
    const conversations = this.getConversationList();
    const existingIndex = conversations.findIndex(c => c.id === conversation.id);

    if (existingIndex >= 0) {
      conversations[existingIndex] = conversation;
    } else {
      conversations.push(conversation);
    }

    // Sort by lastMessageAt (most recent first)
    conversations.sort((a, b) =>
      new Date(b.lastMessageAt).getTime() - new Date(a.lastMessageAt).getTime()
    );

    this.safeSetItem(STORAGE_KEYS.CONVERSATION_LIST, JSON.stringify(conversations));
  }

  private removeFromConversationList(id: string): void {
    const conversations = this.getConversationList();
    const filteredConversations = conversations.filter(c => c.id !== id);
    this.safeSetItem(STORAGE_KEYS.CONVERSATION_LIST, JSON.stringify(filteredConversations));
  }

  // Message management
  public saveMessages(conversationId: string, messages: Message[]): void {
    const key = `${STORAGE_KEYS.CONVERSATION_PREFIX}${conversationId}_messages`;
    this.safeSetItem(key, JSON.stringify(messages));
  }

  public getMessages(conversationId: string): Message[] {
    const key = `${STORAGE_KEYS.CONVERSATION_PREFIX}${conversationId}_messages`;
    const data = this.safeGetItem(key);
    return data ? JSON.parse(data) : [];
  }

  public addMessage(conversationId: string, message: Message): void {
    const messages = this.getMessages(conversationId);
    messages.push(message);

    // Sort messages by timestamp
    messages.sort((a, b) =>
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );

    this.saveMessages(conversationId, messages);
  }

  public updateMessage(conversationId: string, messageId: string, updates: Partial<Message>): void {
    const messages = this.getMessages(conversationId);
    const messageIndex = messages.findIndex(m => m.id === messageId);

    if (messageIndex >= 0) {
      messages[messageIndex] = { ...messages[messageIndex], ...updates };
      this.saveMessages(conversationId, messages);
    }
  }

  public deleteMessage(conversationId: string, messageId: string): void {
    const messages = this.getMessages(conversationId);
    const filteredMessages = messages.filter(m => m.id !== messageId);
    this.saveMessages(conversationId, filteredMessages);
  }

  public deleteMessages(conversationId: string): void {
    const key = `${STORAGE_KEYS.CONVERSATION_PREFIX}${conversationId}_messages`;
    this.safeRemoveItem(key);
  }

  // User preferences
  public savePreferences(preferences: UserPreferences): void {
    this.safeSetItem(STORAGE_KEYS.USER_PREFERENCES, JSON.stringify(preferences));
  }

  public getPreferences(): UserPreferences | null {
    const data = this.safeGetItem(STORAGE_KEYS.USER_PREFERENCES);
    return data ? JSON.parse(data) : null;
  }

  // User session
  public saveUserSession(session: UserSession): void {
    this.safeSetItem(STORAGE_KEYS.USER_SESSION, JSON.stringify(session));
  }

  public getUserSession(): UserSession | null {
    const data = this.safeGetItem(STORAGE_KEYS.USER_SESSION);
    return data ? JSON.parse(data) : null;
  }

  public clearUserSession(): void {
    this.safeRemoveItem(STORAGE_KEYS.USER_SESSION);
  }

  // Active conversation
  public setActiveConversation(conversationId: string | null): void {
    if (conversationId) {
      this.safeSetItem(STORAGE_KEYS.ACTIVE_CONVERSATION, conversationId);
    } else {
      this.safeRemoveItem(STORAGE_KEYS.ACTIVE_CONVERSATION);
    }
  }

  public getActiveConversation(): string | null {
    return this.safeGetItem(STORAGE_KEYS.ACTIVE_CONVERSATION);
  }

  // Sync status
  public saveSyncStatus(syncStatus: SyncStatus): void {
    this.safeSetItem(STORAGE_KEYS.SYNC_STATUS, JSON.stringify(syncStatus));
  }

  public getSyncStatus(): SyncStatus | null {
    const data = this.safeGetItem(STORAGE_KEYS.SYNC_STATUS);
    return data ? JSON.parse(data) : null;
  }

  // Real-time updates
  public saveLastUpdate(update: RealtimeUpdate): void {
    this.safeSetItem(STORAGE_KEYS.LAST_UPDATE, JSON.stringify(update));
  }

  public getLastUpdate(): RealtimeUpdate | null {
    const data = this.safeGetItem(STORAGE_KEYS.LAST_UPDATE);
    return data ? JSON.parse(data) : null;
  }

  // Failed operations management
  public addFailedOperation(operation: FailedOperation): void {
    const syncStatus = this.getSyncStatus() || {
      lastSyncAt: new Date().toISOString(),
      pendingMessages: [],
      failedOperations: [],
      isOnline: navigator.onLine
    };

    syncStatus.failedOperations.push(operation);
    this.saveSyncStatus(syncStatus);
  }

  public removeFailedOperation(operationId: string): void {
    const syncStatus = this.getSyncStatus();
    if (syncStatus) {
      syncStatus.failedOperations = syncStatus.failedOperations.filter(
        op => op.id !== operationId
      );
      this.saveSyncStatus(syncStatus);
    }
  }

  public getFailedOperations(): FailedOperation[] {
    const syncStatus = this.getSyncStatus();
    return syncStatus ? syncStatus.failedOperations : [];
  }

  // Utility methods
  public clearOldConversations(daysOld: number = 30): void {
    const conversations = this.getConversationList();
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysOld);

    const oldConversations = conversations.filter(c =>
      new Date(c.updatedAt) < cutoffDate
    );

    oldConversations.forEach(conversation => {
      this.deleteConversation(conversation.id);
    });
  }

  public clearFailedOperations(): void {
    const syncStatus = this.getSyncStatus();
    if (syncStatus) {
      syncStatus.failedOperations = [];
      this.saveSyncStatus(syncStatus);
    }
  }

  public getStorageUsage(): { used: number; available: number; percentage: number } {
    try {
      let used = 0;
      for (let key in this.storage) {
        if (this.storage.hasOwnProperty(key)) {
          used += this.storage[key].length;
        }
      }

      // Rough estimate of localStorage limit (usually 5-10MB)
      const estimated = 5 * 1024 * 1024; // 5MB
      const percentage = (used / estimated) * 100;

      return {
        used,
        available: estimated - used,
        percentage
      };
    } catch (error) {
      return { used: 0, available: 0, percentage: 0 };
    }
  }

  public clearAllChatData(): void {
    const keysToRemove: string[] = [];

    for (let i = 0; i < this.storage.length; i++) {
      const key = this.storage.key(i);
      if (key && key.startsWith('chatkit_')) {
        keysToRemove.push(key);
      }
    }

    keysToRemove.forEach(key => {
      this.safeRemoveItem(key);
    });
  }
}

// Export singleton instance
export const storageManager = StorageManager.getInstance();

// Export convenience functions
export const {
  saveConversation,
  getConversation,
  deleteConversation,
  getConversationList,
  saveMessages,
  getMessages,
  addMessage,
  updateMessage,
  deleteMessage,
  savePreferences,
  getPreferences,
  saveUserSession,
  getUserSession,
  clearUserSession,
  setActiveConversation,
  getActiveConversation,
  saveSyncStatus,
  getSyncStatus,
  saveLastUpdate,
  getLastUpdate,
  addFailedOperation,
  removeFailedOperation,
  getFailedOperations,
  clearOldConversations,
  clearFailedOperations,
  getStorageUsage,
  clearAllChatData,
} = storageManager;

export default storageManager;