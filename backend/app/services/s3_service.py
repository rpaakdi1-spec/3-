"""
S3 (MinIO) 파일 스토리지 서비스
"""

import os
import io
import logging
from typing import Optional, BinaryIO, List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import mimetypes

import boto3
from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError
from botocore.client import Config
from PIL import Image

logger = logging.getLogger(__name__)


class S3Service:
    """S3/MinIO 파일 스토리지 서비스"""
    
    def __init__(self):
        """S3 클라이언트 초기화"""
        self.endpoint = os.getenv("S3_ENDPOINT", "http://localhost:9000")
        self.access_key = os.getenv("S3_ACCESS_KEY", "minioadmin")
        self.secret_key = os.getenv("S3_SECRET_KEY", "minioadmin123")
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "uvis-files")
        self.region = os.getenv("S3_REGION", "us-east-1")
        self.use_ssl = os.getenv("S3_USE_SSL", "false").lower() == "true"
        
        # S3 클라이언트 생성
        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
            config=Config(signature_version='s3v4'),
            use_ssl=self.use_ssl
        )
        
        # 버킷 생성 (존재하지 않으면)
        self._ensure_bucket_exists()
        
        logger.info(f"✅ S3Service initialized: endpoint={self.endpoint}, bucket={self.bucket_name}")
    
    def _ensure_bucket_exists(self):
        """버킷이 존재하는지 확인하고 없으면 생성"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"✅ Bucket '{self.bucket_name}' exists")
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == '404':
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"✅ Bucket '{self.bucket_name}' created")
                except ClientError as create_error:
                    logger.error(f"❌ Failed to create bucket: {create_error}")
            else:
                logger.error(f"❌ Error checking bucket: {e}")
    
    def upload_file(
        self,
        file_data: BinaryIO,
        file_name: str,
        folder: str = "uploads",
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        파일 업로드
        
        Args:
            file_data: 파일 데이터 (바이너리)
            file_name: 파일명
            folder: 폴더 경로 (기본: uploads)
            content_type: MIME 타입
            metadata: 메타데이터 (딕셔너리)
            
        Returns:
            업로드 결과 (url, key, size 등)
        """
        try:
            # 파일명 정리 (안전한 이름)
            safe_name = self._sanitize_filename(file_name)
            
            # S3 키 생성 (폴더/년월일/타임스탬프_파일명)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            date_folder = datetime.now().strftime("%Y/%m/%d")
            s3_key = f"{folder}/{date_folder}/{timestamp}_{safe_name}"
            
            # Content-Type 자동 감지
            if not content_type:
                content_type, _ = mimetypes.guess_type(safe_name)
                if not content_type:
                    content_type = 'application/octet-stream'
            
            # 메타데이터 준비
            extra_args = {
                'ContentType': content_type,
                'Metadata': metadata or {}
            }
            
            # 파일 업로드
            file_data.seek(0)  # 파일 포인터를 처음으로
            self.s3_client.upload_fileobj(
                file_data,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )
            
            # 파일 URL 생성
            file_url = f"{self.endpoint}/{self.bucket_name}/{s3_key}"
            
            # 파일 크기 가져오기
            file_data.seek(0, 2)  # 파일 끝으로 이동
            file_size = file_data.tell()
            
            logger.info(f"✅ File uploaded: {s3_key} ({file_size} bytes)")
            
            return {
                "success": True,
                "url": file_url,
                "key": s3_key,
                "bucket": self.bucket_name,
                "size": file_size,
                "content_type": content_type,
                "uploaded_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ File upload failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def upload_image(
        self,
        image_data: BinaryIO,
        file_name: str,
        folder: str = "images",
        max_width: int = 1920,
        max_height: int = 1080,
        quality: int = 85
    ) -> Dict[str, Any]:
        """
        이미지 업로드 (자동 최적화)
        
        Args:
            image_data: 이미지 데이터
            file_name: 파일명
            folder: 폴더 경로
            max_width: 최대 너비
            max_height: 최대 높이
            quality: 압축 품질 (1-100)
            
        Returns:
            업로드 결과
        """
        try:
            # 이미지 열기
            image = Image.open(image_data)
            
            # 원본 크기 저장
            original_size = image.size
            
            # 이미지 리사이즈 (비율 유지)
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # RGB 변환 (PNG 투명도 제거)
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 메모리에 JPEG로 저장
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)
            output.seek(0)
            
            # 파일명을 .jpg로 변경
            file_name_without_ext = Path(file_name).stem
            optimized_file_name = f"{file_name_without_ext}.jpg"
            
            # 메타데이터
            metadata = {
                'original_size': f"{original_size[0]}x{original_size[1]}",
                'optimized_size': f"{image.size[0]}x{image.size[1]}",
                'quality': str(quality)
            }
            
            # 업로드
            result = self.upload_file(
                output,
                optimized_file_name,
                folder=folder,
                content_type='image/jpeg',
                metadata=metadata
            )
            
            if result.get('success'):
                logger.info(
                    f"✅ Image optimized and uploaded: "
                    f"{original_size} → {image.size}, "
                    f"quality={quality}"
                )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Image upload failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_file(self, s3_key: str) -> Optional[bytes]:
        """
        파일 다운로드
        
        Args:
            s3_key: S3 키
            
        Returns:
            파일 데이터 (바이트)
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            data = response['Body'].read()
            logger.info(f"✅ File downloaded: {s3_key}")
            return data
            
        except ClientError as e:
            logger.error(f"❌ File download failed: {e}")
            return None
    
    def delete_file(self, s3_key: str) -> bool:
        """
        파일 삭제
        
        Args:
            s3_key: S3 키
            
        Returns:
            성공 여부
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            logger.info(f"✅ File deleted: {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"❌ File deletion failed: {e}")
            return False
    
    def list_files(self, prefix: str = "", max_keys: int = 100) -> List[Dict[str, Any]]:
        """
        파일 목록 조회
        
        Args:
            prefix: 접두어 (폴더 경로)
            max_keys: 최대 개수
            
        Returns:
            파일 목록
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'url': f"{self.endpoint}/{self.bucket_name}/{obj['Key']}"
                })
            
            logger.info(f"✅ Listed {len(files)} files with prefix '{prefix}'")
            return files
            
        except ClientError as e:
            logger.error(f"❌ File listing failed: {e}")
            return []
    
    def generate_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600,
        http_method: str = 'GET'
    ) -> Optional[str]:
        """
        미리 서명된 URL 생성 (임시 접근 링크)
        
        Args:
            s3_key: S3 키
            expiration: 만료 시간 (초, 기본 1시간)
            http_method: HTTP 메서드 ('GET' 또는 'PUT')
            
        Returns:
            미리 서명된 URL
        """
        try:
            if http_method == 'GET':
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': self.bucket_name,
                        'Key': s3_key
                    },
                    ExpiresIn=expiration
                )
            elif http_method == 'PUT':
                url = self.s3_client.generate_presigned_url(
                    'put_object',
                    Params={
                        'Bucket': self.bucket_name,
                        'Key': s3_key
                    },
                    ExpiresIn=expiration
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {http_method}")
            
            logger.info(f"✅ Presigned URL generated: {s3_key} (expires in {expiration}s)")
            return url
            
        except ClientError as e:
            logger.error(f"❌ Presigned URL generation failed: {e}")
            return None
    
    def _sanitize_filename(self, filename: str) -> str:
        """파일명 안전하게 정리"""
        # 특수문자 제거
        safe_chars = ('-', '_', '.')
        sanitized = ''.join(
            c for c in filename
            if c.isalnum() or c in safe_chars or ord(c) > 127  # 한글 허용
        )
        
        # 공백을 언더스코어로
        sanitized = sanitized.replace(' ', '_')
        
        return sanitized or 'unnamed_file'


# 싱글톤 인스턴스
_s3_service_instance = None


def get_s3_service() -> S3Service:
    """S3 서비스 인스턴스 가져오기 (싱글톤)"""
    global _s3_service_instance
    
    if _s3_service_instance is None:
        _s3_service_instance = S3Service()
    
    return _s3_service_instance
