"""修复现有提交记录中因 secure_filename 导致的文件名缺失问题"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from app import create_app
from extensions import db
from models.submission import Submission

STAGE_LABELS = {
    'draft': '初稿', 'round1': '一轮修改', 'round2': '二轮修改',
    'round3': '三轮修改', 'final_check': '查重定稿', 'final': '最终版',
}

def has_chinese(text):
    return any('\u4e00' <= c <= '\u9fff' for c in text)

def fix():
    app = create_app()
    with app.app_context():
        subs = Submission.query.all()
        fixed = 0
        for sub in subs:
            if has_chinese(sub.file_name):
                continue
            ext = Path(sub.file_name).suffix or '.pdf'
            label = STAGE_LABELS.get(sub.submission_type, sub.submission_type)
            new_name = f'{label}_v{sub.version}{ext}'
            if new_name != sub.file_name:
                print(f'  [{sub.id}] {sub.file_name!r} -> {new_name!r}')
                sub.file_name = new_name
                fixed += 1
        db.session.commit()
        print(f'\n共修复 {fixed} 条记录')

if __name__ == '__main__':
    fix()
