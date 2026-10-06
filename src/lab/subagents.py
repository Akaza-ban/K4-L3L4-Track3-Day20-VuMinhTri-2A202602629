"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Delegate to this subagent to explore files, inspect project structure, read README, "
                "docstrings, code, and sample data. Reports findings objectively without modifying any files."
            ),
            "system_prompt": (
                "You are an exploration subagent. Your job is to inspect files, read instructions, docstrings, "
                "and data samples. Report facts clearly and concisely. Never create or edit any files."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Delegate to this subagent to implement code changes, create files, clean data, "
                "or run scripts and tests. Reports what was modified and command execution outcomes."
            ),
            "system_prompt": (
                "You are an implementation subagent. Your job is to make required code changes, write or update "
                "files, and execute tests or scripts to verify your modifications. Report what you changed and test results."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Delegate to this subagent for independent verification. Checks solutions against requirements, "
                "edge cases, and rules before finalizing. Never modifies files."
            ),
            "system_prompt": (
                "You are a reviewer subagent. Your job is to independently inspect the workspace against task requirements "
                "and rules. Run verification checks or review code and data outputs. Do not modify files."
            ),
        },
    ]
