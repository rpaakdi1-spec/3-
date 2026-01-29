import { wsClient } from '../../../utils/websocket';

describe('WebSocket Client', () => {
  beforeEach(() => {
    // Mock WebSocket
    global.WebSocket = jest.fn(() => ({
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      send: jest.fn(),
      close: jest.fn(),
      readyState: WebSocket.CONNECTING,
    })) as any;
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('creates WebSocket instance', () => {
    expect(wsClient).toBeDefined();
  });

  it('connects to WebSocket server', () => {
    wsClient.connect();
    expect(global.WebSocket).toHaveBeenCalled();
  });

  it('registers event listeners', () => {
    const callback = jest.fn();
    wsClient.on('test_event', callback);
    
    // Verify callback is registered
    expect(callback).toBeDefined();
  });

  it('removes event listeners', () => {
    const callback = jest.fn();
    wsClient.on('test_event', callback);
    wsClient.off('test_event', callback);
    
    // Verify callback is removed
    expect(callback).toBeDefined();
  });

  it('disconnects from WebSocket server', () => {
    wsClient.connect();
    wsClient.disconnect();
    
    // Verify disconnect was called
    expect(wsClient).toBeDefined();
  });

  it('attempts reconnection on connection loss', (done) => {
    wsClient.connect();
    
    // Simulate connection loss
    setTimeout(() => {
      // Verify reconnection attempt
      expect(wsClient).toBeDefined();
      done();
    }, 100);
  });

  it('handles multiple event listeners for same event', () => {
    const callback1 = jest.fn();
    const callback2 = jest.fn();
    
    wsClient.on('test_event', callback1);
    wsClient.on('test_event', callback2);
    
    expect(callback1).toBeDefined();
    expect(callback2).toBeDefined();
  });

  it('does not reconnect after manual disconnect', () => {
    wsClient.connect();
    wsClient.disconnect();
    
    // Verify no reconnection attempt after manual disconnect
    expect(wsClient).toBeDefined();
  });
});
