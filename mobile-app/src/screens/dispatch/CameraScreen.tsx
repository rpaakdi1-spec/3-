import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  Alert,
  ActivityIndicator,
  SafeAreaView,
} from 'react-native';
import { Camera, useCameraDevice } from 'react-native-vision-camera';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { DispatchStackParamList } from '../../types/navigation';
import api from '../../services/api';

type CameraScreenRouteProp = RouteProp<DispatchStackParamList, 'Camera'>;

const CameraScreen: React.FC = () => {
  const navigation = useNavigation();
  const route = useRoute<CameraScreenRouteProp>();
  const { dispatchId, routeId, photoType } = route.params;

  const [capturedPhoto, setCapturedPhoto] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [hasPermission, setHasPermission] = useState(false);

  const device = useCameraDevice('back');
  const camera = useRef<Camera>(null);

  // 카메라 권한 요청
  React.useEffect(() => {
    (async () => {
      const cameraPermission = await Camera.requestCameraPermission();
      setHasPermission(cameraPermission === 'granted');
    })();
  }, []);

  // 사진 촬영
  const takePhoto = async () => {
    if (camera.current) {
      try {
        const photo = await camera.current.takePhoto({
          qualityPrioritization: 'balanced',
          flash: 'off',
        });
        setCapturedPhoto(`file://${photo.path}`);
      } catch (error) {
        Alert.alert('오류', '사진 촬영에 실패했습니다.');
        console.error('Take photo error:', error);
      }
    }
  };

  // 사진 재촬영
  const retakePhoto = () => {
    setCapturedPhoto(null);
  };

  // 사진 업로드
  const uploadPhoto = async () => {
    if (!capturedPhoto) return;

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', {
        uri: capturedPhoto,
        type: 'image/jpeg',
        name: `${photoType}_${Date.now()}.jpg`,
      } as any);
      formData.append('dispatch_id', dispatchId.toString());
      formData.append('route_id', routeId.toString());
      formData.append('photo_type', photoType);

      await api.uploadPhoto(formData);

      Alert.alert('성공', '사진이 업로드되었습니다.', [
        {
          text: '확인',
          onPress: () => navigation.goBack(),
        },
      ]);
    } catch (error) {
      Alert.alert('오류', '사진 업로드에 실패했습니다.');
      console.error('Upload photo error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  if (!hasPermission) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.permissionText}>
          카메라 권한이 필요합니다.{'\n'}
          설정에서 카메라 권한을 허용해주세요.
        </Text>
      </SafeAreaView>
    );
  }

  if (!device) {
    return (
      <SafeAreaView style={styles.container}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>카메라를 불러오는 중...</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* 헤더 */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Text style={styles.backButtonText}>취소</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>
          {photoType === 'pickup' ? '상차 사진' : '하차 사진'}
        </Text>
        <View style={styles.placeholder} />
      </View>

      {/* 카메라 또는 캡처된 사진 */}
      {capturedPhoto ? (
        <View style={styles.previewContainer}>
          <Image source={{ uri: capturedPhoto }} style={styles.preview} />
          
          <View style={styles.actionButtons}>
            <TouchableOpacity
              style={[styles.actionButton, styles.retakeButton]}
              onPress={retakePhoto}
              disabled={isUploading}
            >
              <Text style={styles.actionButtonText}>재촬영</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.actionButton, styles.uploadButton]}
              onPress={uploadPhoto}
              disabled={isUploading}
            >
              {isUploading ? (
                <ActivityIndicator color="#FFF" />
              ) : (
                <Text style={styles.actionButtonText}>업로드</Text>
              )}
            </TouchableOpacity>
          </View>
        </View>
      ) : (
        <View style={styles.cameraContainer}>
          <Camera
            ref={camera}
            style={StyleSheet.absoluteFill}
            device={device}
            isActive={true}
            photo={true}
          />

          {/* 촬영 버튼 */}
          <View style={styles.captureButtonContainer}>
            <TouchableOpacity style={styles.captureButton} onPress={takePhoto}>
              <View style={styles.captureButtonInner} />
            </TouchableOpacity>
          </View>
        </View>
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#1C1C1E',
  },
  backButton: {
    padding: 8,
  },
  backButtonText: {
    color: '#007AFF',
    fontSize: 17,
  },
  headerTitle: {
    color: '#FFF',
    fontSize: 17,
    fontWeight: '600',
  },
  placeholder: {
    width: 60,
  },
  permissionText: {
    color: '#FFF',
    fontSize: 16,
    textAlign: 'center',
    marginTop: 100,
    paddingHorizontal: 32,
    lineHeight: 24,
  },
  loadingText: {
    color: '#FFF',
    fontSize: 16,
    textAlign: 'center',
    marginTop: 16,
  },
  cameraContainer: {
    flex: 1,
  },
  captureButtonContainer: {
    position: 'absolute',
    bottom: 40,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  captureButton: {
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  captureButtonInner: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#FFF',
  },
  previewContainer: {
    flex: 1,
  },
  preview: {
    flex: 1,
    resizeMode: 'contain',
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingHorizontal: 32,
    paddingVertical: 24,
    backgroundColor: '#1C1C1E',
  },
  actionButton: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
    marginHorizontal: 8,
  },
  retakeButton: {
    backgroundColor: '#48484A',
  },
  uploadButton: {
    backgroundColor: '#007AFF',
  },
  actionButtonText: {
    color: '#FFF',
    fontSize: 17,
    fontWeight: '600',
  },
});

export default CameraScreen;
