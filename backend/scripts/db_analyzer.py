"""
데이터베이스 분석 및 최적화 도구
쿼리 성능 분석, 인덱스 사용률 분석, 느린 쿼리 식별
"""
import sys
import os
from typing import List, Dict, Any
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from loguru import logger

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings


class DatabaseAnalyzer:
    """데이터베이스 분석 클래스"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or settings.DATABASE_URL
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
        self.inspector = inspect(self.engine)
    
    def analyze_table_sizes(self) -> List[Dict[str, Any]]:
        """테이블 크기 분석"""
        logger.info("📊 테이블 크기 분석 중...")
        
        results = []
        tables = self.inspector.get_table_names()
        
        with self.Session() as session:
            for table in tables:
                try:
                    # PostgreSQL
                    if 'postgresql' in self.database_url:
                        query = text(f"""
                            SELECT 
                                '{table}' as table_name,
                                pg_size_pretty(pg_total_relation_size('{table}')) as total_size,
                                pg_size_pretty(pg_relation_size('{table}')) as table_size,
                                pg_size_pretty(pg_indexes_size('{table}')) as indexes_size,
                                (SELECT COUNT(*) FROM {table}) as row_count
                        """)
                        result = session.execute(query).fetchone()
                        results.append({
                            'table_name': result[0],
                            'total_size': result[1],
                            'table_size': result[2],
                            'indexes_size': result[3],
                            'row_count': result[4]
                        })
                    # SQLite
                    else:
                        query = text(f"SELECT COUNT(*) FROM {table}")
                        count = session.execute(query).scalar()
                        results.append({
                            'table_name': table,
                            'row_count': count
                        })
                except Exception as e:
                    logger.warning(f"테이블 {table} 분석 실패: {e}")
        
        return results
    
    def analyze_indexes(self) -> Dict[str, List[Dict]]:
        """인덱스 분석"""
        logger.info("🔍 인덱스 분석 중...")
        
        results = {}
        tables = self.inspector.get_table_names()
        
        for table in tables:
            indexes = self.inspector.get_indexes(table)
            results[table] = indexes
        
        return results
    
    def check_missing_indexes(self) -> List[Dict[str, Any]]:
        """누락된 인덱스 확인"""
        logger.info("⚠️  누락된 인덱스 확인 중...")
        
        recommendations = []
        
        # 주요 외래 키 컬럼 확인
        fk_checks = {
            'orders': ['pickup_client_id', 'delivery_client_id'],
            'dispatches': ['vehicle_id', 'driver_id'],
            'dispatch_routes': ['dispatch_id', 'order_id'],
            'vehicle_locations': ['vehicle_id', 'dispatch_id']
        }
        
        existing_indexes = self.analyze_indexes()
        
        for table, columns in fk_checks.items():
            if table not in existing_indexes:
                continue
            
            table_indexes = existing_indexes[table]
            indexed_columns = set()
            for index in table_indexes:
                indexed_columns.update(index['column_names'])
            
            for column in columns:
                if column not in indexed_columns:
                    recommendations.append({
                        'table': table,
                        'column': column,
                        'reason': '외래 키 컬럼에 인덱스 없음',
                        'suggestion': f'CREATE INDEX idx_{table}_{column} ON {table}({column});'
                    })
        
        return recommendations
    
    def analyze_query_performance(self, query: str) -> Dict[str, Any]:
        """쿼리 성능 분석 (EXPLAIN)"""
        logger.info(f"🔬 쿼리 성능 분석: {query[:50]}...")
        
        with self.Session() as session:
            try:
                # PostgreSQL EXPLAIN ANALYZE
                if 'postgresql' in self.database_url:
                    explain_query = text(f"EXPLAIN ANALYZE {query}")
                    result = session.execute(explain_query)
                    explain_output = [row[0] for row in result]
                    return {
                        'query': query,
                        'explain': explain_output,
                        'database': 'postgresql'
                    }
                # SQLite EXPLAIN QUERY PLAN
                else:
                    explain_query = text(f"EXPLAIN QUERY PLAN {query}")
                    result = session.execute(explain_query)
                    explain_output = [dict(row) for row in result]
                    return {
                        'query': query,
                        'explain': explain_output,
                        'database': 'sqlite'
                    }
            except Exception as e:
                logger.error(f"쿼리 분석 실패: {e}")
                return {'error': str(e)}
    
    def get_connection_pool_stats(self) -> Dict[str, Any]:
        """커넥션 풀 통계"""
        pool = self.engine.pool
        return {
            'pool_size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'status': 'healthy' if pool.checkedin() > 0 else 'warning'
        }
    
    def optimize_vacuum(self):
        """데이터베이스 정리 (PostgreSQL VACUUM, SQLite VACUUM)"""
        logger.info("🧹 데이터베이스 정리 중...")
        
        with self.Session() as session:
            try:
                if 'postgresql' in self.database_url:
                    # PostgreSQL VACUUM ANALYZE
                    session.execute(text("VACUUM ANALYZE"))
                    logger.success("✅ PostgreSQL VACUUM ANALYZE 완료")
                else:
                    # SQLite VACUUM
                    session.execute(text("VACUUM"))
                    logger.success("✅ SQLite VACUUM 완료")
                session.commit()
            except Exception as e:
                logger.error(f"VACUUM 실패: {e}")
    
    def generate_report(self) -> str:
        """종합 분석 보고서 생성"""
        logger.info("📝 분석 보고서 생성 중...")
        
        report = []
        report.append("=" * 80)
        report.append(f"데이터베이스 분석 보고서 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")
        
        # 1. 테이블 크기
        report.append("📊 테이블 크기 분석")
        report.append("-" * 80)
        table_sizes = self.analyze_table_sizes()
        for table in table_sizes:
            if 'total_size' in table:
                report.append(f"  {table['table_name']:30} | "
                            f"Total: {table['total_size']:15} | "
                            f"Table: {table['table_size']:15} | "
                            f"Indexes: {table['indexes_size']:15} | "
                            f"Rows: {table['row_count']:>10,}")
            else:
                report.append(f"  {table['table_name']:30} | Rows: {table['row_count']:>10,}")
        report.append("")
        
        # 2. 인덱스 현황
        report.append("🔍 인덱스 현황")
        report.append("-" * 80)
        indexes = self.analyze_indexes()
        for table, table_indexes in indexes.items():
            report.append(f"  테이블: {table}")
            if table_indexes:
                for idx in table_indexes:
                    columns = ', '.join(idx['column_names'])
                    unique = ' (UNIQUE)' if idx.get('unique') else ''
                    report.append(f"    - {idx['name']}: {columns}{unique}")
            else:
                report.append(f"    인덱스 없음")
        report.append("")
        
        # 3. 누락된 인덱스
        report.append("⚠️  인덱스 권장사항")
        report.append("-" * 80)
        missing = self.check_missing_indexes()
        if missing:
            for rec in missing:
                report.append(f"  [{rec['table']}.{rec['column']}]")
                report.append(f"    이유: {rec['reason']}")
                report.append(f"    권장: {rec['suggestion']}")
        else:
            report.append("  모든 필수 인덱스가 존재합니다.")
        report.append("")
        
        # 4. 커넥션 풀 상태
        report.append("🔌 커넥션 풀 상태")
        report.append("-" * 80)
        pool_stats = self.get_connection_pool_stats()
        report.append(f"  Pool Size: {pool_stats['pool_size']}")
        report.append(f"  Checked In: {pool_stats['checked_in']}")
        report.append(f"  Checked Out: {pool_stats['checked_out']}")
        report.append(f"  Overflow: {pool_stats['overflow']}")
        report.append(f"  Status: {pool_stats['status']}")
        report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """메인 실행 함수"""
    logger.add("logs/db_analysis.log", rotation="1 day")
    
    analyzer = DatabaseAnalyzer()
    
    # 분석 보고서 생성
    report = analyzer.generate_report()
    print(report)
    
    # 파일로 저장
    report_file = f"db_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    logger.success(f"✅ 보고서가 {report_file}에 저장되었습니다.")
    
    # VACUUM 실행 (선택사항)
    if input("\nVACUUM을 실행하시겠습니까? (y/n): ").lower() == 'y':
        analyzer.optimize_vacuum()


if __name__ == "__main__":
    main()
