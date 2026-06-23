import os
import re

ROOT = "src"  # 你的代码根目录

pattern = re.compile(r"datetime\.utcnow\(\)")

for folder, _, files in os.walk(ROOT):
    for file in files:
        if not file.endswith(".py"):
            continue

        path = os.path.join(folder, file)

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        if "datetime.utcnow()" not in content:
            continue

        print(f"Fixing: {path}")

        # 替换 utcnow
        new_content = content.replace(
            "datetime.utcnow()",
            "datetime.now(timezone.utc)"
        )

        # 如果缺少 timezone import，则自动添加
        if "timezone" not in new_content:
            new_content = new_content.replace(
                "from datetime import datetime",
                "from datetime import datetime, timezone"
            )

        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)

print("All datetime.utcnow() replaced.")
