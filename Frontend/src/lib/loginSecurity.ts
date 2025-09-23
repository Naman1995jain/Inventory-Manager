interface LoginAttempt {
  email: string;
  attempts: number;
  lockedUntil?: number;
}

class LoginSecurityManager {
  private static readonly MAX_ATTEMPTS = 3;
  private static readonly LOCKOUT_DURATION = 60 * 1000; // 60 seconds in milliseconds
  private static readonly STORAGE_KEY = 'login_attempts';

  static getAttempts(): LoginAttempt[] {
    if (typeof window === 'undefined') return [];
    
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }

  static saveAttempts(attempts: LoginAttempt[]): void {
    if (typeof window === 'undefined') return;
    
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(attempts));
    } catch {
      // Ignore storage errors
    }
  }

  static isLocked(email: string): { locked: boolean; remainingTime?: number } {
    const attempts = this.getAttempts();
    const userAttempt = attempts.find(a => a.email === email);
    
    if (!userAttempt || !userAttempt.lockedUntil) {
      return { locked: false };
    }

    const now = Date.now();
    if (now >= userAttempt.lockedUntil) {
      // Lock has expired, reset attempts
      this.resetAttempts(email);
      return { locked: false };
    }

    const remainingTime = Math.ceil((userAttempt.lockedUntil - now) / 1000);
    return { locked: true, remainingTime };
  }

  static recordFailedAttempt(email: string): { locked: boolean; remainingTime?: number; attempts: number } {
    const attempts = this.getAttempts();
    const existingIndex = attempts.findIndex(a => a.email === email);
    
    if (existingIndex >= 0) {
      attempts[existingIndex].attempts += 1;
      
      if (attempts[existingIndex].attempts >= this.MAX_ATTEMPTS) {
        attempts[existingIndex].lockedUntil = Date.now() + this.LOCKOUT_DURATION;
        this.saveAttempts(attempts);
        return { 
          locked: true, 
          remainingTime: Math.ceil(this.LOCKOUT_DURATION / 1000),
          attempts: attempts[existingIndex].attempts
        };
      }
    } else {
      attempts.push({
        email,
        attempts: 1
      });
    }
    
    this.saveAttempts(attempts);
    const userAttempt = attempts.find(a => a.email === email);
    return { 
      locked: false, 
      attempts: userAttempt?.attempts || 1
    };
  }

  static resetAttempts(email: string): void {
    const attempts = this.getAttempts();
    const filteredAttempts = attempts.filter(a => a.email !== email);
    this.saveAttempts(filteredAttempts);
  }

  static cleanupExpiredLocks(): void {
    const attempts = this.getAttempts();
    const now = Date.now();
    const validAttempts = attempts.filter(a => 
      !a.lockedUntil || a.lockedUntil > now
    );
    this.saveAttempts(validAttempts);
  }
}

export default LoginSecurityManager;