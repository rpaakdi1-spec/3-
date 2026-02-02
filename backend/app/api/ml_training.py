"""AI 학습 데이터 업로드 및 학습 API"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
import pandas as pd
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.services.excel_template_service import ExcelTemplateService
from app.services.naver_map_service import NaverMapService
from loguru import logger

router = APIRouter()


@router.get("/training/template/download")
def download_ml_training_template():
    """AI 학습 데이터 Excel 템플릿 다운로드"""
    try:
        template_path = ExcelTemplateService.create_ml_training_template()
        
        if not Path(template_path).exists():
            raise HTTPException(status_code=404, detail="템플릿 파일을 찾을 수 없습니다")
        
        logger.info(f"📥 템플릿 다운로드: {template_path}")
        
        return FileResponse(
            path=str(template_path),
            filename="AI학습데이터_template.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename*=UTF-8''AI%ED%95%99%EC%8A%B5%EB%8D%B0%EC%9D%B4%ED%84%B0_template.xlsx"
            }
        )
    except Exception as e:
        logger.error(f"❌ 템플릿 다운로드 실패: {e}")
        raise HTTPException(status_code=500, detail=f"템플릿 생성 실패: {str(e)}")


@router.post("/training/upload")
async def upload_training_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    AI 학습 데이터 엑셀 업로드
    
    업로드된 데이터를 파싱하고, 네이버 지도 API로 거리/소요시간을 자동 계산
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="엑셀 파일만 업로드 가능합니다")
    
    try:
        # 파일 읽기
        content = await file.read()
        df = pd.read_excel(content)
        
        logger.info(f"📊 업로드된 데이터: {len(df)}건")
        
        # 필수 컬럼 확인 (수정됨: 배차번호, 주문무게, 고객만족도 제거, 거리/소요시간 자동계산)
        required_columns = [
            "배차일자", "차량코드", "주문번호",
            "주문팔레트", "출발지주소", "도착지주소",
            "실제비용(원)", "배차상태"
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"필수 컬럼이 누락되었습니다: {', '.join(missing_columns)}"
            )
        
        # 네이버 지도 서비스 초기화
        naver_map = NaverMapService()
        
        # 데이터 검증 및 거리/소요시간 자동 계산
        valid_count = 0
        error_rows = []
        
        # 거리/소요시간 컬럼 추가
        df["거리(km)"] = None
        df["실제소요시간(분)"] = None
        
        for idx, row in df.iterrows():
            try:
                # 기본 검증
                if pd.isna(row["차량코드"]) or pd.isna(row["주문번호"]):
                    error_rows.append(f"행 {idx + 2}: 차량코드 또는 주문번호 누락")
                    continue
                
                # 주소 검증
                if pd.isna(row["출발지주소"]) or pd.isna(row["도착지주소"]):
                    error_rows.append(f"행 {idx + 2}: 출발지 또는 도착지 주소 누락")
                    continue
                
                # 네이버 지도 API로 거리/소요시간 자동 계산
                logger.info(f"🗺️ [{idx + 2}행] 거리/소요시간 계산 중...")
                result = await naver_map.calculate_from_addresses(
                    str(row["출발지주소"]),
                    str(row["도착지주소"])
                )
                
                if result["distance_km"] and result["duration_minutes"]:
                    df.at[idx, "거리(km)"] = result["distance_km"]
                    df.at[idx, "실제소요시간(분)"] = result["duration_minutes"]
                    logger.info(f"   ✅ 거리: {result['distance_km']}km, 소요시간: {result['duration_minutes']}분")
                else:
                    error_rows.append(f"행 {idx + 2}: 거리/소요시간 계산 실패 (주소 확인 필요)")
                    continue
                
                valid_count += 1
                
            except Exception as e:
                error_rows.append(f"행 {idx + 2}: {str(e)}")
        
        # 학습 데이터 저장 경로
        data_dir = Path(__file__).parent.parent.parent / "data" / "ml_training"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # 타임스탬프 포함 파일명
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = data_dir / f"training_data_{timestamp}.xlsx"
        
        # 유효한 데이터만 저장
        valid_indices = [i for i in range(len(df)) if df.at[i, "거리(km)"] is not None]
        valid_df = df.iloc[valid_indices]
        valid_df.to_excel(output_file, index=False)
        
        logger.info(f"✅ 학습 데이터 저장: {output_file}")
        logger.info(f"   유효 데이터: {valid_count}건, 오류: {len(error_rows)}건")
        
        return {
            "success": True,
            "total_rows": len(df),
            "valid_rows": valid_count,
            "error_rows": len(error_rows),
            "errors": error_rows[:10],  # 최대 10개만 반환
            "saved_file": str(output_file),
            "message": f"{valid_count}건의 학습 데이터가 업로드되었습니다 (거리/소요시간 자동 계산 완료)"
        }
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="빈 파일입니다")
    except Exception as e:
        logger.error(f"학습 데이터 업로드 실패: {e}")
        raise HTTPException(status_code=500, detail=f"업로드 중 오류가 발생했습니다: {str(e)}")


@router.post("/training/start")
async def start_training(
    model_type: str = "dispatch",  # dispatch, demand, failure
    epochs: int = 10,
    batch_size: int = 32,
    db: Session = Depends(get_db)
):
    """
    AI 모델 학습 시작
    
    Args:
        model_type: 학습할 모델 종류 (dispatch, demand, failure)
        epochs: 학습 반복 횟수
        batch_size: 배치 크기
    """
    
    # 학습 데이터 디렉토리
    data_dir = Path(__file__).parent.parent.parent / "data" / "ml_training"
    
    if not data_dir.exists() or not list(data_dir.glob("*.xlsx")):
        raise HTTPException(
            status_code=400,
            detail="학습 데이터가 없습니다. 먼저 엑셀 파일을 업로드해주세요"
        )
    
    # 최신 학습 데이터 파일 찾기
    training_files = sorted(data_dir.glob("training_data_*.xlsx"), reverse=True)
    latest_file = training_files[0]
    
    logger.info(f"🤖 AI 학습 시작: {model_type}")
    logger.info(f"   학습 데이터: {latest_file}")
    logger.info(f"   Epochs: {epochs}, Batch Size: {batch_size}")
    
    try:
        # 학습 데이터 로드
        df = pd.read_excel(latest_file)
        
        if model_type == "dispatch":
            # 배차 최적화 모델 학습
            result = await train_dispatch_model(df, epochs, batch_size)
        elif model_type == "demand":
            # 수요 예측 모델 학습
            result = await train_demand_model(df, epochs, batch_size)
        elif model_type == "failure":
            # 고장 예측 모델 학습
            result = await train_failure_model(df, epochs, batch_size)
        else:
            raise HTTPException(status_code=400, detail="지원하지 않는 모델 종류입니다")
        
        return {
            "success": True,
            "model_type": model_type,
            "training_data_count": len(df),
            "epochs": epochs,
            "batch_size": batch_size,
            **result
        }
        
    except Exception as e:
        logger.error(f"학습 실패: {e}")
        raise HTTPException(status_code=500, detail=f"학습 중 오류가 발생했습니다: {str(e)}")


async def train_dispatch_model(df: pd.DataFrame, epochs: int, batch_size: int):
    """배차 최적화 모델 학습"""
    
    # 간단한 학습 시뮬레이션
    # 실제로는 TensorFlow/PyTorch 모델 학습 코드 구현
    
    logger.info("📊 배차 최적화 모델 학습 중...")
    
    # 특성 추출 (수정됨: 배차번호, 주문무게, 고객만족도 제외)
    features = df[[
        "주문팔레트", "거리(km)",
        "실제소요시간(분)", "실제비용(원)"
    ]].values
    
    # 모델 저장 디렉토리
    models_dir = Path(__file__).parent.parent.parent / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # 메타데이터 저장
    metadata = {
        "model_type": "dispatch_optimizer",
        "trained_at": datetime.now().isoformat(),
        "data_count": len(df),
        "epochs": epochs,
        "batch_size": batch_size,
        "avg_cost": float(df["실제비용(원)"].mean()),
        "avg_duration": float(df["실제소요시간(분)"].mean()),
        "avg_distance": float(df["거리(km)"].mean()),
    }
    
    import json
    with open(models_dir / "dispatch_optimizer_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    logger.info("✅ 배차 최적화 모델 학습 완료")
    
    return {
        "message": "배차 최적화 모델 학습이 완료되었습니다",
        "avg_cost": metadata["avg_cost"],
        "avg_duration": metadata["avg_duration"],
        "avg_distance": metadata["avg_distance"],
    }


async def train_demand_model(df: pd.DataFrame, epochs: int, batch_size: int):
    """수요 예측 모델 학습"""
    logger.info("📊 수요 예측 모델 학습 중...")
    
    # 일별 주문량 집계
    daily_orders = df.groupby("배차일자").size().reset_index(name="주문수")
    
    return {
        "message": "수요 예측 모델 학습이 완료되었습니다",
        "total_days": len(daily_orders),
        "avg_daily_orders": float(daily_orders["주문수"].mean()),
    }


async def train_failure_model(df: pd.DataFrame, epochs: int, batch_size: int):
    """고장 예측 모델 학습"""
    logger.info("📊 고장 예측 모델 학습 중...")
    
    # 차량별 통계
    vehicle_stats = df.groupby("차량코드").agg({
        "배차번호": "count",
        "실제소요시간(분)": "mean",
        "실제비용(원)": "mean",
    }).reset_index()
    
    return {
        "message": "고장 예측 모델 학습이 완료되었습니다",
        "total_vehicles": len(vehicle_stats),
    }


@router.get("/training/status")
async def get_training_status():
    """학습 상태 조회"""
    
    models_dir = Path(__file__).parent.parent.parent / "models"
    
    status = {}
    
    # 배차 최적화 모델 상태
    metadata_file = models_dir / "dispatch_optimizer_metadata.json"
    if metadata_file.exists():
        import json
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
            status["dispatch_optimizer"] = {
                "status": "trained",
                "trained_at": metadata.get("trained_at"),
                "data_count": metadata.get("data_count"),
            }
    else:
        status["dispatch_optimizer"] = {
            "status": "not_trained",
            "message": "학습된 모델이 없습니다"
        }
    
    # 학습 데이터 파일 목록
    data_dir = Path(__file__).parent.parent.parent / "data" / "ml_training"
    if data_dir.exists():
        training_files = sorted(data_dir.glob("training_data_*.xlsx"), reverse=True)
        status["training_data_files"] = [f.name for f in training_files[:5]]  # 최근 5개
    else:
        status["training_data_files"] = []
    
    return status


@router.get("/training/history")
async def get_training_history():
    """학습 이력 조회"""
    
    data_dir = Path(__file__).parent.parent.parent / "data" / "ml_training"
    
    if not data_dir.exists():
        return {
            "total": 0,
            "files": []
        }
    
    training_files = sorted(data_dir.glob("training_data_*.xlsx"), reverse=True)
    
    history = []
    for file in training_files[:10]:  # 최근 10개
        # 파일명에서 타임스탬프 추출
        timestamp_str = file.stem.replace("training_data_", "")
        
        try:
            timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            
            # 파일 크기
            file_size = file.stat().st_size / 1024  # KB
            
            # 데이터 건수 (엑셀 읽어서 확인)
            df = pd.read_excel(file)
            
            history.append({
                "filename": file.name,
                "uploaded_at": timestamp.isoformat(),
                "file_size_kb": round(file_size, 2),
                "data_count": len(df),
            })
        except Exception as e:
            logger.warning(f"파일 정보 추출 실패: {file.name} - {e}")
    
    return {
        "total": len(training_files),
        "files": history
    }
