"""
Sharding Manager
Advanced database sharding and partitioning for BigTech scale
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import uuid
import hashlib
import json
import math

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
import numpy as np

from backend.config import settings
from backend.db.enterprise_database import enterprise_database, DatabaseShard

logger = logging.getLogger(__name__)


class ShardingStrategy(Enum):
    """Sharding strategies"""
    HASH = "hash"
    RANGE = "range"
    DIRECTORY = "directory"
    CONSISTENT_HASH = "consistent_hash"


class PartitionStrategy(Enum):
    """Partitioning strategies"""
    TIME_BASED = "time_based"
    USER_BASED = "user_based"
    GEOGRAPHIC = "geographic"
    CUSTOM = "custom"


@dataclass
class ShardConfig:
    """Shard configuration"""
    shard_id: str
    database_host: str
    database_port: int
    database_name: str
    weight: int = 1
    is_active: bool = True
    created_at: datetime = None
    last_rebalanced: datetime = None


@dataclass
class PartitionConfig:
    """Partition configuration"""
    partition_id: str
    table_name: str
    partition_key: str
    partition_strategy: PartitionStrategy
    partition_expression: str
    created_at: datetime = None


@dataclass
class ShardingMetrics:
    """Sharding performance metrics"""
    shard_id: str
    total_queries: int
    avg_query_time: float
    total_rows: int
    storage_size_mb: float
    connection_count: int
    last_updated: datetime


class ShardingManager:
    """Advanced sharding and partitioning manager for BigTech scale"""
    
    def __init__(self):
        self.shards = {}
        self.partitions = {}
        self.sharding_strategy = ShardingStrategy.CONSISTENT_HASH
        self.partition_strategy = PartitionStrategy.TIME_BASED
        self.shard_weights = {}
        self.consistent_hash_ring = {}
        self.rebalancing_in_progress = False
        
        # Performance monitoring
        self.shard_metrics = {}
        self.query_routing_cache = {}
        self.hot_spot_detection = {}
        
        # Auto-scaling configuration
        self.auto_scaling_config = {
            "min_shards": 3,
            "max_shards": 100,
            "scale_up_threshold": 80,  # CPU/Memory usage %
            "scale_down_threshold": 20,
            "rebalance_threshold": 30,  # Data imbalance %
            "check_interval": 300  # 5 minutes
        }
    
    async def initialize(self):
        """Initialize sharding manager"""
        try:
            logger.info("🚀 Initializing Sharding Manager...")
            
            # Initialize shard configurations
            await self._initialize_shards()
            
            # Initialize partitions
            await self._initialize_partitions()
            
            # Build consistent hash ring
            await self._build_consistent_hash_ring()
            
            # Start background tasks
            asyncio.create_task(self._shard_monitor())
            asyncio.create_task(self._auto_scaler())
            asyncio.create_task(self._hot_spot_detector())
            asyncio.create_task(self._query_optimizer())
            
            logger.info("✅ Sharding Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Sharding Manager: {e}")
            raise
    
    async def _initialize_shards(self):
        """Initialize database shards"""
        try:
            # Primary shards for different data types
            shard_configs = [
                ShardConfig(
                    shard_id="users_primary",
                    database_host=settings.database_host,
                    database_port=settings.database_port,
                    database_name=f"{settings.database_name}_users_primary",
                    weight=10,
                    created_at=datetime.utcnow()
                ),
                ShardConfig(
                    shard_id="users_secondary",
                    database_host=settings.database_host,
                    database_port=settings.database_port,
                    database_name=f"{settings.database_name}_users_secondary",
                    weight=10,
                    created_at=datetime.utcnow()
                ),
                ShardConfig(
                    shard_id="meetings_primary",
                    database_host=settings.database_host,
                    database_port=settings.database_port,
                    database_name=f"{settings.database_name}_meetings_primary",
                    weight=15,
                    created_at=datetime.utcnow()
                ),
                ShardConfig(
                    shard_id="meetings_secondary",
                    database_host=settings.database_host,
                    database_port=settings.database_port,
                    database_name=f"{settings.database_name}_meetings_secondary",
                    weight=15,
                    created_at=datetime.utcnow()
                ),
                ShardConfig(
                    shard_id="analytics_primary",
                    database_host=settings.database_host,
                    database_port=settings.database_port,
                    database_name=f"{settings.database_name}_analytics_primary",
                    weight=20,
                    created_at=datetime.utcnow()
                ),
                ShardConfig(
                    shard_id="analytics_secondary",
                    database_host=settings.database_host,
                    database_port=settings.database_port,
                    database_name=f"{settings.database_name}_analytics_secondary",
                    weight=20,
                    created_at=datetime.utcnow()
                ),
                ShardConfig(
                    shard_id="social_primary",
                    database_host=settings.database_host,
                    database_port=settings.database_port,
                    database_name=f"{settings.database_name}_social_primary",
                    weight=8,
                    created_at=datetime.utcnow()
                ),
                ShardConfig(
                    shard_id="social_secondary",
                    database_host=settings.database_host,
                    database_port=settings.database_port,
                    database_name=f"{settings.database_name}_social_secondary",
                    weight=8,
                    created_at=datetime.utcnow()
                ),
                ShardConfig(
                    shard_id="billing_primary",
                    database_host=settings.database_host,
                    database_port=settings.database_port,
                    database_name=f"{settings.database_name}_billing_primary",
                    weight=5,
                    created_at=datetime.utcnow()
                ),
                ShardConfig(
                    shard_id="billing_secondary",
                    database_host=settings.database_host,
                    database_port=settings.database_port,
                    database_name=f"{settings.database_name}_billing_secondary",
                    weight=5,
                    created_at=datetime.utcnow()
                )
            ]
            
            for config in shard_configs:
                self.shards[config.shard_id] = config
                self.shard_weights[config.shard_id] = config.weight
                
                # Initialize metrics
                self.shard_metrics[config.shard_id] = ShardingMetrics(
                    shard_id=config.shard_id,
                    total_queries=0,
                    avg_query_time=0.0,
                    total_rows=0,
                    storage_size_mb=0.0,
                    connection_count=0,
                    last_updated=datetime.utcnow()
                )
            
            logger.info(f"✅ Initialized {len(self.shards)} database shards")
            
        except Exception as e:
            logger.error(f"Failed to initialize shards: {e}")
            raise
    
    async def _initialize_partitions(self):
        """Initialize table partitions"""
        try:
            # Time-based partitions for analytics
            analytics_partitions = [
                PartitionConfig(
                    partition_id="analytics_2024_q1",
                    table_name="meeting_analytics",
                    partition_key="created_at",
                    partition_strategy=PartitionStrategy.TIME_BASED,
                    partition_expression="created_at >= '2024-01-01' AND created_at < '2024-04-01'"
                ),
                PartitionConfig(
                    partition_id="analytics_2024_q2",
                    table_name="meeting_analytics",
                    partition_key="created_at",
                    partition_strategy=PartitionStrategy.TIME_BASED,
                    partition_expression="created_at >= '2024-04-01' AND created_at < '2024-07-01'"
                ),
                PartitionConfig(
                    partition_id="analytics_2024_q3",
                    table_name="meeting_analytics",
                    partition_key="created_at",
                    partition_strategy=PartitionStrategy.TIME_BASED,
                    partition_expression="created_at >= '2024-07-01' AND created_at < '2024-10-01'"
                ),
                PartitionConfig(
                    partition_id="analytics_2024_q4",
                    table_name="meeting_analytics",
                    partition_key="created_at",
                    partition_strategy=PartitionStrategy.TIME_BASED,
                    partition_expression="created_at >= '2024-10-01' AND created_at < '2025-01-01'"
                )
            ]
            
            # User-based partitions for user data
            user_partitions = [
                PartitionConfig(
                    partition_id="users_0_999999",
                    table_name="users",
                    partition_key="user_id",
                    partition_strategy=PartitionStrategy.USER_BASED,
                    partition_expression="user_id >= 0 AND user_id < 1000000"
                ),
                PartitionConfig(
                    partition_id="users_1000000_1999999",
                    table_name="users",
                    partition_key="user_id",
                    partition_strategy=PartitionStrategy.USER_BASED,
                    partition_expression="user_id >= 1000000 AND user_id < 2000000"
                ),
                PartitionConfig(
                    partition_id="users_2000000_2999999",
                    table_name="users",
                    partition_key="user_id",
                    partition_strategy=PartitionStrategy.USER_BASED,
                    partition_expression="user_id >= 2000000 AND user_id < 3000000"
                )
            ]
            
            # Geographic partitions for global distribution
            geo_partitions = [
                PartitionConfig(
                    partition_id="geo_americas",
                    table_name="meetings",
                    partition_key="region",
                    partition_strategy=PartitionStrategy.GEOGRAPHIC,
                    partition_expression="region IN ('US', 'CA', 'MX', 'BR', 'AR')"
                ),
                PartitionConfig(
                    partition_id="geo_europe",
                    table_name="meetings",
                    partition_key="region",
                    partition_strategy=PartitionStrategy.GEOGRAPHIC,
                    partition_expression="region IN ('GB', 'DE', 'FR', 'IT', 'ES', 'NL')"
                ),
                PartitionConfig(
                    partition_id="geo_asia",
                    table_name="meetings",
                    partition_key="region",
                    partition_strategy=PartitionStrategy.GEOGRAPHIC,
                    partition_expression="region IN ('JP', 'KR', 'CN', 'IN', 'SG', 'AU')"
                )
            ]
            
            all_partitions = analytics_partitions + user_partitions + geo_partitions
            
            for partition in all_partitions:
                self.partitions[partition.partition_id] = partition
            
            logger.info(f"✅ Initialized {len(self.partitions)} table partitions")
            
        except Exception as e:
            logger.error(f"Failed to initialize partitions: {e}")
            raise
    
    async def _build_consistent_hash_ring(self):
        """Build consistent hash ring for shard routing"""
        try:
            # Create virtual nodes for better distribution
            virtual_nodes_per_shard = 100
            
            for shard_id, weight in self.shard_weights.items():
                for i in range(virtual_nodes_per_shard * weight):
                    virtual_node = f"{shard_id}_vnode_{i}"
                    hash_value = self._hash_function(virtual_node)
                    self.consistent_hash_ring[hash_value] = shard_id
            
            # Sort hash ring
            self.consistent_hash_ring = dict(sorted(self.consistent_hash_ring.items()))
            
            logger.info(f"✅ Built consistent hash ring with {len(self.consistent_hash_ring)} virtual nodes")
            
        except Exception as e:
            logger.error(f"Failed to build consistent hash ring: {e}")
            raise
    
    def _hash_function(self, key: str) -> int:
        """Consistent hash function"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    async def get_shard_for_key(self, key: str, data_type: str = "users") -> str:
        """Get shard for a specific key using consistent hashing"""
        try:
            # Check cache first
            cache_key = f"shard_routing:{data_type}:{key}"
            cached_shard = await enterprise_database.cache_get(cache_key, "primary")
            if cached_shard:
                return cached_shard
            
            # Determine shard using consistent hashing
            hash_value = self._hash_function(f"{data_type}:{key}")
            
            # Find the first shard with hash >= hash_value
            for ring_hash, shard_id in self.consistent_hash_ring.items():
                if ring_hash >= hash_value:
                    # Cache the result
                    await enterprise_database.cache_set(cache_key, shard_id, ttl=3600)
                    return shard_id
            
            # If no shard found, use the first one (wrap around)
            shard_id = list(self.consistent_hash_ring.values())[0]
            await enterprise_database.cache_set(cache_key, shard_id, ttl=3600)
            return shard_id
            
        except Exception as e:
            logger.error(f"Failed to get shard for key: {e}")
            # Fallback to primary shard
            return f"{data_type}_primary"
    
    async def get_partition_for_query(self, table_name: str, query_conditions: Dict[str, Any]) -> List[str]:
        """Get relevant partitions for a query"""
        try:
            relevant_partitions = []
            
            for partition_id, partition in self.partitions.items():
                if partition.table_name != table_name:
                    continue
                
                # Check if query conditions match partition
                if await self._query_matches_partition(partition, query_conditions):
                    relevant_partitions.append(partition_id)
            
            # If no specific partitions match, return all partitions for the table
            if not relevant_partitions:
                relevant_partitions = [
                    p.partition_id for p in self.partitions.values() 
                    if p.table_name == table_name
                ]
            
            return relevant_partitions
            
        except Exception as e:
            logger.error(f"Failed to get partitions for query: {e}")
            return []
    
    async def _query_matches_partition(self, partition: PartitionConfig, query_conditions: Dict[str, Any]) -> bool:
        """Check if query conditions match partition criteria"""
        try:
            partition_key = partition.partition_key
            
            if partition_key not in query_conditions:
                return False
            
            query_value = query_conditions[partition_key]
            
            # Parse partition expression
            if partition.partition_strategy == PartitionStrategy.TIME_BASED:
                return await self._check_time_partition(partition, query_value)
            elif partition.partition_strategy == PartitionStrategy.USER_BASED:
                return await self._check_user_partition(partition, query_value)
            elif partition.partition_strategy == PartitionStrategy.GEOGRAPHIC:
                return await self._check_geo_partition(partition, query_value)
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check partition match: {e}")
            return False
    
    async def _check_time_partition(self, partition: PartitionConfig, query_value: Any) -> bool:
        """Check if query value matches time-based partition"""
        try:
            # This would implement time-based partition checking
            # For now, return True for simplicity
            return True
        except Exception as e:
            logger.error(f"Failed to check time partition: {e}")
            return False
    
    async def _check_user_partition(self, partition: PartitionConfig, query_value: Any) -> bool:
        """Check if query value matches user-based partition"""
        try:
            # Parse user ID range from partition expression
            # This would implement user ID range checking
            # For now, return True for simplicity
            return True
        except Exception as e:
            logger.error(f"Failed to check user partition: {e}")
            return False
    
    async def _check_geo_partition(self, partition: PartitionConfig, query_value: Any) -> bool:
        """Check if query value matches geographic partition"""
        try:
            # Check if region matches partition
            # This would implement geographic partition checking
            # For now, return True for simplicity
            return True
        except Exception as e:
            logger.error(f"Failed to check geo partition: {e}")
            return False
    
    async def execute_sharded_query(self, query: str, params: Dict[str, Any], 
                                   data_type: str = "users", key: str = None) -> List[Dict[str, Any]]:
        """Execute query across appropriate shards"""
        try:
            results = []
            
            if key:
                # Single shard query
                shard_id = await self.get_shard_for_key(key, data_type)
                shard_results = await self._execute_on_shard(shard_id, query, params)
                results.extend(shard_results)
            else:
                # Multi-shard query
                relevant_shards = await self._get_relevant_shards(data_type)
                
                # Execute query on all relevant shards in parallel
                tasks = []
                for shard_id in relevant_shards:
                    tasks.append(self._execute_on_shard(shard_id, query, params))
                
                shard_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Combine results
                for shard_result in shard_results:
                    if isinstance(shard_result, list):
                        results.extend(shard_result)
                    else:
                        logger.error(f"Shard query failed: {shard_result}")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to execute sharded query: {e}")
            return []
    
    async def _execute_on_shard(self, shard_id: str, query: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute query on specific shard"""
        try:
            # Map shard_id to DatabaseShard enum
            shard_mapping = {
                "users_primary": DatabaseShard.USERS,
                "users_secondary": DatabaseShard.USERS,
                "meetings_primary": DatabaseShard.MEETINGS,
                "meetings_secondary": DatabaseShard.MEETINGS,
                "analytics_primary": DatabaseShard.ANALYTICS,
                "analytics_secondary": DatabaseShard.ANALYTICS,
                "social_primary": DatabaseShard.SOCIAL,
                "social_secondary": DatabaseShard.SOCIAL,
                "billing_primary": DatabaseShard.BILLING,
                "billing_secondary": DatabaseShard.BILLING
            }
            
            database_shard = shard_mapping.get(shard_id, DatabaseShard.USERS)
            
            # Execute query using enterprise database
            results = await enterprise_database.execute_query(database_shard, query, params)
            
            # Update shard metrics
            await self._update_shard_metrics(shard_id, len(results))
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to execute query on shard {shard_id}: {e}")
            return []
    
    async def _get_relevant_shards(self, data_type: str) -> List[str]:
        """Get relevant shards for data type"""
        try:
            relevant_shards = []
            
            for shard_id in self.shards.keys():
                if data_type in shard_id:
                    relevant_shards.append(shard_id)
            
            return relevant_shards
            
        except Exception as e:
            logger.error(f"Failed to get relevant shards: {e}")
            return []
    
    async def _update_shard_metrics(self, shard_id: str, row_count: int):
        """Update shard performance metrics"""
        try:
            if shard_id in self.shard_metrics:
                metrics = self.shard_metrics[shard_id]
                metrics.total_queries += 1
                metrics.total_rows += row_count
                metrics.last_updated = datetime.utcnow()
                
        except Exception as e:
            logger.error(f"Failed to update shard metrics: {e}")
    
    async def rebalance_shards(self):
        """Rebalance data across shards"""
        try:
            if self.rebalancing_in_progress:
                logger.warning("Rebalancing already in progress")
                return
            
            self.rebalancing_in_progress = True
            logger.info("Starting shard rebalancing...")
            
            # Analyze current data distribution
            distribution = await self._analyze_data_distribution()
            
            # Identify imbalanced shards
            imbalanced_shards = await self._identify_imbalanced_shards(distribution)
            
            # Plan rebalancing
            rebalance_plan = await self._create_rebalance_plan(imbalanced_shards)
            
            # Execute rebalancing
            await self._execute_rebalance_plan(rebalance_plan)
            
            # Update hash ring
            await self._build_consistent_hash_ring()
            
            logger.info("Shard rebalancing completed")
            
        except Exception as e:
            logger.error(f"Failed to rebalance shards: {e}")
        finally:
            self.rebalancing_in_progress = False
    
    async def _analyze_data_distribution(self) -> Dict[str, int]:
        """Analyze current data distribution across shards"""
        try:
            distribution = {}
            
            for shard_id in self.shards.keys():
                # Get row count for each shard
                query = "SELECT COUNT(*) as row_count FROM users"
                results = await self._execute_on_shard(shard_id, query, {})
                
                if results:
                    distribution[shard_id] = results[0]["row_count"]
                else:
                    distribution[shard_id] = 0
            
            return distribution
            
        except Exception as e:
            logger.error(f"Failed to analyze data distribution: {e}")
            return {}
    
    async def _identify_imbalanced_shards(self, distribution: Dict[str, int]) -> List[str]:
        """Identify shards that need rebalancing"""
        try:
            if not distribution:
                return []
            
            total_rows = sum(distribution.values())
            num_shards = len(distribution)
            target_rows_per_shard = total_rows / num_shards
            
            imbalanced_shards = []
            
            for shard_id, row_count in distribution.items():
                imbalance_percentage = abs(row_count - target_rows_per_shard) / target_rows_per_shard * 100
                
                if imbalance_percentage > self.auto_scaling_config["rebalance_threshold"]:
                    imbalanced_shards.append(shard_id)
            
            return imbalanced_shards
            
        except Exception as e:
            logger.error(f"Failed to identify imbalanced shards: {e}")
            return []
    
    async def _create_rebalance_plan(self, imbalanced_shards: List[str]) -> Dict[str, Any]:
        """Create rebalancing plan"""
        try:
            # This would implement sophisticated rebalancing logic
            # For now, return a simple plan
            return {
                "shards_to_rebalance": imbalanced_shards,
                "estimated_duration": "2 hours",
                "data_to_move": "10GB"
            }
            
        except Exception as e:
            logger.error(f"Failed to create rebalance plan: {e}")
            return {}
    
    async def _execute_rebalance_plan(self, plan: Dict[str, Any]):
        """Execute rebalancing plan"""
        try:
            # This would implement actual data movement
            # For now, just log the plan
            logger.info(f"Executing rebalance plan: {plan}")
            
        except Exception as e:
            logger.error(f"Failed to execute rebalance plan: {e}")
    
    async def _shard_monitor(self):
        """Monitor shard health and performance"""
        while True:
            try:
                await asyncio.sleep(60)  # Monitor every minute
                
                # Check shard health
                for shard_id, shard_config in self.shards.items():
                    if not shard_config.is_active:
                        continue
                    
                    # Check shard performance
                    metrics = self.shard_metrics.get(shard_id)
                    if metrics:
                        # Check for performance issues
                        if metrics.avg_query_time > 1.0:  # > 1 second
                            logger.warning(f"Slow queries detected on shard {shard_id}: {metrics.avg_query_time:.2f}s")
                        
                        # Check for high connection usage
                        if metrics.connection_count > 80:  # > 80% capacity
                            logger.warning(f"High connection usage on shard {shard_id}: {metrics.connection_count}%")
                
            except Exception as e:
                logger.error(f"Shard monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _auto_scaler(self):
        """Auto-scale shards based on load"""
        while True:
            try:
                await asyncio.sleep(self.auto_scaling_config["check_interval"])
                
                # Check if scaling is needed
                if await self._should_scale_up():
                    await self._scale_up()
                elif await self._should_scale_down():
                    await self._scale_down()
                
            except Exception as e:
                logger.error(f"Auto scaler error: {e}")
                await asyncio.sleep(self.auto_scaling_config["check_interval"])
    
    async def _should_scale_up(self) -> bool:
        """Check if scaling up is needed"""
        try:
            # Check average CPU/memory usage across shards
            # This would implement actual monitoring logic
            return False
            
        except Exception as e:
            logger.error(f"Failed to check scale up condition: {e}")
            return False
    
    async def _should_scale_down(self) -> bool:
        """Check if scaling down is needed"""
        try:
            # Check if resources are underutilized
            # This would implement actual monitoring logic
            return False
            
        except Exception as e:
            logger.error(f"Failed to check scale down condition: {e}")
            return False
    
    async def _scale_up(self):
        """Scale up by adding new shards"""
        try:
            logger.info("Scaling up database shards...")
            # This would implement actual scaling logic
            
        except Exception as e:
            logger.error(f"Failed to scale up: {e}")
    
    async def _scale_down(self):
        """Scale down by removing underutilized shards"""
        try:
            logger.info("Scaling down database shards...")
            # This would implement actual scaling logic
            
        except Exception as e:
            logger.error(f"Failed to scale down: {e}")
    
    async def _hot_spot_detector(self):
        """Detect and handle hot spots"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                # Analyze query patterns for hot spots
                hot_spots = await self._detect_hot_spots()
                
                if hot_spots:
                    logger.warning(f"Hot spots detected: {hot_spots}")
                    await self._handle_hot_spots(hot_spots)
                
            except Exception as e:
                logger.error(f"Hot spot detector error: {e}")
                await asyncio.sleep(300)
    
    async def _detect_hot_spots(self) -> List[str]:
        """Detect hot spots in the system"""
        try:
            # This would implement hot spot detection logic
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Failed to detect hot spots: {e}")
            return []
    
    async def _handle_hot_spots(self, hot_spots: List[str]):
        """Handle detected hot spots"""
        try:
            # This would implement hot spot handling logic
            # For now, just log
            logger.info(f"Handling hot spots: {hot_spots}")
            
        except Exception as e:
            logger.error(f"Failed to handle hot spots: {e}")
    
    async def _query_optimizer(self):
        """Optimize queries across shards"""
        while True:
            try:
                await asyncio.sleep(600)  # Optimize every 10 minutes
                
                # Analyze slow queries
                slow_queries = await self._identify_slow_queries()
                
                if slow_queries:
                    await self._optimize_queries(slow_queries)
                
            except Exception as e:
                logger.error(f"Query optimizer error: {e}")
                await asyncio.sleep(600)
    
    async def _identify_slow_queries(self) -> List[Dict[str, Any]]:
        """Identify slow queries across shards"""
        try:
            slow_queries = []
            
            for shard_id, metrics in self.shard_metrics.items():
                if metrics.avg_query_time > 0.5:  # > 500ms
                    slow_queries.append({
                        "shard_id": shard_id,
                        "avg_time": metrics.avg_query_time,
                        "total_queries": metrics.total_queries
                    })
            
            return slow_queries
            
        except Exception as e:
            logger.error(f"Failed to identify slow queries: {e}")
            return []
    
    async def _optimize_queries(self, slow_queries: List[Dict[str, Any]]):
        """Optimize slow queries"""
        try:
            for query_info in slow_queries:
                logger.info(f"Optimizing slow query on shard {query_info['shard_id']}")
                # This would implement actual query optimization
                
        except Exception as e:
            logger.error(f"Failed to optimize queries: {e}")
    
    async def get_sharding_metrics(self) -> Dict[str, Any]:
        """Get comprehensive sharding metrics"""
        try:
            return {
                "shards": {
                    shard_id: {
                        "config": {
                            "weight": shard_config.weight,
                            "is_active": shard_config.is_active,
                            "created_at": shard_config.created_at.isoformat() if shard_config.created_at else None
                        },
                        "metrics": {
                            "total_queries": metrics.total_queries,
                            "avg_query_time": metrics.avg_query_time,
                            "total_rows": metrics.total_rows,
                            "storage_size_mb": metrics.storage_size_mb,
                            "connection_count": metrics.connection_count,
                            "last_updated": metrics.last_updated.isoformat()
                        }
                    }
                    for shard_id, shard_config in self.shards.items()
                    for metrics in [self.shard_metrics.get(shard_id)]
                    if metrics
                },
                "partitions": {
                    partition_id: {
                        "table_name": partition.table_name,
                        "partition_key": partition.partition_key,
                        "strategy": partition.partition_strategy.value,
                        "expression": partition.partition_expression
                    }
                    for partition_id, partition in self.partitions.items()
                },
                "hash_ring": {
                    "total_virtual_nodes": len(self.consistent_hash_ring),
                    "shard_distribution": self._get_shard_distribution()
                },
                "auto_scaling": {
                    "config": self.auto_scaling_config,
                    "rebalancing_in_progress": self.rebalancing_in_progress
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get sharding metrics: {e}")
            return {}
    
    def _get_shard_distribution(self) -> Dict[str, int]:
        """Get distribution of virtual nodes across shards"""
        try:
            distribution = {}
            
            for shard_id in self.shards.keys():
                count = sum(1 for s in self.consistent_hash_ring.values() if s == shard_id)
                distribution[shard_id] = count
            
            return distribution
            
        except Exception as e:
            logger.error(f"Failed to get shard distribution: {e}")
            return {}


# Global sharding manager instance
sharding_manager = ShardingManager()
