import { useState, useEffect, useCallback, useRef } from 'react';
import { toast } from 'react-hot-toast';

// Web Speech API 타입 선언
interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  abort(): void;
  onstart: ((this: SpeechRecognition, ev: Event) => any) | null;
  onend: ((this: SpeechRecognition, ev: Event) => any) | null;
  onerror: ((this: SpeechRecognition, ev: SpeechRecognitionErrorEvent) => any) | null;
  onresult: ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => any) | null;
}

declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognition;
    webkitSpeechRecognition: new () => SpeechRecognition;
  }
}

interface UseSpeechRecognitionReturn {
  isListening: boolean;
  transcript: string;
  startListening: () => void;
  stopListening: () => void;
  resetTranscript: () => void;
  isSupported: boolean;
  error: string | null;
}

export const useSpeechRecognition = (): UseSpeechRecognitionReturn => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  // 브라우저 지원 여부 확인
  const isSupported = typeof window !== 'undefined' && 
    ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window);

  useEffect(() => {
    if (!isSupported) {
      console.warn('음성 인식이 지원되지 않는 브라우저입니다.');
      return;
    }

    // SpeechRecognition 인스턴스 생성
    const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognitionAPI();

    // 설정
    recognition.continuous = false; // 한 번에 한 문장만
    recognition.interimResults = true; // 중간 결과 표시
    recognition.lang = 'ko-KR'; // 한국어

    // 이벤트 핸들러
    recognition.onstart = () => {
      console.log('🎤 음성 인식 시작');
      setIsListening(true);
      setError(null);
    };

    recognition.onend = () => {
      console.log('🎤 음성 인식 종료');
      setIsListening(false);
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      console.error('🎤 음성 인식 오류:', event.error);
      
      let errorMessage = '음성 인식 중 오류가 발생했습니다.';
      
      switch (event.error) {
        case 'no-speech':
          errorMessage = '음성이 감지되지 않았습니다. 다시 시도해주세요.';
          break;
        case 'audio-capture':
          errorMessage = '마이크에 접근할 수 없습니다. 권한을 확인해주세요.';
          break;
        case 'not-allowed':
          errorMessage = '마이크 사용 권한이 거부되었습니다.';
          break;
        case 'network':
          errorMessage = '네트워크 오류가 발생했습니다.';
          break;
        case 'aborted':
          // 사용자가 중단한 경우는 오류로 처리하지 않음
          errorMessage = '';
          break;
      }

      if (errorMessage) {
        setError(errorMessage);
        toast.error(errorMessage);
      }
      setIsListening(false);
    };

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        const transcriptPart = result[0].transcript;

        if (result.isFinal) {
          finalTranscript += transcriptPart + ' ';
        } else {
          interimTranscript += transcriptPart;
        }
      }

      // 최종 결과가 있으면 사용, 없으면 중간 결과 사용
      if (finalTranscript) {
        console.log('🎤 최종 인식 결과:', finalTranscript);
        setTranscript(prev => prev + finalTranscript);
      } else if (interimTranscript) {
        console.log('🎤 중간 인식 결과:', interimTranscript);
        // 중간 결과는 임시로만 표시 (여기서는 최종 결과만 사용)
      }
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, [isSupported]);

  const startListening = useCallback(() => {
    if (!isSupported) {
      toast.error('음성 인식이 지원되지 않는 브라우저입니다.');
      return;
    }

    if (!recognitionRef.current) {
      toast.error('음성 인식을 초기화할 수 없습니다.');
      return;
    }

    try {
      recognitionRef.current.start();
      toast.success('🎤 음성 인식을 시작합니다. 말씀해주세요!');
    } catch (error) {
      console.error('음성 인식 시작 오류:', error);
      if (isListening) {
        // 이미 실행 중인 경우 중지 후 재시작
        recognitionRef.current.stop();
        setTimeout(() => {
          recognitionRef.current?.start();
        }, 100);
      }
    }
  }, [isSupported, isListening]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  }, []);

  const resetTranscript = useCallback(() => {
    setTranscript('');
    setError(null);
  }, []);

  return {
    isListening,
    transcript,
    startListening,
    stopListening,
    resetTranscript,
    isSupported,
    error,
  };
};

export default useSpeechRecognition;
