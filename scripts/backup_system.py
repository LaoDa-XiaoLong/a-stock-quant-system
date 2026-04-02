#!/usr/bin/env python3
import os
from datetime import datetime
import shutil

def main():
    print(f'系统备份 - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 60)

    backup_dir = 'backups/daily'
    os.makedirs(backup_dir, exist_ok=True)

    # 备份重要目录
    dirs_to_backup = ['scripts', 'strategies', 'config', 'docs']

    for dir_name in dirs_to_backup:
        if os.path.exists(dir_name):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f'{dir_name}_backup_{timestamp}.tar.gz'
            backup_path = os.path.join(backup_dir, backup_name)

            # 创建tar.gz备份
            import tarfile
            with tarfile.open(backup_path, 'w:gz') as tar:
                tar.add(dir_name)

            size_mb = os.path.getsize(backup_path) / (1024 * 1024)
            print(f'✅ {dir_name}: {backup_path} ({size_mb:.1f}MB)')

    print(f'
备份完成! 备份目录: {backup_dir}')

if __name__ == '__main__':
    main()
