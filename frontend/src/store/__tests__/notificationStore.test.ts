import { renderHook, act } from '@testing-library/react';
import { useNotificationStore } from '../../../store/notificationStore';

describe('useNotificationStore', () => {
  beforeEach(() => {
    // Clear notifications before each test
    const { result } = renderHook(() => useNotificationStore());
    act(() => {
      result.current.notifications.forEach(n => {
        result.current.removeNotification(n.id);
      });
    });
  });

  it('initializes with empty notifications', () => {
    const { result } = renderHook(() => useNotificationStore());
    expect(result.current.notifications).toEqual([]);
  });

  it('adds a notification', () => {
    const { result } = renderHook(() => useNotificationStore());

    act(() => {
      result.current.addNotification({
        type: 'success',
        title: 'Success',
        message: 'Operation completed successfully',
      });
    });

    expect(result.current.notifications).toHaveLength(1);
    expect(result.current.notifications[0]).toMatchObject({
      type: 'success',
      title: 'Success',
      message: 'Operation completed successfully',
      read: false,
    });
  });

  it('generates unique IDs for notifications', () => {
    const { result } = renderHook(() => useNotificationStore());

    act(() => {
      result.current.addNotification({
        type: 'info',
        title: 'Info 1',
        message: 'Message 1',
      });
      result.current.addNotification({
        type: 'info',
        title: 'Info 2',
        message: 'Message 2',
      });
    });

    expect(result.current.notifications).toHaveLength(2);
    expect(result.current.notifications[0].id).not.toBe(
      result.current.notifications[1].id
    );
  });

  it('removes a notification', () => {
    const { result } = renderHook(() => useNotificationStore());

    let notificationId: string;

    act(() => {
      result.current.addNotification({
        type: 'warning',
        title: 'Warning',
        message: 'This is a warning',
      });
      notificationId = result.current.notifications[0].id;
    });

    expect(result.current.notifications).toHaveLength(1);

    act(() => {
      result.current.removeNotification(notificationId);
    });

    expect(result.current.notifications).toHaveLength(0);
  });

  it('marks notification as read', () => {
    const { result } = renderHook(() => useNotificationStore());

    let notificationId: string;

    act(() => {
      result.current.addNotification({
        type: 'error',
        title: 'Error',
        message: 'An error occurred',
      });
      notificationId = result.current.notifications[0].id;
    });

    expect(result.current.notifications[0].read).toBe(false);

    act(() => {
      result.current.markAsRead(notificationId);
    });

    expect(result.current.notifications[0].read).toBe(true);
  });

  it('marks all notifications as read', () => {
    const { result } = renderHook(() => useNotificationStore());

    act(() => {
      result.current.addNotification({
        type: 'info',
        title: 'Info 1',
        message: 'Message 1',
      });
      result.current.addNotification({
        type: 'info',
        title: 'Info 2',
        message: 'Message 2',
      });
      result.current.addNotification({
        type: 'info',
        title: 'Info 3',
        message: 'Message 3',
      });
    });

    expect(result.current.notifications.every(n => !n.read)).toBe(true);

    act(() => {
      result.current.markAllAsRead();
    });

    expect(result.current.notifications.every(n => n.read)).toBe(true);
  });

  it('clears all notifications', () => {
    const { result } = renderHook(() => useNotificationStore());

    act(() => {
      result.current.addNotification({
        type: 'success',
        title: 'Success 1',
        message: 'Message 1',
      });
      result.current.addNotification({
        type: 'success',
        title: 'Success 2',
        message: 'Message 2',
      });
    });

    expect(result.current.notifications).toHaveLength(2);

    act(() => {
      result.current.clearAll();
    });

    expect(result.current.notifications).toHaveLength(0);
  });

  it('adds notification with different types', () => {
    const { result } = renderHook(() => useNotificationStore());

    act(() => {
      result.current.addNotification({
        type: 'success',
        title: 'Success',
        message: 'Success message',
      });
      result.current.addNotification({
        type: 'error',
        title: 'Error',
        message: 'Error message',
      });
      result.current.addNotification({
        type: 'warning',
        title: 'Warning',
        message: 'Warning message',
      });
      result.current.addNotification({
        type: 'info',
        title: 'Info',
        message: 'Info message',
      });
    });

    expect(result.current.notifications).toHaveLength(4);
    expect(result.current.notifications[0].type).toBe('success');
    expect(result.current.notifications[1].type).toBe('error');
    expect(result.current.notifications[2].type).toBe('warning');
    expect(result.current.notifications[3].type).toBe('info');
  });
});
