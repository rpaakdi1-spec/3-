import { Camera } from 'expo-camera';
import * as ImagePicker from 'expo-image-picker';
import * as FileSystem from 'expo-file-system';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { StorageKeys } from '../types';

interface PhotoMetadata {
  uri: string;
  timestamp: string;
  location?: {
    latitude: number;
    longitude: number;
  };
}

interface UploadResult {
  success: boolean;
  url?: string;
  error?: string;
}

class CameraService {
  private apiBaseUrl: string = '';

  constructor() {
    this.loadSettings();
  }

  private async loadSettings() {
    try {
      const settings = await AsyncStorage.getItem(StorageKeys.SETTINGS);
      if (settings) {
        const parsed = JSON.parse(settings);
        this.apiBaseUrl = parsed.apiBaseUrl || 'http://localhost:8000';
      }
    } catch (error) {
      console.error('Failed to load camera settings:', error);
    }
  }

  /**
   * 카메라 권한 요청
   */
  async requestCameraPermission(): Promise<boolean> {
    try {
      const { status } = await Camera.requestCameraPermissionsAsync();
      return status === 'granted';
    } catch (error) {
      console.error('Failed to request camera permission:', error);
      return false;
    }
  }

  /**
   * 갤러리 권한 요청
   */
  async requestMediaLibraryPermission(): Promise<boolean> {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      return status === 'granted';
    } catch (error) {
      console.error('Failed to request media library permission:', error);
      return false;
    }
  }

  /**
   * 사진 촬영
   */
  async takePicture(): Promise<PhotoMetadata | null> {
    try {
      const hasPermission = await this.requestCameraPermission();
      if (!hasPermission) {
        throw new Error('Camera permission not granted');
      }

      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
        exif: true,
      });

      if (result.canceled) {
        return null;
      }

      const photo = result.assets[0];
      
      return {
        uri: photo.uri,
        timestamp: new Date().toISOString(),
        location: photo.exif?.GPSLatitude && photo.exif?.GPSLongitude
          ? {
              latitude: this.convertExifCoordinate(photo.exif.GPSLatitude, photo.exif.GPSLatitudeRef),
              longitude: this.convertExifCoordinate(photo.exif.GPSLongitude, photo.exif.GPSLongitudeRef),
            }
          : undefined,
      };
    } catch (error) {
      console.error('Failed to take picture:', error);
      throw error;
    }
  }

  /**
   * 갤러리에서 사진 선택
   */
  async pickFromGallery(): Promise<PhotoMetadata | null> {
    try {
      const hasPermission = await this.requestMediaLibraryPermission();
      if (!hasPermission) {
        throw new Error('Media library permission not granted');
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
        exif: true,
      });

      if (result.canceled) {
        return null;
      }

      const photo = result.assets[0];
      
      return {
        uri: photo.uri,
        timestamp: new Date().toISOString(),
        location: photo.exif?.GPSLatitude && photo.exif?.GPSLongitude
          ? {
              latitude: this.convertExifCoordinate(photo.exif.GPSLatitude, photo.exif.GPSLatitudeRef),
              longitude: this.convertExifCoordinate(photo.exif.GPSLongitude, photo.exif.GPSLongitudeRef),
            }
          : undefined,
      };
    } catch (error) {
      console.error('Failed to pick from gallery:', error);
      throw error;
    }
  }

  /**
   * EXIF 좌표 변환
   */
  private convertExifCoordinate(coordinate: number[], ref: string): number {
    const decimal = coordinate[0] + coordinate[1] / 60 + coordinate[2] / 3600;
    return ref === 'S' || ref === 'W' ? -decimal : decimal;
  }

  /**
   * 배송 증명 사진 업로드 (픽업/배송)
   */
  async uploadDeliveryProof(
    dispatchId: number,
    photo: PhotoMetadata,
    type: 'pickup' | 'delivery'
  ): Promise<UploadResult> {
    try {
      const token = await AsyncStorage.getItem(StorageKeys.AUTH_TOKEN);
      
      // FormData 생성
      const formData = new FormData();
      
      const filename = photo.uri.split('/').pop() || 'photo.jpg';
      const match = /\.(\w+)$/.exec(filename);
      const fileType = match ? `image/${match[1]}` : 'image/jpeg';

      formData.append('file', {
        uri: photo.uri,
        name: filename,
        type: fileType,
      } as any);

      formData.append('type', type);
      formData.append('timestamp', photo.timestamp);
      
      if (photo.location) {
        formData.append('latitude', photo.location.latitude.toString());
        formData.append('longitude', photo.location.longitude.toString());
      }

      const response = await axios.post(
        `${this.apiBaseUrl}/api/v1/dispatches/${dispatchId}/photos`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data',
          },
          timeout: 30000,
        }
      );

      return {
        success: true,
        url: response.data.url,
      };
    } catch (error: any) {
      console.error('Failed to upload delivery proof:', error);
      
      // 오프라인 큐에 추가
      await this.addToOfflineQueue(dispatchId, photo, type);
      
      return {
        success: false,
        error: error.message || 'Upload failed',
      };
    }
  }

  /**
   * 온도 이상 사진 업로드
   */
  async uploadTemperatureAlert(
    vehicleId: number,
    photo: PhotoMetadata,
    temperature: number
  ): Promise<UploadResult> {
    try {
      const token = await AsyncStorage.getItem(StorageKeys.AUTH_TOKEN);
      
      const formData = new FormData();
      
      const filename = photo.uri.split('/').pop() || 'photo.jpg';
      const match = /\.(\w+)$/.exec(filename);
      const fileType = match ? `image/${match[1]}` : 'image/jpeg';

      formData.append('file', {
        uri: photo.uri,
        name: filename,
        type: fileType,
      } as any);

      formData.append('type', 'temperature_alert');
      formData.append('timestamp', photo.timestamp);
      formData.append('temperature', temperature.toString());
      
      if (photo.location) {
        formData.append('latitude', photo.location.latitude.toString());
        formData.append('longitude', photo.location.longitude.toString());
      }

      const response = await axios.post(
        `${this.apiBaseUrl}/api/v1/vehicles/${vehicleId}/photos`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data',
          },
          timeout: 30000,
        }
      );

      return {
        success: true,
        url: response.data.url,
      };
    } catch (error: any) {
      console.error('Failed to upload temperature alert photo:', error);
      return {
        success: false,
        error: error.message || 'Upload failed',
      };
    }
  }

  /**
   * 오프라인 큐에 추가
   */
  private async addToOfflineQueue(
    dispatchId: number,
    photo: PhotoMetadata,
    type: 'pickup' | 'delivery'
  ): Promise<void> {
    try {
      const key = StorageKeys.OFFLINE_DATA;
      const existingData = await AsyncStorage.getItem(key);
      const offlineData = existingData ? JSON.parse(existingData) : { photoQueue: [] };

      offlineData.photoQueue = offlineData.photoQueue || [];
      offlineData.photoQueue.push({
        dispatchId,
        photo,
        type,
        timestamp: new Date().toISOString(),
      });

      await AsyncStorage.setItem(key, JSON.stringify(offlineData));
      console.log('Photo added to offline queue');
    } catch (error) {
      console.error('Failed to add photo to offline queue:', error);
    }
  }

  /**
   * 오프라인 사진 동기화
   */
  async syncOfflinePhotos(): Promise<void> {
    try {
      const key = StorageKeys.OFFLINE_DATA;
      const existingData = await AsyncStorage.getItem(key);
      if (!existingData) return;

      const offlineData = JSON.parse(existingData);
      const photoQueue = offlineData.photoQueue || [];

      if (photoQueue.length === 0) return;

      console.log(`Syncing ${photoQueue.length} offline photos...`);

      const failedItems: any[] = [];

      for (const item of photoQueue) {
        const result = await this.uploadDeliveryProof(
          item.dispatchId,
          item.photo,
          item.type
        );

        if (!result.success) {
          failedItems.push(item);
        }
      }

      // 실패한 항목만 큐에 남김
      offlineData.photoQueue = failedItems;
      await AsyncStorage.setItem(key, JSON.stringify(offlineData));

      console.log(`Synced ${photoQueue.length - failedItems.length} photos, ${failedItems.length} failed`);
    } catch (error) {
      console.error('Failed to sync offline photos:', error);
    }
  }

  /**
   * 로컬 사진 삭제
   */
  async deleteLocalPhoto(uri: string): Promise<void> {
    try {
      const fileInfo = await FileSystem.getInfoAsync(uri);
      if (fileInfo.exists) {
        await FileSystem.deleteAsync(uri);
      }
    } catch (error) {
      console.error('Failed to delete local photo:', error);
    }
  }
}

export default new CameraService();
