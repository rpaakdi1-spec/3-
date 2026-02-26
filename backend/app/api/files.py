"""
파일 업로드 API 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import io
import logging

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.services.s3_service import get_s3_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ===== Schemas =====

class FileUploadResponse(BaseModel):
    """파일 업로드 응답"""
    success: bool
    message: str
    url: Optional[str] = None
    key: Optional[str] = None
    size: Optional[int] = None
    content_type: Optional[str] = None


class FileListResponse(BaseModel):
    """파일 목록 응답"""
    files: List[dict]
    total: int


# ===== API Endpoints =====

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    folder: str = Form("uploads"),
    current_user: User = Depends(get_current_user)
):
    """
    파일 업로드
    
    - 일반 파일을 S3/MinIO에 업로드합니다.
    - 지원 형식: 모든 파일 (문서, 이미지, PDF 등)
    - 최대 크기: 50MB
    """
    try:
        # 파일 크기 확인
        max_size = 50 * 1024 * 1024  # 50MB
        contents = await file.read()
        
        if len(contents) > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {max_size // (1024 * 1024)}MB"
            )
        
        # S3 서비스
        s3_service = get_s3_service()
        
        # 파일 업로드
        file_data = io.BytesIO(contents)
        result = s3_service.upload_file(
            file_data=file_data,
            file_name=file.filename,
            folder=folder,
            content_type=file.content_type
        )
        
        if result.get('success'):
            return FileUploadResponse(
                success=True,
                message="파일이 업로드되었습니다.",
                url=result.get('url'),
                key=result.get('key'),
                size=result.get('size'),
                content_type=result.get('content_type')
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Upload failed')
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"파일 업로드 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-image", response_model=FileUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    folder: str = Form("images"),
    max_width: int = Form(1920),
    max_height: int = Form(1080),
    quality: int = Form(85),
    current_user: User = Depends(get_current_user)
):
    """
    이미지 업로드 (자동 최적화)
    
    - 이미지를 자동으로 리사이즈 및 압축하여 업로드합니다.
    - 지원 형식: JPG, PNG, GIF, BMP, WEBP
    - 최대 원본 크기: 20MB
    - 출력 형식: JPEG (최적화)
    """
    try:
        # 이미지 파일 확인
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="이미지 파일만 업로드 가능합니다."
            )
        
        # 파일 크기 확인
        max_size = 20 * 1024 * 1024  # 20MB
        contents = await file.read()
        
        if len(contents) > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"이미지가 너무 큽니다. 최대 크기는 {max_size // (1024 * 1024)}MB입니다."
            )
        
        # 품질 범위 확인
        if not 1 <= quality <= 100:
            quality = 85
        
        # S3 서비스
        s3_service = get_s3_service()
        
        # 이미지 업로드 (최적화)
        image_data = io.BytesIO(contents)
        result = s3_service.upload_image(
            image_data=image_data,
            file_name=file.filename,
            folder=folder,
            max_width=max_width,
            max_height=max_height,
            quality=quality
        )
        
        if result.get('success'):
            return FileUploadResponse(
                success=True,
                message="이미지가 업로드되었습니다.",
                url=result.get('url'),
                key=result.get('key'),
                size=result.get('size'),
                content_type='image/jpeg'
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Image upload failed')
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"이미지 업로드 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-multiple", response_model=List[FileUploadResponse])
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    folder: str = Form("uploads"),
    current_user: User = Depends(get_current_user)
):
    """
    여러 파일 업로드
    
    - 한 번에 여러 파일을 업로드합니다.
    - 최대 10개까지 동시 업로드 가능
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="한 번에 최대 10개 파일만 업로드 가능합니다."
        )
    
    results = []
    s3_service = get_s3_service()
    
    for file in files:
        try:
            contents = await file.read()
            
            # 크기 확인
            if len(contents) > 50 * 1024 * 1024:  # 50MB
                results.append(FileUploadResponse(
                    success=False,
                    message=f"{file.filename}: 파일이 너무 큽니다 (최대 50MB)"
                ))
                continue
            
            # 업로드
            file_data = io.BytesIO(contents)
            result = s3_service.upload_file(
                file_data=file_data,
                file_name=file.filename,
                folder=folder,
                content_type=file.content_type
            )
            
            if result.get('success'):
                results.append(FileUploadResponse(
                    success=True,
                    message=f"{file.filename}: 업로드 완료",
                    url=result.get('url'),
                    key=result.get('key'),
                    size=result.get('size'),
                    content_type=result.get('content_type')
                ))
            else:
                results.append(FileUploadResponse(
                    success=False,
                    message=f"{file.filename}: 업로드 실패 - {result.get('error')}"
                ))
        
        except Exception as e:
            logger.error(f"파일 업로드 오류 ({file.filename}): {e}")
            results.append(FileUploadResponse(
                success=False,
                message=f"{file.filename}: 오류 - {str(e)}"
            ))
    
    return results


@router.get("/list", response_model=FileListResponse)
async def list_files(
    folder: str = "uploads",
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """
    파일 목록 조회
    
    - 특정 폴더의 파일 목록을 반환합니다.
    """
    try:
        s3_service = get_s3_service()
        
        files = s3_service.list_files(
            prefix=folder,
            max_keys=limit
        )
        
        return FileListResponse(
            files=files,
            total=len(files)
        )
    
    except Exception as e:
        logger.error(f"파일 목록 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{s3_key:path}")
async def delete_file(
    s3_key: str,
    current_user: User = Depends(get_current_user)
):
    """
    파일 삭제
    
    - S3/MinIO에서 파일을 삭제합니다.
    - 관리자 권한 필요
    """
    # 관리자 권한 확인
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(
            status_code=403,
            detail="파일 삭제 권한이 없습니다."
        )
    
    try:
        s3_service = get_s3_service()
        
        success = s3_service.delete_file(s3_key)
        
        if success:
            return {"success": True, "message": "파일이 삭제되었습니다."}
        else:
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"파일 삭제 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{s3_key:path}")
async def download_file(
    s3_key: str,
    current_user: User = Depends(get_current_user)
):
    """
    파일 다운로드
    
    - S3/MinIO에서 파일을 다운로드합니다.
    """
    try:
        s3_service = get_s3_service()
        
        file_data = s3_service.get_file(s3_key)
        
        if file_data:
            # 파일명 추출
            file_name = s3_key.split('/')[-1]
            
            return StreamingResponse(
                io.BytesIO(file_data),
                media_type='application/octet-stream',
                headers={
                    'Content-Disposition': f'attachment; filename="{file_name}"'
                }
            )
        else:
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"파일 다운로드 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presigned-url/{s3_key:path}")
async def generate_presigned_url(
    s3_key: str,
    expiration: int = 3600,
    current_user: User = Depends(get_current_user)
):
    """
    미리 서명된 URL 생성
    
    - 임시 접근 링크를 생성합니다.
    - 기본 만료 시간: 1시간
    """
    try:
        s3_service = get_s3_service()
        
        url = s3_service.generate_presigned_url(
            s3_key=s3_key,
            expiration=expiration
        )
        
        if url:
            return {
                "success": True,
                "url": url,
                "expires_in": expiration
            }
        else:
            raise HTTPException(status_code=500, detail="URL 생성 실패")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"URL 생성 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))
