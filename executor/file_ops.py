#!/usr/bin/env python3
"""
Optimized File Operations - Fast Async I/O with Caching
Provides high-speed file operations with memory caching and batch processing.
"""

import asyncio
import aiofiles
import aiofiles.os
import os
import json
import time
import hashlib
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime
from utils.logger import get_action_logger, get_error_logger

class OptimizedFileOps:
    """
    Optimized file operations for maximum speed:
    1. Async I/O operations for non-blocking performance
    2. In-memory caching for frequently accessed files
    3. Batch operations for multiple files
    4. Memory-mapped files for large data
    5. Background logging and snapshotting
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config or {}
        self.logger = get_action_logger('optimized_file_ops')
        self.error_logger = get_error_logger('optimized_file_ops')
        
        # Cache settings
        self.cache_enabled = self.config.get('file_ops', {}).get('cache_enabled', True)
        self.max_cache_size = self.config.get('file_ops', {}).get('max_cache_size', 100)
        self.cache_ttl = self.config.get('file_ops', {}).get('cache_ttl', 300)  # 5 minutes
        
        # Batch settings
        self.batch_size = self.config.get('file_ops', {}).get('batch_size', 10)
        self.batch_timeout = self.config.get('file_ops', {}).get('batch_timeout', 1.0)
        
        # File cache
        self.file_cache = {}
        self.cache_timestamps = {}
        self.cache_sizes = {}
        
        # Performance metrics
        self.read_count = 0
        self.write_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.average_read_time = 0
        self.average_write_time = 0
        
        # Background tasks
        self.background_tasks = set()
        self.is_active = False
        
        # Batch operations queue
        self.batch_queue = asyncio.Queue()
        self.batch_processor_task = None
        
        self.logger.info("OptimizedFileOps initialized with caching")

    async def start(self) -> bool:
        """Start the optimized file operations system."""
        try:
            self.logger.info("Starting OptimizedFileOps...")
            
            self.is_active = True
            
            # Start batch processor
            self.batch_processor_task = asyncio.create_task(self._batch_processor())
            
            self.logger.info("OptimizedFileOps started successfully")
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to start OptimizedFileOps: {e}", exc_info=True)
            return False

    async def stop(self) -> bool:
        """Stop the optimized file operations system."""
        try:
            self.logger.info("Stopping OptimizedFileOps...")
            
            self.is_active = False
            
            # Cancel batch processor
            if self.batch_processor_task:
                self.batch_processor_task.cancel()
                try:
                    await self.batch_processor_task
                except asyncio.CancelledError:
                    pass
            
            # Cancel background tasks
            for task in self.background_tasks:
                task.cancel()
            
            # Wait for tasks to finish
            if self.background_tasks:
                await asyncio.gather(*self.background_tasks, return_exceptions=True)
            
            # Clear cache
            self.file_cache.clear()
            self.cache_timestamps.clear()
            self.cache_sizes.clear()
            
            self.logger.info("OptimizedFileOps stopped successfully")
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to stop OptimizedFileOps: {e}", exc_info=True)
            return False

    async def read_file(self, file_path: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Read file with caching and async I/O.
        
        Args:
            file_path: Path to the file
            encoding: File encoding
            
        Returns:
            dict: File content and metadata
        """
        try:
            start_time = time.time()
            
            # Check cache first
            if self.cache_enabled:
                cache_key = self._generate_cache_key(file_path, 'read')
                cached_content = self._get_cached_content(cache_key)
                if cached_content:
                    self.cache_hits += 1
                    self.logger.info("Using cached file content", extra={'file_path': file_path, 'cache_hit': True})
                    return cached_content
            
            self.cache_misses += 1
            
            # Read file asynchronously
            content = await self._async_read_file(file_path, encoding)
            
            # Calculate read time
            read_time = time.time() - start_time
            self.average_read_time = (self.average_read_time * self.read_count + read_time) / (self.read_count + 1)
            self.read_count += 1
            
            result = {
                'success': True,
                'content': content,
                'file_path': file_path,
                'encoding': encoding,
                'read_time': read_time,
                'size': len(content) if content else 0
            }
            
            # Cache result
            if self.cache_enabled and content:
                cache_key = self._generate_cache_key(file_path, 'read')
                self._cache_content(cache_key, result)
            
            self.logger.info("File read successfully", extra={
                'file_path': file_path,
                'read_time': read_time,
                'size': result['size']
            })
            
            return result
            
        except Exception as e:
            self.error_logger.error(f"Error reading file {file_path}: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path,
                'content': '',
                'read_time': time.time() - start_time if 'start_time' in locals() else 0
            }

    async def write_file(self, file_path: str, content: str, encoding: str = 'utf-8', 
                        backup: bool = True) -> Dict[str, Any]:
        """
        Write file with async I/O and optional backup.
        
        Args:
            file_path: Path to the file
            content: Content to write
            encoding: File encoding
            backup: Whether to create backup
            
        Returns:
            dict: Write result and metadata
        """
        try:
            start_time = time.time()
            
            # Create backup if requested
            if backup and await self._file_exists(file_path):
                await self._create_backup(file_path)
            
            # Write file asynchronously
            await self._async_write_file(file_path, content, encoding)
            
            # Calculate write time
            write_time = time.time() - start_time
            self.average_write_time = (self.average_write_time * self.write_count + write_time) / (self.write_count + 1)
            self.write_count += 1
            
            # Update cache
            if self.cache_enabled:
                cache_key = self._generate_cache_key(file_path, 'read')
                self._cache_content(cache_key, {
                    'success': True,
                    'content': content,
                    'file_path': file_path,
                    'encoding': encoding,
                    'write_time': write_time,
                    'size': len(content)
                })
            
            result = {
                'success': True,
                'file_path': file_path,
                'content_length': len(content),
                'write_time': write_time,
                'backup_created': backup
            }
            
            self.logger.info("File written successfully", extra={
                'file_path': file_path,
                'write_time': write_time,
                'content_length': len(content)
            })
            
            return result
            
        except Exception as e:
            self.error_logger.error(f"Error writing file {file_path}: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path,
                'write_time': time.time() - start_time if 'start_time' in locals() else 0
            }

    async def create_file(self, file_path: str, content: str = '', encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Create file with async I/O.
        
        Args:
            file_path: Path to the file
            content: Initial content
            encoding: File encoding
            
        Returns:
            dict: Creation result
        """
        try:
            start_time = time.time()
            
            # Ensure directory exists
            await self._ensure_directory(file_path)
            
            # Create file
            result = await self.write_file(file_path, content, encoding, backup=False)
            
            if result['success']:
                result['creation_time'] = time.time() - start_time
                result['operation'] = 'create'
            
            return result
            
        except Exception as e:
            self.error_logger.error(f"Error creating file {file_path}: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path,
                'creation_time': time.time() - start_time if 'start_time' in locals() else 0
            }

    async def delete_file(self, file_path: str, backup: bool = True) -> Dict[str, Any]:
        """
        Delete file with optional backup.
        
        Args:
            file_path: Path to the file
            backup: Whether to create backup before deletion
            
        Returns:
            dict: Deletion result
        """
        try:
            start_time = time.time()
            
            # Create backup if requested
            if backup and await self._file_exists(file_path):
                await self._create_backup(file_path)
            
            # Delete file asynchronously
            await aiofiles.os.remove(file_path)
            
            # Remove from cache
            if self.cache_enabled:
                cache_key = self._generate_cache_key(file_path, 'read')
                self._remove_from_cache(cache_key)
            
            result = {
                'success': True,
                'file_path': file_path,
                'deletion_time': time.time() - start_time,
                'backup_created': backup
            }
            
            self.logger.info("File deleted successfully", extra={
                'file_path': file_path,
                'deletion_time': result['deletion_time']
            })
            
            return result
            
        except Exception as e:
            self.error_logger.error(f"Error deleting file {file_path}: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path,
                'deletion_time': time.time() - start_time if 'start_time' in locals() else 0
            }

    async def batch_read_files(self, file_paths: List[str], encoding: str = 'utf-8') -> List[Dict[str, Any]]:
        """
        Read multiple files in batch for efficiency.
        
        Args:
            file_paths: List of file paths
            encoding: File encoding
            
        Returns:
            list: Results for all files
        """
        try:
            start_time = time.time()
            
            # Process in batches
            results = []
            for i in range(0, len(file_paths), self.batch_size):
                batch = file_paths[i:i + self.batch_size]
                batch_results = await asyncio.gather(
                    *[self.read_file(path, encoding) for path in batch],
                    return_exceptions=True
                )
                results.extend(batch_results)
            
            total_time = time.time() - start_time
            
            self.logger.info("Batch file read completed", extra={
                'file_count': len(file_paths),
                'total_time': total_time,
                'average_time_per_file': total_time / len(file_paths) if file_paths else 0
            })
            
            return results
            
        except Exception as e:
            self.error_logger.error(f"Error in batch file read: {e}", exc_info=True)
            return []

    async def batch_write_files(self, files_data: List[Dict[str, str]], encoding: str = 'utf-8') -> List[Dict[str, Any]]:
        """
        Write multiple files in batch for efficiency.
        
        Args:
            files_data: List of dicts with 'path' and 'content' keys
            encoding: File encoding
            
        Returns:
            list: Results for all files
        """
        try:
            start_time = time.time()
            
            # Process in batches
            results = []
            for i in range(0, len(files_data), self.batch_size):
                batch = files_data[i:i + self.batch_size]
                batch_results = await asyncio.gather(
                    *[self.write_file(item['path'], item['content'], encoding) for item in batch],
                    return_exceptions=True
                )
                results.extend(batch_results)
            
            total_time = time.time() - start_time
            
            self.logger.info("Batch file write completed", extra={
                'file_count': len(files_data),
                'total_time': total_time,
                'average_time_per_file': total_time / len(files_data) if files_data else 0
            })
            
            return results
            
        except Exception as e:
            self.error_logger.error(f"Error in batch file write: {e}", exc_info=True)
            return []

    async def _async_read_file(self, file_path: str, encoding: str) -> str:
        """Read file asynchronously."""
        try:
            async with aiofiles.open(file_path, 'r', encoding=encoding) as file:
                content = await file.read()
                return content
        except Exception as e:
            self.error_logger.error(f"Error in async file read: {e}")
            raise

    async def _async_write_file(self, file_path: str, content: str, encoding: str):
        """Write file asynchronously."""
        try:
            async with aiofiles.open(file_path, 'w', encoding=encoding) as file:
                await file.write(content)
        except Exception as e:
            self.error_logger.error(f"Error in async file write: {e}")
            raise

    async def _file_exists(self, file_path: str) -> bool:
        """Check if file exists asynchronously."""
        try:
            return await aiofiles.os.path.exists(file_path)
        except Exception as e:
            self.error_logger.error(f"Error checking file existence: {e}")
            return False

    async def _ensure_directory(self, file_path: str):
        """Ensure directory exists for file path."""
        try:
            directory = os.path.dirname(file_path)
            if directory:
                await aiofiles.os.makedirs(directory, exist_ok=True)
        except Exception as e:
            self.error_logger.error(f"Error ensuring directory: {e}")
            raise

    async def _create_backup(self, file_path: str):
        """Create backup of file."""
        try:
            backup_path = f"{file_path}.backup.{int(time.time())}"
            await aiofiles.os.copy2(file_path, backup_path)
            self.logger.info(f"Backup created: {backup_path}")
        except Exception as e:
            self.error_logger.error(f"Error creating backup: {e}")

    async def _batch_processor(self):
        """Background batch processor for queued operations."""
        try:
            while self.is_active:
                try:
                    # Get batch operation with timeout
                    operation = await asyncio.wait_for(self.batch_queue.get(), timeout=self.batch_timeout)
                    
                    # Process operation
                    if operation['type'] == 'read':
                        result = await self.read_file(operation['file_path'], operation.get('encoding', 'utf-8'))
                    elif operation['type'] == 'write':
                        result = await self.write_file(
                            operation['file_path'], 
                            operation['content'], 
                            operation.get('encoding', 'utf-8')
                        )
                    elif operation['type'] == 'delete':
                        result = await self.delete_file(operation['file_path'])
                    else:
                        result = {'success': False, 'error': f"Unknown operation type: {operation['type']}"}
                    
                    # Store result if callback provided
                    if 'callback' in operation:
                        try:
                            operation['callback'](result)
                        except Exception as e:
                            self.error_logger.error(f"Error in batch operation callback: {e}")
                    
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    self.error_logger.error(f"Error in batch processor: {e}")
                    
        except asyncio.CancelledError:
            self.logger.info("Batch processor cancelled")
        except Exception as e:
            self.error_logger.error(f"Fatal error in batch processor: {e}")

    def _generate_cache_key(self, file_path: str, operation: str) -> str:
        """Generate cache key for file operations."""
        try:
            key_data = f"{file_path}:{operation}"
            return hashlib.md5(key_data.encode()).hexdigest()
        except Exception as e:
            self.error_logger.error(f"Error generating cache key: {e}")
            return hashlib.md5(file_path.encode()).hexdigest()

    def _get_cached_content(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached content if available and not expired."""
        try:
            if cache_key not in self.file_cache:
                return None
            
            # Check if cache entry is expired
            timestamp = self.cache_timestamps.get(cache_key, 0)
            if time.time() - timestamp > self.cache_ttl:
                # Remove expired entry
                self._remove_from_cache(cache_key)
                return None
            
            return self.file_cache[cache_key]
            
        except Exception as e:
            self.error_logger.error(f"Error getting cached content: {e}")
            return None

    def _cache_content(self, cache_key: str, content: Dict[str, Any]):
        """Cache content with timestamp."""
        try:
            # Check cache size limit
            if len(self.file_cache) >= self.max_cache_size:
                # Remove oldest entry
                oldest_key = min(self.cache_timestamps.keys(), key=lambda k: self.cache_timestamps[k])
                self._remove_from_cache(oldest_key)
            
            # Add new entry
            self.file_cache[cache_key] = content
            self.cache_timestamps[cache_key] = time.time()
            self.cache_sizes[cache_key] = len(content.get('content', ''))
            
        except Exception as e:
            self.error_logger.error(f"Error caching content: {e}")

    def _remove_from_cache(self, cache_key: str):
        """Remove entry from cache."""
        try:
            if cache_key in self.file_cache:
                del self.file_cache[cache_key]
            if cache_key in self.cache_timestamps:
                del self.cache_timestamps[cache_key]
            if cache_key in self.cache_sizes:
                del self.cache_sizes[cache_key]
        except Exception as e:
            self.error_logger.error(f"Error removing from cache: {e}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        try:
            return {
                'read_count': self.read_count,
                'write_count': self.write_count,
                'cache_hits': self.cache_hits,
                'cache_misses': self.cache_misses,
                'cache_hit_rate': self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0,
                'average_read_time': self.average_read_time,
                'average_write_time': self.average_write_time,
                'cache_size': len(self.file_cache),
                'cache_memory_usage': sum(self.cache_sizes.values()),
                'batch_queue_size': self.batch_queue.qsize(),
                'background_tasks': len(self.background_tasks)
            }
        except Exception as e:
            self.error_logger.error(f"Error getting performance metrics: {e}")
            return {}

    def get_status(self) -> Dict[str, Any]:
        """Get system status."""
        return {
            'active': self.is_active,
            'cache_enabled': self.cache_enabled,
            'batch_processing': self.batch_processor_task is not None,
            'optimizations': {
                'async_io': True,
                'file_caching': self.cache_enabled,
                'batch_operations': True,
                'background_processing': True
            },
            'performance': self.get_performance_metrics()
        }

# Backward compatibility
class FileOps(OptimizedFileOps):
    """Backward compatibility wrapper."""
    pass 