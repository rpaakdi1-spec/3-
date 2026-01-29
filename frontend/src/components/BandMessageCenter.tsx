import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface BandMessage {
  id: number;
  dispatch_id: number;
  message_content: string;
  message_type: string;
  is_sent: boolean;
  sent_at: string | null;
  generated_at: string;
  scheduled_for: string | null;
  variation_seed: number | null;
}

interface BandChatRoom {
  id: number;
  name: string;
  band_url: string;
  description: string | null;
  is_active: boolean;
  last_message_at: string | null;
  total_messages: number;
  created_at: string;
}

interface BandMessageSchedule {
  id: number;
  dispatch_id: number;
  is_active: boolean;
  start_time: string;
  end_time: string;
  min_interval_seconds: number;
  max_interval_seconds: number;
  messages_generated: number;
  last_generated_at: string | null;
}

const BandMessageCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'messages' | 'chatrooms' | 'schedules'>('messages');
  
  // 메시지 상태
  const [messages, setMessages] = useState<BandMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState<string>('');
  const [dispatchId, setDispatchId] = useState<number>(1);
  const [copied, setCopied] = useState(false);
  const [nextSchedule, setNextSchedule] = useState<string | null>(null);
  
  // 채팅방 상태
  const [chatRooms, setChatRooms] = useState<BandChatRoom[]>([]);
  const [newRoom, setNewRoom] = useState({ name: '', band_url: '', description: '' });
  
  // 스케줄 상태
  const [schedules, setSchedules] = useState<BandMessageSchedule[]>([]);
  const [showScheduleForm, setShowScheduleForm] = useState(false);
  const [scheduleForm, setScheduleForm] = useState({
    dispatch_id: 1,
    start_time: '',
    end_time: '',
    min_interval_seconds: 180,
    max_interval_seconds: 300
  });
  
  // 자동 생성 타이머
  const [autoGenerate, setAutoGenerate] = useState(false);
  const [countdown, setCountdown] = useState<number>(0);

  useEffect(() => {
    fetchMessages();
    fetchChatRooms();
    fetchSchedules();
  }, []);

  // 자동 생성 타이머
  useEffect(() => {
    if (!autoGenerate || countdown <= 0) return;
    
    const timer = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          generateMessage();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    
    return () => clearInterval(timer);
  }, [autoGenerate, countdown]);

  const fetchMessages = async () => {
    try {
      const response = await axios.get('/api/v1/band/messages/');
      setMessages(response.data.items);
    } catch (error) {
      console.error('메시지 조회 실패:', error);
    }
  };

  const fetchChatRooms = async () => {
    try {
      const response = await axios.get('/api/v1/band/chat-rooms/');
      setChatRooms(response.data.items);
    } catch (error) {
      console.error('채팅방 조회 실패:', error);
    }
  };

  const fetchSchedules = async () => {
    try {
      const response = await axios.get('/api/v1/band/schedules/');
      setSchedules(response.data.items);
    } catch (error) {
      console.error('스케줄 조회 실패:', error);
    }
  };

  const generateMessage = async () => {
    try {
      const response = await axios.post('/api/v1/band/generate', {
        dispatch_id: dispatchId
      });
      
      setCurrentMessage(response.data.message);
      setNextSchedule(response.data.next_schedule);
      fetchMessages();
      
      // 다음 생성 시간 설정 (3-5분 랜덤)
      if (autoGenerate) {
        const randomInterval = Math.floor(Math.random() * (300 - 180 + 1)) + 180;
        setCountdown(randomInterval);
      }
    } catch (error) {
      console.error('메시지 생성 실패:', error);
      alert('메시지 생성에 실패했습니다.');
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(currentMessage);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const markAsSent = async (messageId: number) => {
    try {
      await axios.put(`/api/v1/band/messages/${messageId}/mark-sent`);
      fetchMessages();
      alert('전송 완료로 표시되었습니다');
    } catch (error) {
      console.error('상태 업데이트 실패:', error);
    }
  };

  const addChatRoom = async () => {
    if (!newRoom.name || !newRoom.band_url) {
      alert('채팅방 이름과 URL을 입력하세요');
      return;
    }
    
    try {
      await axios.post('/api/v1/band/chat-rooms/', newRoom);
      setNewRoom({ name: '', band_url: '', description: '' });
      fetchChatRooms();
      alert('채팅방이 추가되었습니다');
    } catch (error) {
      console.error('채팅방 추가 실패:', error);
      alert('채팅방 추가에 실패했습니다');
    }
  };

  const createSchedule = async () => {
    if (!scheduleForm.start_time || !scheduleForm.end_time) {
      alert('시작 시간과 종료 시간을 입력하세요');
      return;
    }
    
    try {
      await axios.post('/api/v1/band/schedules/', scheduleForm);
      setShowScheduleForm(false);
      fetchSchedules();
      alert('스케줄이 생성되었습니다');
    } catch (error) {
      console.error('스케줄 생성 실패:', error);
      alert('스케줄 생성에 실패했습니다');
    }
  };

  const toggleSchedule = async (scheduleId: number) => {
    try {
      await axios.post(`/api/v1/band/schedules/${scheduleId}/toggle`);
      fetchSchedules();
    } catch (error) {
      console.error('스케줄 토글 실패:', error);
    }
  };

  const formatCountdown = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '28px', marginBottom: '20px', color: '#333' }}>
        📱 네이버밴드 메시지 센터
      </h1>

      {/* 탭 메뉴 */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', borderBottom: '2px solid #ddd' }}>
        <button
          onClick={() => setActiveTab('messages')}
          style={{
            padding: '10px 20px',
            backgroundColor: activeTab === 'messages' ? '#00C73C' : 'transparent',
            color: activeTab === 'messages' ? 'white' : '#333',
            border: 'none',
            borderBottom: activeTab === 'messages' ? '3px solid #00C73C' : 'none',
            cursor: 'pointer',
            fontWeight: activeTab === 'messages' ? 'bold' : 'normal'
          }}
        >
          메시지 생성
        </button>
        <button
          onClick={() => setActiveTab('chatrooms')}
          style={{
            padding: '10px 20px',
            backgroundColor: activeTab === 'chatrooms' ? '#00C73C' : 'transparent',
            color: activeTab === 'chatrooms' ? 'white' : '#333',
            border: 'none',
            borderBottom: activeTab === 'chatrooms' ? '3px solid #00C73C' : 'none',
            cursor: 'pointer',
            fontWeight: activeTab === 'chatrooms' ? 'bold' : 'normal'
          }}
        >
          채팅방 관리
        </button>
        <button
          onClick={() => setActiveTab('schedules')}
          style={{
            padding: '10px 20px',
            backgroundColor: activeTab === 'schedules' ? '#00C73C' : 'transparent',
            color: activeTab === 'schedules' ? 'white' : '#333',
            border: 'none',
            borderBottom: activeTab === 'schedules' ? '3px solid #00C73C' : 'none',
            cursor: 'pointer',
            fontWeight: activeTab === 'schedules' ? 'bold' : 'normal'
          }}
        >
          자동 스케줄
        </button>
      </div>

      {/* 메시지 생성 탭 */}
      {activeTab === 'messages' && (
        <div>
          <div style={{ backgroundColor: '#f5f5f5', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
            <h2 style={{ fontSize: '20px', marginBottom: '15px' }}>🔄 새 메시지 생성</h2>
            
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                배차 ID:
              </label>
              <input
                type="number"
                value={dispatchId}
                onChange={(e) => setDispatchId(parseInt(e.target.value))}
                style={{
                  padding: '8px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  width: '100px'
                }}
              />
            </div>

            <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
              <button
                onClick={generateMessage}
                style={{
                  padding: '12px 24px',
                  backgroundColor: '#00C73C',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '16px',
                  fontWeight: 'bold'
                }}
              >
                🔄 메시지 생성
              </button>
              
              <button
                onClick={() => {
                  setAutoGenerate(!autoGenerate);
                  if (!autoGenerate) {
                    setCountdown(0);
                    generateMessage();
                  }
                }}
                style={{
                  padding: '12px 24px',
                  backgroundColor: autoGenerate ? '#ff4444' : '#4CAF50',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '16px',
                  fontWeight: 'bold'
                }}
              >
                {autoGenerate ? '⏸️ 자동 중지' : '▶️ 자동 생성 (3-5분)'}
              </button>
            </div>

            {autoGenerate && countdown > 0 && (
              <div style={{ 
                padding: '10px', 
                backgroundColor: '#fffde7', 
                borderRadius: '4px',
                marginBottom: '15px'
              }}>
                ⏰ 다음 메시지 생성까지: <strong>{formatCountdown(countdown)}</strong>
              </div>
            )}

            {currentMessage && (
              <div>
                <pre style={{
                  backgroundColor: 'white',
                  padding: '20px',
                  borderRadius: '4px',
                  border: '1px solid #ddd',
                  whiteSpace: 'pre-wrap',
                  fontSize: '14px',
                  lineHeight: '1.6',
                  marginBottom: '10px'
                }}>
                  {currentMessage}
                </pre>

                <div style={{ display: 'flex', gap: '10px' }}>
                  <button
                    onClick={copyToClipboard}
                    style={{
                      padding: '10px 20px',
                      backgroundColor: copied ? '#4CAF50' : '#2196F3',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontWeight: 'bold'
                    }}
                  >
                    {copied ? '✅ 복사완료!' : '📋 클립보드에 복사'}
                  </button>
                  
                  {chatRooms.filter(r => r.is_active).map(room => (
                    <button
                      key={room.id}
                      onClick={() => window.open(room.band_url, '_blank')}
                      style={{
                        padding: '10px 20px',
                        backgroundColor: '#00C73C',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                      }}
                    >
                      🔗 {room.name}
                    </button>
                  ))}
                </div>

                <div style={{ marginTop: '15px', padding: '10px', backgroundColor: '#e3f2fd', borderRadius: '4px' }}>
                  <strong>💡 사용 방법:</strong>
                  <ol style={{ marginLeft: '20px', marginTop: '10px' }}>
                    <li>위의 "클립보드에 복사" 버튼 클릭</li>
                    <li>원하는 채팅방 버튼 클릭 (새 탭에서 열림)</li>
                    <li>채팅방에서 Ctrl+V로 붙여넣기</li>
                    <li>전송 후 아래 메시지 목록에서 "전송 완료" 버튼 클릭</li>
                  </ol>
                </div>
              </div>
            )}
          </div>

          {/* 메시지 히스토리 */}
          <div>
            <h2 style={{ fontSize: '20px', marginBottom: '15px' }}>📜 메시지 히스토리</h2>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', backgroundColor: 'white' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f5f5f5' }}>
                    <th style={{ padding: '12px', border: '1px solid #ddd', textAlign: 'left' }}>ID</th>
                    <th style={{ padding: '12px', border: '1px solid #ddd', textAlign: 'left' }}>배차ID</th>
                    <th style={{ padding: '12px', border: '1px solid #ddd', textAlign: 'left' }}>메시지 미리보기</th>
                    <th style={{ padding: '12px', border: '1px solid #ddd', textAlign: 'left' }}>생성시간</th>
                    <th style={{ padding: '12px', border: '1px solid #ddd', textAlign: 'left' }}>상태</th>
                    <th style={{ padding: '12px', border: '1px solid #ddd', textAlign: 'left' }}>액션</th>
                  </tr>
                </thead>
                <tbody>
                  {messages.map(message => (
                    <tr key={message.id}>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>{message.id}</td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>{message.dispatch_id}</td>
                      <td style={{ padding: '12px', border: '1px solid #ddd', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {message.message_content.substring(0, 50)}...
                      </td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                        {new Date(message.generated_at).toLocaleString('ko-KR')}
                      </td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                        {message.is_sent ? (
                          <span style={{ color: '#4CAF50', fontWeight: 'bold' }}>✅ 전송완료</span>
                        ) : (
                          <span style={{ color: '#ff9800', fontWeight: 'bold' }}>⏳ 대기중</span>
                        )}
                      </td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                        {!message.is_sent && (
                          <button
                            onClick={() => markAsSent(message.id)}
                            style={{
                              padding: '6px 12px',
                              backgroundColor: '#4CAF50',
                              color: 'white',
                              border: 'none',
                              borderRadius: '4px',
                              cursor: 'pointer',
                              fontSize: '12px'
                            }}
                          >
                            전송 완료
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* 채팅방 관리 탭 */}
      {activeTab === 'chatrooms' && (
        <div>
          <div style={{ backgroundColor: '#f5f5f5', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
            <h2 style={{ fontSize: '20px', marginBottom: '15px' }}>➕ 채팅방 추가</h2>
            
            <div style={{ marginBottom: '10px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>채팅방 이름:</label>
              <input
                type="text"
                value={newRoom.name}
                onChange={(e) => setNewRoom({...newRoom, name: e.target.value})}
                placeholder="예: 화물 수배방 A"
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #ddd',
                  borderRadius: '4px'
                }}
              />
            </div>

            <div style={{ marginBottom: '10px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>밴드 URL:</label>
              <input
                type="text"
                value={newRoom.band_url}
                onChange={(e) => setNewRoom({...newRoom, band_url: e.target.value})}
                placeholder="https://band.us/band/12345"
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #ddd',
                  borderRadius: '4px'
                }}
              />
            </div>

            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>설명 (선택):</label>
              <textarea
                value={newRoom.description}
                onChange={(e) => setNewRoom({...newRoom, description: e.target.value})}
                placeholder="채팅방 설명"
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  resize: 'vertical',
                  minHeight: '60px'
                }}
              />
            </div>

            <button
              onClick={addChatRoom}
              style={{
                padding: '10px 20px',
                backgroundColor: '#00C73C',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: 'bold'
              }}
            >
              채팅방 추가
            </button>
          </div>

          {/* 채팅방 목록 */}
          <div>
            <h2 style={{ fontSize: '20px', marginBottom: '15px' }}>📋 등록된 채팅방</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '15px' }}>
              {chatRooms.map(room => (
                <div
                  key={room.id}
                  style={{
                    padding: '15px',
                    backgroundColor: room.is_active ? 'white' : '#f5f5f5',
                    border: '1px solid #ddd',
                    borderRadius: '8px'
                  }}
                >
                  <h3 style={{ fontSize: '16px', marginBottom: '10px' }}>{room.name}</h3>
                  <p style={{ fontSize: '12px', color: '#666', marginBottom: '10px' }}>
                    {room.description || '설명 없음'}
                  </p>
                  <p style={{ fontSize: '12px', color: '#666', marginBottom: '10px' }}>
                    💬 총 {room.total_messages}개 메시지
                  </p>
                  <button
                    onClick={() => window.open(room.band_url, '_blank')}
                    style={{
                      padding: '8px 16px',
                      backgroundColor: '#00C73C',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      width: '100%'
                    }}
                  >
                    🔗 채팅방 열기
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 자동 스케줄 탭 */}
      {activeTab === 'schedules' && (
        <div>
          {showScheduleForm ? (
            <div style={{ backgroundColor: '#f5f5f5', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
              <h2 style={{ fontSize: '20px', marginBottom: '15px' }}>➕ 스케줄 생성</h2>
              
              <div style={{ marginBottom: '10px' }}>
                <label>배차 ID:</label>
                <input
                  type="number"
                  value={scheduleForm.dispatch_id}
                  onChange={(e) => setScheduleForm({...scheduleForm, dispatch_id: parseInt(e.target.value)})}
                  style={{ width: '100%', padding: '8px', marginTop: '5px' }}
                />
              </div>

              <div style={{ marginBottom: '10px' }}>
                <label>시작 시간:</label>
                <input
                  type="datetime-local"
                  value={scheduleForm.start_time}
                  onChange={(e) => setScheduleForm({...scheduleForm, start_time: e.target.value})}
                  style={{ width: '100%', padding: '8px', marginTop: '5px' }}
                />
              </div>

              <div style={{ marginBottom: '10px' }}>
                <label>종료 시간:</label>
                <input
                  type="datetime-local"
                  value={scheduleForm.end_time}
                  onChange={(e) => setScheduleForm({...scheduleForm, end_time: e.target.value})}
                  style={{ width: '100%', padding: '8px', marginTop: '5px' }}
                />
              </div>

              <div style={{ marginBottom: '10px' }}>
                <label>최소 간격 (초):</label>
                <input
                  type="number"
                  value={scheduleForm.min_interval_seconds}
                  onChange={(e) => setScheduleForm({...scheduleForm, min_interval_seconds: parseInt(e.target.value)})}
                  style={{ width: '100%', padding: '8px', marginTop: '5px' }}
                />
              </div>

              <div style={{ marginBottom: '15px' }}>
                <label>최대 간격 (초):</label>
                <input
                  type="number"
                  value={scheduleForm.max_interval_seconds}
                  onChange={(e) => setScheduleForm({...scheduleForm, max_interval_seconds: parseInt(e.target.value)})}
                  style={{ width: '100%', padding: '8px', marginTop: '5px' }}
                />
              </div>

              <div style={{ display: 'flex', gap: '10px' }}>
                <button onClick={createSchedule} style={{ padding: '10px 20px', backgroundColor: '#00C73C', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                  스케줄 생성
                </button>
                <button onClick={() => setShowScheduleForm(false)} style={{ padding: '10px 20px', backgroundColor: '#ccc', color: '#333', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                  취소
                </button>
              </div>
            </div>
          ) : (
            <button
              onClick={() => setShowScheduleForm(true)}
              style={{
                padding: '12px 24px',
                backgroundColor: '#00C73C',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                marginBottom: '20px',
                fontWeight: 'bold'
              }}
            >
              ➕ 새 스케줄 생성
            </button>
          )}

          <div>
            <h2 style={{ fontSize: '20px', marginBottom: '15px' }}>📅 스케줄 목록</h2>
            <table style={{ width: '100%', borderCollapse: 'collapse', backgroundColor: 'white' }}>
              <thead>
                <tr style={{ backgroundColor: '#f5f5f5' }}>
                  <th style={{ padding: '12px', border: '1px solid #ddd' }}>ID</th>
                  <th style={{ padding: '12px', border: '1px solid #ddd' }}>배차ID</th>
                  <th style={{ padding: '12px', border: '1px solid #ddd' }}>시작</th>
                  <th style={{ padding: '12px', border: '1px solid #ddd' }}>종료</th>
                  <th style={{ padding: '12px', border: '1px solid #ddd' }}>간격</th>
                  <th style={{ padding: '12px', border: '1px solid #ddd' }}>생성수</th>
                  <th style={{ padding: '12px', border: '1px solid #ddd' }}>상태</th>
                  <th style={{ padding: '12px', border: '1px solid #ddd' }}>액션</th>
                </tr>
              </thead>
              <tbody>
                {schedules.map(schedule => (
                  <tr key={schedule.id}>
                    <td style={{ padding: '12px', border: '1px solid #ddd' }}>{schedule.id}</td>
                    <td style={{ padding: '12px', border: '1px solid #ddd' }}>{schedule.dispatch_id}</td>
                    <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                      {new Date(schedule.start_time).toLocaleString('ko-KR')}
                    </td>
                    <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                      {new Date(schedule.end_time).toLocaleString('ko-KR')}
                    </td>
                    <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                      {Math.floor(schedule.min_interval_seconds / 60)}-{Math.floor(schedule.max_interval_seconds / 60)}분
                    </td>
                    <td style={{ padding: '12px', border: '1px solid #ddd' }}>{schedule.messages_generated}개</td>
                    <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                      {schedule.is_active ? (
                        <span style={{ color: '#4CAF50', fontWeight: 'bold' }}>✅ 활성</span>
                      ) : (
                        <span style={{ color: '#999', fontWeight: 'bold' }}>⏸️ 비활성</span>
                      )}
                    </td>
                    <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                      <button
                        onClick={() => toggleSchedule(schedule.id)}
                        style={{
                          padding: '6px 12px',
                          backgroundColor: schedule.is_active ? '#ff9800' : '#4CAF50',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '12px'
                        }}
                      >
                        {schedule.is_active ? '일시중지' : '활성화'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default BandMessageCenter;
