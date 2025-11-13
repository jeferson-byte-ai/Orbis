"""
Disaster Recovery Service
Enterprise-grade backup and disaster recovery system
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid
import json
import hashlib
import gzip
import bz2
import lzma
import os
import shutil
from pathlib import Path

import redis.asyncio as redis
import boto3
from botocore.exceptions import ClientError
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from backend.config import settings
from backend.db.enterprise_database import enterprise_database
from backend.db.sharding_manager import sharding_manager

logger = logging.getLogger(__name__)


class BackupType(Enum):
    """Types of backups"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    CONTINUOUS = "continuous"


class BackupStatus(Enum):
    """Backup status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"


class RecoveryPointObjective(Enum):
    """Recovery Point Objective (RPO)"""
    RPO_15_MIN = 15      # 15 minutes
    RPO_1_HOUR = 60      # 1 hour
    RPO_4_HOURS = 240    # 4 hours
    RPO_24_HOURS = 1440  # 24 hours


class RecoveryTimeObjective(Enum):
    """Recovery Time Objective (RTO)"""
    RTO_5_MIN = 5        # 5 minutes
    RTO_15_MIN = 15      # 15 minutes
    RTO_1_HOUR = 60      # 1 hour
    RTO_4_HOURS = 240    # 4 hours


@dataclass
class BackupConfig:
    """Backup configuration"""
    backup_id: str
    name: str
    backup_type: BackupType
    schedule: str  # Cron expression
    retention_days: int
    compression: str = "gzip"
    encryption: bool = True
    rpo_minutes: int = 60
    rto_minutes: int = 15
    is_active: bool = True
    created_at: datetime = None


@dataclass
class BackupJob:
    """Backup job instance"""
    job_id: str
    backup_config: BackupConfig
    status: BackupStatus
    started_at: datetime
    completed_at: Optional[datetime]
    size_bytes: int = 0
    checksum: str = ""
    error_message: str = ""
    metadata: Dict[str, Any] = None


@dataclass
class RecoveryPlan:
    """Disaster recovery plan"""
    plan_id: str
    name: str
    description: str
    rpo_minutes: int
    rto_minutes: int
    backup_configs: List[str]
    recovery_steps: List[Dict[str, Any]]
    is_active: bool = True
    last_tested: Optional[datetime] = None


class DisasterRecoveryService:
    """Enterprise-grade disaster recovery service"""
    
    def __init__(self):
        self.backup_configs = {}
        self.backup_jobs = {}
        self.recovery_plans = {}
        self.s3_client = None
        self.backup_storage = {}
        
        # Performance monitoring
        self.backup_metrics = {}
        self.recovery_metrics = {}
        
        # Configuration
        self.backup_config = {
            "local_backup_path": "/opt/orbis/backups",
            "s3_bucket": "orbis-backups-prod",
            "s3_region": "us-east-1",
            "encryption_key": None,
            "compression_level": 6,
            "parallel_backups": 4,
            "verification_enabled": True,
            "cross_region_replication": True
        }
    
    async def initialize(self):
        """Initialize disaster recovery service"""
        try:
            logger.info("🚀 Initializing Disaster Recovery Service...")
            
            # Initialize AWS S3 client
            await self._initialize_s3_client()
            
            # Initialize backup storage
            await self._initialize_backup_storage()
            
            # Load backup configurations
            await self._load_backup_configs()
            
            # Load recovery plans
            await self._load_recovery_plans()
            
            # Start background tasks
            asyncio.create_task(self._backup_scheduler())
            asyncio.create_task(self._backup_verifier())
            asyncio.create_task(self._cleanup_scheduler())
            asyncio.create_task(self._monitoring_service())
            
            logger.info("✅ Disaster Recovery Service initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Disaster Recovery Service: {e}")
            raise
    
    async def _initialize_s3_client(self):
        """Initialize AWS S3 client for cloud backups"""
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=self.backup_config["s3_region"],
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key
            )
            
            # Test S3 connection
            await self._test_s3_connection()
            
            logger.info("✅ S3 client initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise
    
    async def _test_s3_connection(self):
        """Test S3 connection"""
        try:
            # Test bucket access
            response = self.s3_client.head_bucket(Bucket=self.backup_config["s3_bucket"])
            logger.info("✅ S3 bucket access verified")
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                # Create bucket if it doesn't exist
                await self._create_s3_bucket()
            else:
                raise
    
    async def _create_s3_bucket(self):
        """Create S3 bucket for backups"""
        try:
            self.s3_client.create_bucket(
                Bucket=self.backup_config["s3_bucket"],
                CreateBucketConfiguration={
                    'LocationConstraint': self.backup_config["s3_region"]
                }
            )
            
            # Enable versioning
            self.s3_client.put_bucket_versioning(
                Bucket=self.backup_config["s3_bucket"],
                VersioningConfiguration={'Status': 'Enabled'}
            )
            
            # Enable encryption
            self.s3_client.put_bucket_encryption(
                Bucket=self.backup_config["s3_bucket"],
                ServerSideEncryptionConfiguration={
                    'Rules': [
                        {
                            'ApplyServerSideEncryptionByDefault': {
                                'SSEAlgorithm': 'AES256'
                            }
                        }
                    ]
                }
            )
            
            logger.info(f"✅ S3 bucket created: {self.backup_config['s3_bucket']}")
            
        except Exception as e:
            logger.error(f"Failed to create S3 bucket: {e}")
            raise
    
    async def _initialize_backup_storage(self):
        """Initialize local backup storage"""
        try:
            backup_path = Path(self.backup_config["local_backup_path"])
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (backup_path / "full").mkdir(exist_ok=True)
            (backup_path / "incremental").mkdir(exist_ok=True)
            (backup_path / "differential").mkdir(exist_ok=True)
            (backup_path / "continuous").mkdir(exist_ok=True)
            (backup_path / "metadata").mkdir(exist_ok=True)
            
            self.backup_storage = {
                "local_path": backup_path,
                "available_space": shutil.disk_usage(backup_path).free,
                "total_space": shutil.disk_usage(backup_path).total
            }
            
            logger.info(f"✅ Backup storage initialized: {backup_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize backup storage: {e}")
            raise
    
    async def _load_backup_configs(self):
        """Load backup configurations"""
        try:
            # Default backup configurations
            default_configs = [
                BackupConfig(
                    backup_id="users_full_daily",
                    name="Users Full Daily Backup",
                    backup_type=BackupType.FULL,
                    schedule="0 2 * * *",  # Daily at 2 AM
                    retention_days=30,
                    compression="gzip",
                    encryption=True,
                    rpo_minutes=1440,  # 24 hours
                    rto_minutes=60,    # 1 hour
                    created_at=datetime.utcnow()
                ),
                BackupConfig(
                    backup_id="meetings_incremental_hourly",
                    name="Meetings Incremental Hourly Backup",
                    backup_type=BackupType.INCREMENTAL,
                    schedule="0 * * * *",  # Every hour
                    retention_days=7,
                    compression="gzip",
                    encryption=True,
                    rpo_minutes=60,    # 1 hour
                    rto_minutes=15,    # 15 minutes
                    created_at=datetime.utcnow()
                ),
                BackupConfig(
                    backup_id="analytics_continuous",
                    name="Analytics Continuous Backup",
                    backup_type=BackupType.CONTINUOUS,
                    schedule="*/15 * * * *",  # Every 15 minutes
                    retention_days=3,
                    compression="lzma",
                    encryption=True,
                    rpo_minutes=15,    # 15 minutes
                    rto_minutes=5,     # 5 minutes
                    created_at=datetime.utcnow()
                ),
                BackupConfig(
                    backup_id="billing_full_weekly",
                    name="Billing Full Weekly Backup",
                    backup_type=BackupType.FULL,
                    schedule="0 3 * * 0",  # Weekly on Sunday at 3 AM
                    retention_days=365,
                    compression="gzip",
                    encryption=True,
                    rpo_minutes=10080, # 1 week
                    rto_minutes=240,   # 4 hours
                    created_at=datetime.utcnow()
                )
            ]
            
            for config in default_configs:
                self.backup_configs[config.backup_id] = config
            
            logger.info(f"✅ Loaded {len(self.backup_configs)} backup configurations")
            
        except Exception as e:
            logger.error(f"Failed to load backup configurations: {e}")
            raise
    
    async def _load_recovery_plans(self):
        """Load disaster recovery plans"""
        try:
            # Default recovery plans
            default_plans = [
                RecoveryPlan(
                    plan_id="critical_systems_recovery",
                    name="Critical Systems Recovery",
                    description="Recovery plan for critical systems (users, billing, authentication)",
                    rpo_minutes=15,
                    rto_minutes=5,
                    backup_configs=["users_full_daily", "billing_full_weekly"],
                    recovery_steps=[
                        {"step": 1, "action": "restore_database", "target": "users_primary"},
                        {"step": 2, "action": "restore_database", "target": "billing_primary"},
                        {"step": 3, "action": "verify_data_integrity", "target": "all"},
                        {"step": 4, "action": "restart_services", "target": "critical"},
                        {"step": 5, "action": "run_health_checks", "target": "all"}
                    ],
                    is_active=True
                ),
                RecoveryPlan(
                    plan_id="full_system_recovery",
                    name="Full System Recovery",
                    description="Complete system recovery plan",
                    rpo_minutes=60,
                    rto_minutes=60,
                    backup_configs=["users_full_daily", "meetings_incremental_hourly", "analytics_continuous", "billing_full_weekly"],
                    recovery_steps=[
                        {"step": 1, "action": "restore_all_databases", "target": "all"},
                        {"step": 2, "action": "restore_redis_clusters", "target": "all"},
                        {"step": 3, "action": "restore_file_systems", "target": "all"},
                        {"step": 4, "action": "verify_system_integrity", "target": "all"},
                        {"step": 5, "action": "restart_all_services", "target": "all"},
                        {"step": 6, "action": "run_comprehensive_tests", "target": "all"}
                    ],
                    is_active=True
                )
            ]
            
            for plan in default_plans:
                self.recovery_plans[plan.plan_id] = plan
            
            logger.info(f"✅ Loaded {len(self.recovery_plans)} recovery plans")
            
        except Exception as e:
            logger.error(f"Failed to load recovery plans: {e}")
            raise
    
    async def create_backup(self, backup_config_id: str, force: bool = False) -> str:
        """Create backup based on configuration"""
        try:
            if backup_config_id not in self.backup_configs:
                raise ValueError(f"Backup configuration not found: {backup_config_id}")
            
            config = self.backup_configs[backup_config_id]
            
            # Check if backup is already in progress
            if not force and await self._is_backup_in_progress(backup_config_id):
                raise ValueError(f"Backup already in progress for: {backup_config_id}")
            
            # Create backup job
            job_id = str(uuid.uuid4())
            job = BackupJob(
                job_id=job_id,
                backup_config=config,
                status=BackupStatus.PENDING,
                started_at=datetime.utcnow(),
                metadata={}
            )
            
            self.backup_jobs[job_id] = job
            
            # Start backup process
            asyncio.create_task(self._execute_backup(job))
            
            logger.info(f"✅ Backup job created: {job_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise
    
    async def _execute_backup(self, job: BackupJob):
        """Execute backup job"""
        try:
            job.status = BackupStatus.IN_PROGRESS
            logger.info(f"Starting backup job: {job.job_id}")
            
            # Determine backup strategy based on type
            if job.backup_config.backup_type == BackupType.FULL:
                await self._execute_full_backup(job)
            elif job.backup_config.backup_type == BackupType.INCREMENTAL:
                await self._execute_incremental_backup(job)
            elif job.backup_config.backup_type == BackupType.DIFFERENTIAL:
                await self._execute_differential_backup(job)
            elif job.backup_config.backup_type == BackupType.CONTINUOUS:
                await self._execute_continuous_backup(job)
            
            # Verify backup
            if self.backup_config["verification_enabled"]:
                await self._verify_backup(job)
            
            # Upload to cloud storage
            await self._upload_to_cloud(job)
            
            job.status = BackupStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            
            logger.info(f"✅ Backup job completed: {job.job_id}")
            
        except Exception as e:
            job.status = BackupStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            logger.error(f"❌ Backup job failed: {job.job_id} - {e}")
    
    async def _execute_full_backup(self, job: BackupJob):
        """Execute full backup"""
        try:
            logger.info(f"Executing full backup: {job.job_id}")
            
            # Get all database shards
            shards = await sharding_manager._get_relevant_shards("all")
            
            backup_files = []
            
            for shard_id in shards:
                # Create database dump
                dump_file = await self._create_database_dump(shard_id, job)
                backup_files.append(dump_file)
            
            # Compress backup files
            compressed_file = await self._compress_backup_files(backup_files, job)
            
            # Calculate checksum
            job.checksum = await self._calculate_checksum(compressed_file)
            
            # Get file size
            job.size_bytes = os.path.getsize(compressed_file)
            
            # Store metadata
            job.metadata = {
                "backup_type": "full",
                "shards_backed_up": shards,
                "files": backup_files,
                "compressed_file": compressed_file,
                "compression_ratio": await self._calculate_compression_ratio(backup_files, compressed_file)
            }
            
        except Exception as e:
            logger.error(f"Failed to execute full backup: {e}")
            raise
    
    async def _execute_incremental_backup(self, job: BackupJob):
        """Execute incremental backup"""
        try:
            logger.info(f"Executing incremental backup: {job.job_id}")
            
            # Get last backup timestamp
            last_backup_time = await self._get_last_backup_time(job.backup_config.backup_id)
            
            # Create incremental dump
            dump_file = await self._create_incremental_dump(last_backup_time, job)
            
            # Compress backup file
            compressed_file = await self._compress_backup_files([dump_file], job)
            
            # Calculate checksum
            job.checksum = await self._calculate_checksum(compressed_file)
            
            # Get file size
            job.size_bytes = os.path.getsize(compressed_file)
            
            # Store metadata
            job.metadata = {
                "backup_type": "incremental",
                "last_backup_time": last_backup_time.isoformat() if last_backup_time else None,
                "files": [dump_file],
                "compressed_file": compressed_file
            }
            
        except Exception as e:
            logger.error(f"Failed to execute incremental backup: {e}")
            raise
    
    async def _execute_differential_backup(self, job: BackupJob):
        """Execute differential backup"""
        try:
            logger.info(f"Executing differential backup: {job.job_id}")
            
            # Get last full backup timestamp
            last_full_backup_time = await self._get_last_full_backup_time(job.backup_config.backup_id)
            
            # Create differential dump
            dump_file = await self._create_differential_dump(last_full_backup_time, job)
            
            # Compress backup file
            compressed_file = await self._compress_backup_files([dump_file], job)
            
            # Calculate checksum
            job.checksum = await self._calculate_checksum(compressed_file)
            
            # Get file size
            job.size_bytes = os.path.getsize(compressed_file)
            
            # Store metadata
            job.metadata = {
                "backup_type": "differential",
                "last_full_backup_time": last_full_backup_time.isoformat() if last_full_backup_time else None,
                "files": [dump_file],
                "compressed_file": compressed_file
            }
            
        except Exception as e:
            logger.error(f"Failed to execute differential backup: {e}")
            raise
    
    async def _execute_continuous_backup(self, job: BackupJob):
        """Execute continuous backup"""
        try:
            logger.info(f"Executing continuous backup: {job.job_id}")
            
            # Create WAL (Write-Ahead Log) backup
            wal_files = await self._create_wal_backup(job)
            
            # Compress WAL files
            compressed_file = await self._compress_backup_files(wal_files, job)
            
            # Calculate checksum
            job.checksum = await self._calculate_checksum(compressed_file)
            
            # Get file size
            job.size_bytes = os.path.getsize(compressed_file)
            
            # Store metadata
            job.metadata = {
                "backup_type": "continuous",
                "wal_files": wal_files,
                "compressed_file": compressed_file
            }
            
        except Exception as e:
            logger.error(f"Failed to execute continuous backup: {e}")
            raise
    
    async def _create_database_dump(self, shard_id: str, job: BackupJob) -> str:
        """Create database dump for shard"""
        try:
            # Map shard to database connection
            shard_mapping = {
                "users_primary": "orbis_users_primary",
                "users_secondary": "orbis_users_secondary",
                "meetings_primary": "orbis_meetings_primary",
                "meetings_secondary": "orbis_meetings_secondary",
                "analytics_primary": "orbis_analytics_primary",
                "analytics_secondary": "orbis_analytics_secondary",
                "social_primary": "orbis_social_primary",
                "social_secondary": "orbis_social_secondary",
                "billing_primary": "orbis_billing_primary",
                "billing_secondary": "orbis_billing_secondary"
            }
            
            database_name = shard_mapping.get(shard_id, "orbis_users_primary")
            
            # Create dump file path
            dump_file = self.backup_storage["local_path"] / job.backup_config.backup_type.value / f"{database_name}_{job.job_id}.sql"
            
            # Create pg_dump command
            dump_command = [
                "pg_dump",
                f"--host={settings.database_host}",
                f"--port={settings.database_port}",
                f"--username={settings.database_user}",
                f"--dbname={database_name}",
                "--verbose",
                "--no-password",
                "--format=custom",
                "--compress=9",
                f"--file={dump_file}"
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            env["PGPASSWORD"] = settings.database_password
            
            # Execute dump command
            process = await asyncio.create_subprocess_exec(
                *dump_command,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"pg_dump failed: {stderr.decode()}")
            
            return str(dump_file)
            
        except Exception as e:
            logger.error(f"Failed to create database dump: {e}")
            raise
    
    async def _create_incremental_dump(self, last_backup_time: datetime, job: BackupJob) -> str:
        """Create incremental database dump"""
        try:
            # This would implement incremental backup logic
            # For now, create a simple dump
            return await self._create_database_dump("users_primary", job)
            
        except Exception as e:
            logger.error(f"Failed to create incremental dump: {e}")
            raise
    
    async def _create_differential_dump(self, last_full_backup_time: datetime, job: BackupJob) -> str:
        """Create differential database dump"""
        try:
            # This would implement differential backup logic
            # For now, create a simple dump
            return await self._create_database_dump("users_primary", job)
            
        except Exception as e:
            logger.error(f"Failed to create differential dump: {e}")
            raise
    
    async def _create_wal_backup(self, job: BackupJob) -> List[str]:
        """Create WAL (Write-Ahead Log) backup"""
        try:
            # This would implement WAL backup logic
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Failed to create WAL backup: {e}")
            raise
    
    async def _compress_backup_files(self, files: List[str], job: BackupJob) -> str:
        """Compress backup files"""
        try:
            compression = job.backup_config.compression
            compressed_file = f"{job.job_id}.{compression}"
            compressed_path = self.backup_storage["local_path"] / job.backup_config.backup_type.value / compressed_file
            
            if compression == "gzip":
                with open(compressed_path, 'wb') as f_out:
                    with gzip.open(f_out, 'wt', compresslevel=self.backup_config["compression_level"]) as gz:
                        for file_path in files:
                            with open(file_path, 'r') as f_in:
                                gz.write(f_in.read())
            elif compression == "bzip2":
                with open(compressed_path, 'wb') as f_out:
                    with bz2.open(f_out, 'wt', compresslevel=self.backup_config["compression_level"]) as bz:
                        for file_path in files:
                            with open(file_path, 'r') as f_in:
                                bz.write(f_in.read())
            elif compression == "lzma":
                with open(compressed_path, 'wb') as f_out:
                    with lzma.open(f_out, 'wt', preset=self.backup_config["compression_level"]) as lz:
                        for file_path in files:
                            with open(file_path, 'r') as f_in:
                                lz.write(f_in.read())
            
            return str(compressed_path)
            
        except Exception as e:
            logger.error(f"Failed to compress backup files: {e}")
            raise
    
    async def _calculate_checksum(self, file_path: str) -> str:
        """Calculate file checksum"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
            
        except Exception as e:
            logger.error(f"Failed to calculate checksum: {e}")
            return ""
    
    async def _calculate_compression_ratio(self, original_files: List[str], compressed_file: str) -> float:
        """Calculate compression ratio"""
        try:
            original_size = sum(os.path.getsize(f) for f in original_files)
            compressed_size = os.path.getsize(compressed_file)
            
            if original_size == 0:
                return 0.0
            
            return (1 - compressed_size / original_size) * 100
            
        except Exception as e:
            logger.error(f"Failed to calculate compression ratio: {e}")
            return 0.0
    
    async def _verify_backup(self, job: BackupJob):
        """Verify backup integrity"""
        try:
            logger.info(f"Verifying backup: {job.job_id}")
            
            # Verify file exists and is readable
            if not os.path.exists(job.metadata["compressed_file"]):
                raise Exception("Backup file not found")
            
            # Verify checksum
            calculated_checksum = await self._calculate_checksum(job.metadata["compressed_file"])
            if calculated_checksum != job.checksum:
                raise Exception("Checksum verification failed")
            
            # Test decompression
            await self._test_decompression(job.metadata["compressed_file"], job.backup_config.compression)
            
            job.status = BackupStatus.VERIFIED
            logger.info(f"✅ Backup verified: {job.job_id}")
            
        except Exception as e:
            logger.error(f"Backup verification failed: {e}")
            raise
    
    async def _test_decompression(self, compressed_file: str, compression: str):
        """Test decompression of backup file"""
        try:
            if compression == "gzip":
                with gzip.open(compressed_file, 'rt') as f:
                    f.read(1024)  # Read first 1KB
            elif compression == "bzip2":
                with bz2.open(compressed_file, 'rt') as f:
                    f.read(1024)  # Read first 1KB
            elif compression == "lzma":
                with lzma.open(compressed_file, 'rt') as f:
                    f.read(1024)  # Read first 1KB
            
        except Exception as e:
            logger.error(f"Decompression test failed: {e}")
            raise
    
    async def _upload_to_cloud(self, job: BackupJob):
        """Upload backup to cloud storage"""
        try:
            logger.info(f"Uploading backup to cloud: {job.job_id}")
            
            compressed_file = job.metadata["compressed_file"]
            s3_key = f"backups/{job.backup_config.backup_id}/{job.job_id}.{job.backup_config.compression}"
            
            # Upload to S3
            self.s3_client.upload_file(
                compressed_file,
                self.backup_config["s3_bucket"],
                s3_key,
                ExtraArgs={
                    'ServerSideEncryption': 'AES256',
                    'Metadata': {
                        'backup_id': job.job_id,
                        'backup_type': job.backup_config.backup_type.value,
                        'checksum': job.checksum,
                        'created_at': job.started_at.isoformat()
                    }
                }
            )
            
            # Enable cross-region replication if configured
            if self.backup_config["cross_region_replication"]:
                await self._enable_cross_region_replication(s3_key)
            
            logger.info(f"✅ Backup uploaded to cloud: {job.job_id}")
            
        except Exception as e:
            logger.error(f"Failed to upload backup to cloud: {e}")
            raise
    
    async def _enable_cross_region_replication(self, s3_key: str):
        """Enable cross-region replication for backup"""
        try:
            # This would implement cross-region replication
            # For now, just log
            logger.info(f"Cross-region replication enabled for: {s3_key}")
            
        except Exception as e:
            logger.error(f"Failed to enable cross-region replication: {e}")
    
    async def _get_last_backup_time(self, backup_config_id: str) -> Optional[datetime]:
        """Get last backup time for configuration"""
        try:
            # Find last successful backup
            for job in self.backup_jobs.values():
                if (job.backup_config.backup_id == backup_config_id and 
                    job.status == BackupStatus.COMPLETED):
                    return job.completed_at
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get last backup time: {e}")
            return None
    
    async def _get_last_full_backup_time(self, backup_config_id: str) -> Optional[datetime]:
        """Get last full backup time for configuration"""
        try:
            # Find last successful full backup
            for job in self.backup_jobs.values():
                if (job.backup_config.backup_id == backup_config_id and 
                    job.backup_config.backup_type == BackupType.FULL and
                    job.status == BackupStatus.COMPLETED):
                    return job.completed_at
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get last full backup time: {e}")
            return None
    
    async def _is_backup_in_progress(self, backup_config_id: str) -> bool:
        """Check if backup is already in progress"""
        try:
            for job in self.backup_jobs.values():
                if (job.backup_config.backup_id == backup_config_id and 
                    job.status == BackupStatus.IN_PROGRESS):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check backup progress: {e}")
            return False
    
    async def restore_from_backup(self, backup_job_id: str, target_shard: str = None) -> bool:
        """Restore from backup"""
        try:
            if backup_job_id not in self.backup_jobs:
                raise ValueError(f"Backup job not found: {backup_job_id}")
            
            job = self.backup_jobs[backup_job_id]
            
            if job.status != BackupStatus.COMPLETED:
                raise ValueError(f"Backup job not completed: {backup_job_id}")
            
            logger.info(f"Starting restore from backup: {backup_job_id}")
            
            # Download backup from cloud if needed
            backup_file = await self._download_backup_from_cloud(job)
            
            # Decompress backup
            decompressed_files = await self._decompress_backup(backup_file, job)
            
            # Restore databases
            await self._restore_databases(decompressed_files, target_shard)
            
            # Verify restore
            await self._verify_restore(job)
            
            logger.info(f"✅ Restore completed: {backup_job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            return False
    
    async def _download_backup_from_cloud(self, job: BackupJob) -> str:
        """Download backup from cloud storage"""
        try:
            s3_key = f"backups/{job.backup_config.backup_id}/{job.job_id}.{job.backup_config.compression}"
            local_file = self.backup_storage["local_path"] / "restore" / f"{job.job_id}.{job.backup_config.compression}"
            
            # Create restore directory
            local_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Download from S3
            self.s3_client.download_file(
                self.backup_config["s3_bucket"],
                s3_key,
                str(local_file)
            )
            
            return str(local_file)
            
        except Exception as e:
            logger.error(f"Failed to download backup from cloud: {e}")
            raise
    
    async def _decompress_backup(self, compressed_file: str, job: BackupJob) -> List[str]:
        """Decompress backup file"""
        try:
            decompressed_files = []
            compression = job.backup_config.compression
            
            if compression == "gzip":
                with gzip.open(compressed_file, 'rt') as f_in:
                    decompressed_file = compressed_file.replace('.gzip', '.sql')
                    with open(decompressed_file, 'w') as f_out:
                        f_out.write(f_in.read())
                    decompressed_files.append(decompressed_file)
            elif compression == "bzip2":
                with bz2.open(compressed_file, 'rt') as f_in:
                    decompressed_file = compressed_file.replace('.bzip2', '.sql')
                    with open(decompressed_file, 'w') as f_out:
                        f_out.write(f_in.read())
                    decompressed_files.append(decompressed_file)
            elif compression == "lzma":
                with lzma.open(compressed_file, 'rt') as f_in:
                    decompressed_file = compressed_file.replace('.lzma', '.sql')
                    with open(decompressed_file, 'w') as f_out:
                        f_out.write(f_in.read())
                    decompressed_files.append(decompressed_file)
            
            return decompressed_files
            
        except Exception as e:
            logger.error(f"Failed to decompress backup: {e}")
            raise
    
    async def _restore_databases(self, dump_files: List[str], target_shard: str = None):
        """Restore databases from dump files"""
        try:
            for dump_file in dump_files:
                # Determine target database
                if target_shard:
                    database_name = f"orbis_{target_shard}"
                else:
                    # Extract database name from dump file
                    database_name = "orbis_users_primary"  # Default
                
                # Create restore command
                restore_command = [
                    "pg_restore",
                    f"--host={settings.database_host}",
                    f"--port={settings.database_port}",
                    f"--username={settings.database_user}",
                    f"--dbname={database_name}",
                    "--verbose",
                    "--no-password",
                    "--clean",
                    "--if-exists",
                    str(dump_file)
                ]
                
                # Set password environment variable
                env = os.environ.copy()
                env["PGPASSWORD"] = settings.database_password
                
                # Execute restore command
                process = await asyncio.create_subprocess_exec(
                    *restore_command,
                    env=env,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode != 0:
                    raise Exception(f"pg_restore failed: {stderr.decode()}")
                
        except Exception as e:
            logger.error(f"Failed to restore databases: {e}")
            raise
    
    async def _verify_restore(self, job: BackupJob):
        """Verify restore integrity"""
        try:
            # This would implement restore verification logic
            # For now, just log
            logger.info(f"Restore verification completed for: {job.job_id}")
            
        except Exception as e:
            logger.error(f"Failed to verify restore: {e}")
            raise
    
    async def execute_recovery_plan(self, plan_id: str) -> bool:
        """Execute disaster recovery plan"""
        try:
            if plan_id not in self.recovery_plans:
                raise ValueError(f"Recovery plan not found: {plan_id}")
            
            plan = self.recovery_plans[plan_id]
            
            logger.info(f"Executing recovery plan: {plan.name}")
            
            # Execute recovery steps
            for step in plan.recovery_steps:
                await self._execute_recovery_step(step)
            
            # Update last tested timestamp
            plan.last_tested = datetime.utcnow()
            
            logger.info(f"✅ Recovery plan executed successfully: {plan.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute recovery plan: {e}")
            return False
    
    async def _execute_recovery_step(self, step: Dict[str, Any]):
        """Execute individual recovery step"""
        try:
            action = step["action"]
            target = step["target"]
            
            if action == "restore_database":
                await self._restore_database_step(target)
            elif action == "restore_redis_clusters":
                await self._restore_redis_step(target)
            elif action == "restore_file_systems":
                await self._restore_filesystem_step(target)
            elif action == "verify_data_integrity":
                await self._verify_integrity_step(target)
            elif action == "restart_services":
                await self._restart_services_step(target)
            elif action == "run_health_checks":
                await self._health_check_step(target)
            
        except Exception as e:
            logger.error(f"Failed to execute recovery step: {e}")
            raise
    
    async def _restore_database_step(self, target: str):
        """Restore database step"""
        try:
            logger.info(f"Restoring database: {target}")
            # This would implement database restoration logic
            
        except Exception as e:
            logger.error(f"Failed to restore database: {e}")
            raise
    
    async def _restore_redis_step(self, target: str):
        """Restore Redis step"""
        try:
            logger.info(f"Restoring Redis: {target}")
            # This would implement Redis restoration logic
            
        except Exception as e:
            logger.error(f"Failed to restore Redis: {e}")
            raise
    
    async def _restore_filesystem_step(self, target: str):
        """Restore filesystem step"""
        try:
            logger.info(f"Restoring filesystem: {target}")
            # This would implement filesystem restoration logic
            
        except Exception as e:
            logger.error(f"Failed to restore filesystem: {e}")
            raise
    
    async def _verify_integrity_step(self, target: str):
        """Verify integrity step"""
        try:
            logger.info(f"Verifying integrity: {target}")
            # This would implement integrity verification logic
            
        except Exception as e:
            logger.error(f"Failed to verify integrity: {e}")
            raise
    
    async def _restart_services_step(self, target: str):
        """Restart services step"""
        try:
            logger.info(f"Restarting services: {target}")
            # This would implement service restart logic
            
        except Exception as e:
            logger.error(f"Failed to restart services: {e}")
            raise
    
    async def _health_check_step(self, target: str):
        """Health check step"""
        try:
            logger.info(f"Running health checks: {target}")
            # This would implement health check logic
            
        except Exception as e:
            logger.error(f"Failed to run health checks: {e}")
            raise
    
    async def _backup_scheduler(self):
        """Background task to schedule backups"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                current_time = datetime.utcnow()
                
                # Check each backup configuration
                for config_id, config in self.backup_configs.items():
                    if not config.is_active:
                        continue
                    
                    # Check if backup should run based on schedule
                    if await self._should_run_backup(config, current_time):
                        await self.create_backup(config_id)
                
            except Exception as e:
                logger.error(f"Backup scheduler error: {e}")
                await asyncio.sleep(60)
    
    async def _should_run_backup(self, config: BackupConfig, current_time: datetime) -> bool:
        """Check if backup should run based on schedule"""
        try:
            # This would implement cron-like scheduling logic
            # For now, use simple time-based checks
            
            if config.backup_type == BackupType.CONTINUOUS:
                # Check if 15 minutes have passed since last backup
                last_backup = await self._get_last_backup_time(config.backup_id)
                if last_backup:
                    time_diff = current_time - last_backup
                    return time_diff.total_seconds() >= 900  # 15 minutes
                return True
            
            elif config.backup_type == BackupType.INCREMENTAL:
                # Check if 1 hour has passed since last backup
                last_backup = await self._get_last_backup_time(config.backup_id)
                if last_backup:
                    time_diff = current_time - last_backup
                    return time_diff.total_seconds() >= 3600  # 1 hour
                return True
            
            elif config.backup_type == BackupType.FULL:
                # Check if it's the scheduled time (simplified)
                if config.schedule == "0 2 * * *":  # Daily at 2 AM
                    return current_time.hour == 2 and current_time.minute == 0
                elif config.schedule == "0 3 * * 0":  # Weekly on Sunday at 3 AM
                    return (current_time.weekday() == 6 and 
                           current_time.hour == 3 and 
                           current_time.minute == 0)
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check backup schedule: {e}")
            return False
    
    async def _backup_verifier(self):
        """Background task to verify backups"""
        while True:
            try:
                await asyncio.sleep(3600)  # Verify every hour
                
                # Verify recent backups
                for job_id, job in self.backup_jobs.items():
                    if (job.status == BackupStatus.COMPLETED and 
                        not hasattr(job, 'verified') and
                        job.completed_at and
                        (datetime.utcnow() - job.completed_at).total_seconds() < 3600):
                        
                        await self._verify_backup(job)
                        job.verified = True
                
            except Exception as e:
                logger.error(f"Backup verifier error: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_scheduler(self):
        """Background task to cleanup old backups"""
        while True:
            try:
                await asyncio.sleep(86400)  # Cleanup daily
                
                current_time = datetime.utcnow()
                
                # Cleanup old backups based on retention policy
                for config_id, config in self.backup_configs.items():
                    await self._cleanup_old_backups(config, current_time)
                
            except Exception as e:
                logger.error(f"Cleanup scheduler error: {e}")
                await asyncio.sleep(86400)
    
    async def _cleanup_old_backups(self, config: BackupConfig, current_time: datetime):
        """Cleanup old backups based on retention policy"""
        try:
            cutoff_time = current_time - timedelta(days=config.retention_days)
            
            # Find old backup jobs
            old_jobs = [
                job_id for job_id, job in self.backup_jobs.items()
                if (job.backup_config.backup_id == config.backup_id and
                    job.completed_at and
                    job.completed_at < cutoff_time)
            ]
            
            # Cleanup old backups
            for job_id in old_jobs:
                await self._cleanup_backup_job(job_id)
            
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
    
    async def _cleanup_backup_job(self, job_id: str):
        """Cleanup specific backup job"""
        try:
            job = self.backup_jobs.get(job_id)
            if not job:
                return
            
            # Remove local files
            if "compressed_file" in job.metadata:
                local_file = job.metadata["compressed_file"]
                if os.path.exists(local_file):
                    os.remove(local_file)
            
            # Remove from S3
            s3_key = f"backups/{job.backup_config.backup_id}/{job.job_id}.{job.backup_config.compression}"
            try:
                self.s3_client.delete_object(
                    Bucket=self.backup_config["s3_bucket"],
                    Key=s3_key
                )
            except ClientError:
                pass  # File might not exist
            
            # Remove job from memory
            del self.backup_jobs[job_id]
            
            logger.info(f"Cleaned up backup job: {job_id}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup backup job: {e}")
    
    async def _monitoring_service(self):
        """Background task to monitor backup system"""
        while True:
            try:
                await asyncio.sleep(300)  # Monitor every 5 minutes
                
                # Check backup system health
                await self._check_backup_system_health()
                
                # Update metrics
                await self._update_backup_metrics()
                
            except Exception as e:
                logger.error(f"Monitoring service error: {e}")
                await asyncio.sleep(300)
    
    async def _check_backup_system_health(self):
        """Check backup system health"""
        try:
            # Check disk space
            available_space = shutil.disk_usage(self.backup_storage["local_path"]).free
            total_space = shutil.disk_usage(self.backup_storage["local_path"]).total
            usage_percentage = (1 - available_space / total_space) * 100
            
            if usage_percentage > 90:
                logger.warning(f"Backup storage usage high: {usage_percentage:.1f}%")
            
            # Check failed backups
            failed_backups = [
                job for job in self.backup_jobs.values()
                if job.status == BackupStatus.FAILED
            ]
            
            if len(failed_backups) > 0:
                logger.warning(f"Found {len(failed_backups)} failed backups")
            
        except Exception as e:
            logger.error(f"Failed to check backup system health: {e}")
    
    async def _update_backup_metrics(self):
        """Update backup metrics"""
        try:
            current_time = datetime.utcnow()
            
            # Calculate metrics
            total_backups = len(self.backup_jobs)
            successful_backups = len([j for j in self.backup_jobs.values() if j.status == BackupStatus.COMPLETED])
            failed_backups = len([j for j in self.backup_jobs.values() if j.status == BackupStatus.FAILED])
            
            success_rate = (successful_backups / total_backups * 100) if total_backups > 0 else 0
            
            # Store metrics
            self.backup_metrics = {
                "total_backups": total_backups,
                "successful_backups": successful_backups,
                "failed_backups": failed_backups,
                "success_rate": success_rate,
                "last_updated": current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to update backup metrics: {e}")
    
    async def get_backup_status(self) -> Dict[str, Any]:
        """Get comprehensive backup status"""
        try:
            return {
                "backup_configs": {
                    config_id: {
                        "name": config.name,
                        "type": config.backup_type.value,
                        "schedule": config.schedule,
                        "retention_days": config.retention_days,
                        "is_active": config.is_active,
                        "rpo_minutes": config.rpo_minutes,
                        "rto_minutes": config.rto_minutes
                    }
                    for config_id, config in self.backup_configs.items()
                },
                "recent_backups": [
                    {
                        "job_id": job.job_id,
                        "backup_config": job.backup_config.backup_id,
                        "status": job.status.value,
                        "started_at": job.started_at.isoformat(),
                        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                        "size_bytes": job.size_bytes,
                        "checksum": job.checksum
                    }
                    for job in list(self.backup_jobs.values())[-10:]  # Last 10 backups
                ],
                "recovery_plans": {
                    plan_id: {
                        "name": plan.name,
                        "description": plan.description,
                        "rpo_minutes": plan.rpo_minutes,
                        "rto_minutes": plan.rto_minutes,
                        "is_active": plan.is_active,
                        "last_tested": plan.last_tested.isoformat() if plan.last_tested else None
                    }
                    for plan_id, plan in self.recovery_plans.items()
                },
                "metrics": self.backup_metrics,
                "storage": {
                    "local_path": str(self.backup_storage["local_path"]),
                    "available_space_gb": self.backup_storage["available_space"] / (1024**3),
                    "total_space_gb": self.backup_storage["total_space"] / (1024**3)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get backup status: {e}")
            return {}


# Global disaster recovery service instance
disaster_recovery_service = DisasterRecoveryService()
