"""
Automated Backup Service
Implements scheduled database and file backups with retention policies
"""
import os
import shutil
import gzip
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
import subprocess
import logging
from backend.config import settings
from backend.db.session import engine

logger = logging.getLogger(__name__)


class BackupService:
    """Enterprise backup service with rotation"""
    
    def __init__(
        self,
        backup_dir: str = "./backups",
        retention_days: int = 30,
        max_backups: int = 100
    ):
        self.backup_dir = Path(backup_dir)
        self.retention_days = retention_days
        self.max_backups = max_backups
        
        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ Backup service initialized: {self.backup_dir}")
    
    async def create_full_backup(self) -> dict:
        """
        Create full system backup (database + files)
        Returns backup metadata
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_name = f"orbis_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🔄 Starting full backup: {backup_name}")
        
        try:
            # 1. Backup database
            db_backup_path = await self._backup_database(backup_path)
            
            # 2. Backup files (voices, uploads, etc)
            files_backup_path = await self._backup_files(backup_path)
            
            # 3. Create metadata
            metadata = {
                "backup_name": backup_name,
                "timestamp": timestamp,
                "database": str(db_backup_path.relative_to(backup_path)),
                "files": str(files_backup_path.relative_to(backup_path)),
                "size_mb": self._get_directory_size(backup_path) / (1024 * 1024),
                "retention_until": (
                    datetime.utcnow() + timedelta(days=self.retention_days)
                ).isoformat()
            }
            
            # Save metadata
            metadata_path = backup_path / "metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # 4. Compress backup
            compressed_path = await self._compress_backup(backup_path)
            
            # 5. Cleanup old backups
            await self._cleanup_old_backups()
            
            logger.info(f"✅ Backup completed: {compressed_path}")
            
            return {
                "status": "success",
                "backup_path": str(compressed_path),
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}", exc_info=True)
            # Cleanup failed backup
            if backup_path.exists():
                shutil.rmtree(backup_path)
            
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _backup_database(self, backup_path: Path) -> Path:
        """Backup database"""
        db_backup_path = backup_path / "database"
        db_backup_path.mkdir(parents=True, exist_ok=True)
        
        db_url = str(engine.url)
        
        if "sqlite" in db_url:
            # SQLite backup - just copy the file
            db_file = db_url.split("///")[-1]
            if os.path.exists(db_file):
                shutil.copy2(db_file, db_backup_path / "orbis.db")
                logger.info(f"✅ SQLite database backed up")
        
        elif "postgresql" in db_url:
            # PostgreSQL backup using pg_dump
            output_file = db_backup_path / "orbis_pg.sql"
            
            # Parse connection details
            # Format: postgresql://user:pass@host:port/dbname
            try:
                from urllib.parse import urlparse
                parsed = urlparse(db_url)
                
                env = os.environ.copy()
                env["PGPASSWORD"] = parsed.password or ""
                
                subprocess.run([
                    "pg_dump",
                    "-h", parsed.hostname or "localhost",
                    "-p", str(parsed.port or 5432),
                    "-U", parsed.username or "postgres",
                    "-d", parsed.path.lstrip('/'),
                    "-f", str(output_file),
                    "--format=custom",
                    "--compress=9"
                ], env=env, check=True)
                
                logger.info(f"✅ PostgreSQL database backed up")
            except subprocess.CalledProcessError as e:
                logger.error(f"PostgreSQL backup failed: {e}")
                raise
        
        return db_backup_path
    
    async def _backup_files(self, backup_path: Path) -> Path:
        """Backup user files (voices, uploads, etc)"""
        files_backup_path = backup_path / "files"
        files_backup_path.mkdir(parents=True, exist_ok=True)
        
        # Directories to backup
        dirs_to_backup = [
            ("voices", settings.voices_path),
            ("uploads", settings.uploads_path),
            ("models", settings.models_path)
        ]
        
        for dir_name, source_path in dirs_to_backup:
            if os.path.exists(source_path):
                dest_path = files_backup_path / dir_name
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                logger.info(f"✅ Backed up {dir_name}: {source_path}")
        
        return files_backup_path
    
    async def _compress_backup(self, backup_path: Path) -> Path:
        """Compress backup directory to .tar.gz"""
        compressed_path = backup_path.with_suffix('.tar.gz')
        
        # Create tar.gz archive
        shutil.make_archive(
            base_name=str(backup_path),
            format='gztar',
            root_dir=str(backup_path.parent),
            base_dir=backup_path.name
        )
        
        # Remove uncompressed backup
        shutil.rmtree(backup_path)
        
        logger.info(f"✅ Backup compressed: {compressed_path}")
        return compressed_path
    
    async def _cleanup_old_backups(self):
        """Remove old backups based on retention policy"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
        
        backups = list(self.backup_dir.glob("orbis_backup_*.tar.gz"))
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Keep only max_backups newest backups
        removed_count = 0
        
        for backup in backups[self.max_backups:]:
            backup.unlink()
            removed_count += 1
            logger.info(f"🗑️ Removed old backup (max limit): {backup.name}")
        
        # Remove backups older than retention period
        for backup in backups[:self.max_backups]:
            backup_time = datetime.fromtimestamp(backup.stat().st_mtime)
            if backup_time < cutoff_date:
                backup.unlink()
                removed_count += 1
                logger.info(f"🗑️ Removed old backup (retention): {backup.name}")
        
        if removed_count > 0:
            logger.info(f"✅ Cleaned up {removed_count} old backups")
    
    async def restore_backup(self, backup_name: str) -> dict:
        """
        Restore system from backup
        
        Args:
            backup_name: Name of backup file (without .tar.gz)
        """
        backup_file = self.backup_dir / f"{backup_name}.tar.gz"
        
        if not backup_file.exists():
            return {
                "status": "failed",
                "error": "Backup file not found"
            }
        
        logger.info(f"🔄 Starting restore from: {backup_name}")
        
        try:
            # 1. Extract backup
            extract_path = self.backup_dir / f"{backup_name}_restore"
            shutil.unpack_archive(backup_file, extract_path)
            
            # 2. Load metadata
            metadata_path = extract_path / backup_name / "metadata.json"
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # 3. Restore database
            await self._restore_database(extract_path / backup_name / "database")
            
            # 4. Restore files
            await self._restore_files(extract_path / backup_name / "files")
            
            # 5. Cleanup
            shutil.rmtree(extract_path)
            
            logger.info(f"✅ Restore completed successfully")
            
            return {
                "status": "success",
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"❌ Restore failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _restore_database(self, db_backup_path: Path):
        """Restore database from backup"""
        db_url = str(engine.url)
        
        if "sqlite" in db_url:
            # SQLite restore
            db_file = db_url.split("///")[-1]
            backup_db = db_backup_path / "orbis.db"
            
            if backup_db.exists():
                # Backup current database
                if os.path.exists(db_file):
                    shutil.copy2(db_file, f"{db_file}.pre_restore")
                
                # Restore
                shutil.copy2(backup_db, db_file)
                logger.info("✅ SQLite database restored")
        
        elif "postgresql" in db_url:
            # PostgreSQL restore using pg_restore
            backup_file = db_backup_path / "orbis_pg.sql"
            
            if backup_file.exists():
                from urllib.parse import urlparse
                parsed = urlparse(db_url)
                
                env = os.environ.copy()
                env["PGPASSWORD"] = parsed.password or ""
                
                subprocess.run([
                    "pg_restore",
                    "-h", parsed.hostname or "localhost",
                    "-p", str(parsed.port or 5432),
                    "-U", parsed.username or "postgres",
                    "-d", parsed.path.lstrip('/'),
                    "--clean",
                    "--if-exists",
                    str(backup_file)
                ], env=env, check=True)
                
                logger.info("✅ PostgreSQL database restored")
    
    async def _restore_files(self, files_backup_path: Path):
        """Restore files from backup"""
        dirs_to_restore = [
            ("voices", settings.voices_path),
            ("uploads", settings.uploads_path),
            ("models", settings.models_path)
        ]
        
        for dir_name, dest_path in dirs_to_restore:
            source_path = files_backup_path / dir_name
            
            if source_path.exists():
                # Backup current directory
                if os.path.exists(dest_path):
                    shutil.move(dest_path, f"{dest_path}.pre_restore")
                
                # Restore
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                logger.info(f"✅ Restored {dir_name}: {dest_path}")
    
    def list_backups(self) -> List[dict]:
        """List all available backups"""
        backups = []
        
        for backup_file in self.backup_dir.glob("orbis_backup_*.tar.gz"):
            stat = backup_file.stat()
            
            backups.append({
                "name": backup_file.stem,
                "filename": backup_file.name,
                "size_mb": stat.st_size / (1024 * 1024),
                "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "path": str(backup_file)
            })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x["created_at"], reverse=True)
        
        return backups
    
    def _get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes"""
        total_size = 0
        for item in path.rglob('*'):
            if item.is_file():
                total_size += item.stat().st_size
        return total_size


# Global backup service instance
backup_service = BackupService()
