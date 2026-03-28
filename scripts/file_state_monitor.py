#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件状态监控器
监控文件变化，预防编辑冲突
"""

import os
import sys
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import threading
import json

class FileStateMonitor:
    """文件状态监控器"""
    
    def __init__(self, workspace_path: str = "/Users/ago/.openclaw/workspace"):
        self.workspace_path = Path(workspace_path)
        self.state_file = self.workspace_path / '.file_state_monitor.json'
        
        # 文件状态缓存
        self.file_states: Dict[str, Dict] = {}
        self.locked_files: Set[str] = set()
        
        # 加载历史状态
        self._load_state()
        
        # 监控线程
        self.monitoring = False
        self.monitor_thread = None
        
        # 配置
        self.config = {
            'check_interval': 1.0,  # 检查间隔(秒)
            'max_lock_time': 30.0,  # 最大锁定时间(秒)
            'auto_unlock': True,    # 自动解锁超时文件
            'log_changes': True     # 记录文件变化
        }
    
    def _load_state(self):
        """加载状态文件"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.file_states = data.get('file_states', {})
                    self.locked_files = set(data.get('locked_files', []))
            except Exception as e:
                print(f"加载状态文件失败: {e}")
                self.file_states = {}
                self.locked_files = set()
    
    def _save_state(self):
        """保存状态文件"""
        try:
            data = {
                'file_states': self.file_states,
                'locked_files': list(self.locked_files),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存状态文件失败: {e}")
    
    def get_file_hash(self, file_path: str) -> str:
        """获取文件哈希值"""
        full_path = self.workspace_path / file_path
        
        if not full_path.exists():
            return "FILE_NOT_EXISTS"
        
        try:
            with open(full_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception as e:
            return f"ERROR:{str(e)}"
    
    def get_file_state(self, file_path: str) -> Dict:
        """获取文件状态"""
        full_path = self.workspace_path / file_path
        
        if not full_path.exists():
            return {
                'exists': False,
                'locked': file_path in self.locked_files,
                'error': '文件不存在'
            }
        
        try:
            stat = full_path.stat()
            file_hash = self.get_file_hash(file_path)
            
            state = {
                'exists': True,
                'path': file_path,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'hash': file_hash,
                'locked': file_path in self.locked_files,
                'last_checked': time.time()
            }
            
            # 检查是否被修改
            if file_path in self.file_states:
                old_state = self.file_states[file_path]
                if old_state.get('hash') != file_hash:
                    state['changed'] = True
                    state['old_hash'] = old_state.get('hash')
                else:
                    state['changed'] = False
            
            return state
            
        except Exception as e:
            return {
                'exists': False,
                'locked': file_path in self.locked_files,
                'error': str(e)
            }
    
    def lock_file(self, file_path: str, lock_id: str = None) -> bool:
        """锁定文件"""
        if file_path in self.locked_files:
            print(f"文件已被锁定: {file_path}")
            return False
        
        if lock_id is None:
            lock_id = f"lock_{int(time.time())}_{hash(file_path) % 10000}"
        
        self.locked_files.add(file_path)
        
        # 记录锁定信息
        if file_path not in self.file_states:
            self.file_states[file_path] = {}
        
        self.file_states[file_path]['lock'] = {
            'id': lock_id,
            'time': time.time(),
            'expires': time.time() + self.config['max_lock_time']
        }
        
        self._save_state()
        print(f"✅ 文件锁定成功: {file_path} (ID: {lock_id})")
        return True
    
    def unlock_file(self, file_path: str, lock_id: str = None) -> bool:
        """解锁文件"""
        if file_path not in self.locked_files:
            print(f"文件未被锁定: {file_path}")
            return True
        
        if lock_id:
            # 检查锁定ID是否匹配
            file_state = self.file_states.get(file_path, {})
            file_lock = file_state.get('lock', {})
            if file_lock.get('id') != lock_id:
                print(f"锁定ID不匹配: 期望{lock_id}, 实际{file_lock.get('id')}")
                return False
        
        self.locked_files.remove(file_path)
        
        # 清理锁定信息
        if file_path in self.file_states:
            if 'lock' in self.file_states[file_path]:
                del self.file_states[file_path]['lock']
        
        self._save_state()
        print(f"✅ 文件解锁成功: {file_path}")
        return True
    
    def check_file_safe(self, file_path: str, operation: str = 'edit') -> Tuple[bool, str]:
        """
        检查文件是否安全可操作
        
        Args:
            file_path: 文件路径
            operation: 操作类型 (edit, write, delete)
        
        Returns:
            (是否安全, 原因)
        """
        # 检查文件是否被锁定
        if file_path in self.locked_files:
            lock_info = self.file_states.get(file_path, {}).get('lock', {})
            lock_time = lock_info.get('time', 0)
            lock_id = lock_info.get('id', 'unknown')
            
            # 检查是否超时
            if time.time() - lock_time > self.config['max_lock_time']:
                if self.config['auto_unlock']:
                    self.unlock_file(file_path, lock_id)
                    return True, "锁定已超时，自动解锁"
                else:
                    return False, f"文件被锁定(ID: {lock_id})且已超时"
            else:
                return False, f"文件被其他操作锁定(ID: {lock_id})"
        
        # 获取当前状态
        current_state = self.get_file_state(file_path)
        
        if not current_state['exists'] and operation in ['edit', 'delete']:
            return False, "文件不存在"
        
        # 检查文件是否正在被修改
        if file_path in self.file_states:
            old_state = self.file_states[file_path]
            if old_state.get('hash') != current_state.get('hash'):
                return False, "文件正在被其他进程修改"
        
        return True, "文件状态安全"
    
    def safe_operation(self, file_path: str, operation: str, callback, *args, **kwargs):
        """
        安全执行文件操作
        
        Args:
            file_path: 文件路径
            operation: 操作类型
            callback: 要执行的回调函数
            *args, **kwargs: 回调函数参数
        
        Returns:
            (成功, 结果, 错误信息)
        """
        # 检查安全性
        safe, reason = self.check_file_safe(file_path, operation)
        if not safe:
            return False, None, f"操作不安全: {reason}"
        
        # 锁定文件
        lock_id = f"{operation}_{int(time.time())}"
        if not self.lock_file(file_path, lock_id):
            return False, None, "锁定文件失败"
        
        try:
            # 记录操作前状态
            before_state = self.get_file_state(file_path)
            
            # 执行操作
            result = callback(*args, **kwargs)
            
            # 记录操作后状态
            after_state = self.get_file_state(file_path)
            
            # 记录变化
            if self.config['log_changes']:
                self._log_change(file_path, operation, before_state, after_state)
            
            # 更新文件状态
            self.file_states[file_path] = after_state
            
            return True, result, "操作成功"
            
        except Exception as e:
            return False, None, f"操作失败: {str(e)}"
            
        finally:
            # 解锁文件
            self.unlock_file(file_path, lock_id)
    
    def _log_change(self, file_path: str, operation: str, before: Dict, after: Dict):
        """记录文件变化"""
        change_log = {
            'timestamp': datetime.now().isoformat(),
            'file': file_path,
            'operation': operation,
            'before': before,
            'after': after,
            'changed': before.get('hash') != after.get('hash')
        }
        
        # 保存到日志文件
        log_dir = self.workspace_path / 'logs' / 'file_changes'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"changes_{datetime.now().strftime('%Y%m%d')}.json"
        
        try:
            logs = []
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            
            logs.append(change_log)
            
            # 只保留最近1000条记录
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"记录变化日志失败: {e}")
    
    def start_monitoring(self, files_to_watch: List[str] = None):
        """开始监控"""
        if self.monitoring:
            print("监控已在运行")
            return
        
        self.monitoring = True
        
        def monitor_loop():
            print(f"开始文件状态监控 ({len(files_to_watch or [])}个文件)")
            
            while self.monitoring:
                try:
                    # 检查文件状态
                    if files_to_watch:
                        for file_path in files_to_watch:
                            state = self.get_file_state(file_path)
                            
                            # 检查锁定超时
                            if file_path in self.locked_files:
                                lock_info = self.file_states.get(file_path, {}).get('lock', {})
                                lock_time = lock_info.get('time', 0)
                                
                                if time.time() - lock_time > self.config['max_lock_time']:
                                    print(f"⚠️ 文件锁定超时: {file_path}")
                                    if self.config['auto_unlock']:
                                        self.unlock_file(file_path, lock_info.get('id'))
                    
                    # 保存状态
                    self._save_state()
                    
                    # 等待
                    time.sleep(self.config['check_interval'])
                    
                except Exception as e:
                    print(f"监控循环错误: {e}")
                    time.sleep(5)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print("✅ 文件状态监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self._save_state()
        print("✅ 文件状态监控已停止")
    
    def get_problem_files(self) -> List[Dict]:
        """获取有问题的文件"""
        problems = []
        
        for file_path in list(self.locked_files):
            lock_info = self.file_states.get(file_path, {}).get('lock', {})
            lock_time = lock_info.get('time', 0)
            
            if time.time() - lock_time > self.config['max_lock_time']:
                problems.append({
                    'file': file_path,
                    'problem': '锁定超时',
                    'lock_time': lock_time,
                    'lock_id': lock_info.get('id'),
                    'suggestion': '自动解锁或手动检查'
                })
        
        return problems
    
    def cleanup(self):
        """清理状态"""
        # 解锁所有文件
        for file_path in list(self.locked_files):
            self.unlock_file(file_path)
        
        # 清理旧的状态记录
        cutoff_time = time.time() - 3600  # 1小时前
        
        files_to_remove = []
        for file_path, state in self.file_states.items():
            last_checked = state.get('last_checked', 0)
            if last_checked < cutoff_time:
                files_to_remove.append(file_path)
        
        for file_path in files_to_remove:
            del self.file_states[file_path]
        
        self._save_state()
        print(f"✅ 清理完成: 移除了{len(files_to_remove)}个旧记录")


def example_usage():
    """使用示例"""
    print("文件状态监控器 - 使用示例")
    print("=" * 60)
    
    monitor = FileStateMonitor()
    
    # 示例文件
    test_file = "scripts/test_monitor.py"
    
    print("\n1. 检查文件状态:")
    state = monitor.get_file_state(test_file)
    print(f"文件: {test_file}")
    print(f"存在: {state.get('exists', False)}")
    print(f"大小: {state.get('size', 0)}字节")
    print(f"锁定: {state.get('locked', False)}")
    
    print("\n2. 锁定文件:")
    if monitor.lock_file(test_file, "test_lock"):
        print("✅ 锁定成功")
    else:
        print("❌ 锁定失败")
    
    print("\n3. 检查操作安全性:")
    safe, reason = monitor.check_file_safe(test_file, 'edit')
    print(f"安全: {safe}")
    print(f"原因: {reason}")
    
    print("\n4. 安全执行操作:")
    def test_callback():
        print("  执行回调函数...")
        return "操作结果"
    
    success, result, error = monitor.safe_operation(
        test_file, 'edit', test_callback
    )
    
    print(f"成功: {success}")
    print(f"结果: {result}")
    print(f"错误: {error}")
    
    print("\n5. 解锁文件:")
    monitor.unlock_file(test_file, "test_lock")
    
    print("\n6. 清理:")
    monitor.cleanup()
    
    print("\n" + "=" * 60)
    print("核心功能:")
    print("1. 文件状态监控: 实时监控文件变化")
    print("2. 文件锁定: 防止并发操作冲突")
    print("3. 安全检查: 确保操作前文件状态安全")
    print("4. 变化日志: 记录所有文件操作")
    print("\n解决edit失败问题的关键:")
    print("✅ 防止并发操作冲突")
    print("✅ 监控文件状态变化")
    print("✅ 自动处理锁定超时")
    print("✅ 完整的操作日志")


if __name__ == "__main__":
    example_usage()