#!/usr/bin/env python3
"""
檢查要讀取的檔案是否為敏感檔案的腳本
用於 Cursor beforeReadFile hook
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List


# 敏感檔案名單（可根據需求擴充）
SENSITIVE_FILES = [
    # 常見的敏感檔案
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    "config.json",
    "secrets.json",
    "credentials.json",
    "api_keys.json",
    "private_key.pem",
    "id_rsa",
    "id_rsa.pub",
    ".ssh/id_rsa",
    ".ssh/id_rsa.pub",
    "password.txt",
    "passwords.txt",
    "secret.txt",
    "secrets.txt",
    # 資料庫相關
    "database.yml",
    "db_config.json",
    # AWS 相關
    ".aws/credentials",
    ".aws/config",
    # 其他敏感檔案
    "private.key",
    "secret.key",
    "token.txt",
    "重要資訊.txt",
]


def get_filename_from_path(file_path: str) -> str:
    """
    從檔案路徑中取得檔案名稱
    
    Args:
        file_path: 檔案路徑（可能是絕對路徑或相對路徑）
    
    Returns:
        檔案名稱（包含副檔名）
    """
    if not file_path:
        return ""
    
    # 使用 pathlib 來處理路徑，自動處理不同作業系統的路徑分隔符
    path_obj = Path(file_path)
    return path_obj.name


def is_sensitive_file(filename: str) -> bool:
    """
    檢查檔案名稱是否在敏感檔案名單中
    
    Args:
        filename: 檔案名稱
    
    Returns:
        如果是敏感檔案返回 True，否則返回 False
    """
    if not filename:
        return False
    
    # 直接比對檔案名稱（大小寫不敏感）
    filename_lower = filename.lower()
    for sensitive_file in SENSITIVE_FILES:
        if filename_lower == sensitive_file.lower():
            return True
    
    return False


def main():
    """主函數：讀取 JSON 輸入，檢查檔案是否敏感，輸出結果"""
    try:
        # 從 stdin 讀取 UTF-8 編碼的 JSON 資料
        input_data = sys.stdin.buffer.read().decode('utf-8')
        
        # 解析 JSON
        try:
            data: Dict[str, Any] = json.loads(input_data)
        except json.JSONDecodeError as e:
            # JSON 解析失敗，輸出錯誤並允許讀取（避免阻擋使用者）
            result = {
                "permission": "allow",
                "user_message": f"JSON 解析錯誤: {str(e)}"
            }
            output = json.dumps(result, ensure_ascii=False)
            sys.stdout.buffer.write(output.encode('utf-8'))
            sys.stdout.buffer.flush()
            return
        
        # 取得檔案路徑
        file_path = data.get("file_path", "")
        
        if not file_path:
            # 沒有檔案路徑，允許讀取
            result = {"permission": "allow"}
            output = json.dumps(result, ensure_ascii=False)
            sys.stdout.buffer.write(output.encode('utf-8'))
            sys.stdout.buffer.flush()
            return
        
        # 從檔案路徑取得檔案名稱
        filename = get_filename_from_path(file_path)
        
        # 檢查是否為敏感檔案
        if is_sensitive_file(filename):
            # 是敏感檔案，拒絕讀取
            result = {
                "permission": "deny",
                "user_message": f"無法讀取敏感檔案：{filename}。此檔案包含敏感資訊，為保護您的資料安全，已阻止讀取。"
            }
        else:
            # 不是敏感檔案，允許讀取
            result = {"permission": "allow"}
        
        # 輸出 JSON 結果（使用 UTF-8 編碼）
        output = json.dumps(result, ensure_ascii=False)
        sys.stdout.buffer.write(output.encode('utf-8'))
        sys.stdout.buffer.flush()
        
    except Exception as e:
        # 發生未預期的錯誤，輸出錯誤訊息但允許讀取（避免阻擋使用者）
        result = {
            "permission": "allow",
            "user_message": f"檢查過程中發生錯誤: {str(e)}"
        }
        output = json.dumps(result, ensure_ascii=False)
        sys.stdout.buffer.write(output.encode('utf-8'))
        sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()

