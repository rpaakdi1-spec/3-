import { renderHook, act } from '@testing-library/react';
import { useAuthStore } from '../../../store/authStore';

describe('useAuthStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    const { result } = renderHook(() => useAuthStore());
    act(() => {
      result.current.logout();
    });
  });

  it('initializes with default state', () => {
    const { result } = renderHook(() => useAuthStore());
    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.loading).toBe(false);
  });

  it('sets user and token on login', () => {
    const { result } = renderHook(() => useAuthStore());
    
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      role: 'ADMIN',
      full_name: 'Test User',
    };
    const mockToken = 'test-token-123';

    act(() => {
      result.current.setUser(mockUser);
      result.current.setToken(mockToken);
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.token).toBe(mockToken);
    expect(result.current.isAuthenticated).toBe(true);
  });

  it('clears user and token on logout', () => {
    const { result } = renderHook(() => useAuthStore());
    
    // First login
    act(() => {
      result.current.setUser({
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        role: 'ADMIN',
        full_name: 'Test User',
      });
      result.current.setToken('test-token');
    });

    expect(result.current.isAuthenticated).toBe(true);

    // Then logout
    act(() => {
      result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });

  it('sets loading state', () => {
    const { result } = renderHook(() => useAuthStore());

    act(() => {
      result.current.setLoading(true);
    });

    expect(result.current.loading).toBe(true);

    act(() => {
      result.current.setLoading(false);
    });

    expect(result.current.loading).toBe(false);
  });

  it('persists token to localStorage', () => {
    const { result } = renderHook(() => useAuthStore());
    const mockToken = 'test-token-persistent';

    act(() => {
      result.current.setToken(mockToken);
    });

    expect(localStorage.getItem('token')).toBe(mockToken);
  });

  it('removes token from localStorage on logout', () => {
    const { result } = renderHook(() => useAuthStore());

    act(() => {
      result.current.setToken('test-token');
      result.current.logout();
    });

    expect(localStorage.getItem('token')).toBeNull();
  });
});
