"""
작업 관리 시스템 - 비동기 영상 생성
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobManager:
    def __init__(self, jobs_dir: Path):
        self.jobs_dir = jobs_dir
        self.jobs_dir.mkdir(exist_ok=True)

    def create_job(self, scenes_count: int, output_name: str) -> str:
        """새 작업 생성"""
        job_id = str(uuid.uuid4())

        job_data = {
            "job_id": job_id,
            "status": JobStatus.PENDING,
            "scenes_count": scenes_count,
            "output_name": output_name,
            "created_at": datetime.utcnow().isoformat(),
            "started_at": None,
            "completed_at": None,
            "current_stage": "대기 중...",
            "progress": 0,
            "error": None,
            "result": None
        }

        self._save_job(job_id, job_data)
        return job_id

    def update_job(self, job_id: str, **kwargs):
        """작업 상태 업데이트"""
        job = self.get_job(job_id)
        if job:
            job.update(kwargs)
            self._save_job(job_id, job)

    def get_job(self, job_id: str) -> Optional[Dict]:
        """작업 조회"""
        job_file = self.jobs_dir / f"{job_id}.json"
        if job_file.exists():
            return json.loads(job_file.read_text())
        return None

    def list_jobs(self, limit: int = 20) -> List[Dict]:
        """최근 작업 목록"""
        jobs = []
        for job_file in sorted(self.jobs_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            if len(jobs) >= limit:
                break
            jobs.append(json.loads(job_file.read_text()))
        return jobs

    def delete_job(self, job_id: str):
        """작업 삭제"""
        job_file = self.jobs_dir / f"{job_id}.json"
        if job_file.exists():
            job_file.unlink()

    def _save_job(self, job_id: str, job_data: Dict):
        """작업 저장"""
        job_file = self.jobs_dir / f"{job_id}.json"
        job_file.write_text(json.dumps(job_data, indent=2, ensure_ascii=False))
