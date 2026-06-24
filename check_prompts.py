from fzq_ai.utils.prompt_loader import load_prompt_template

paths = [
    "fzq_ai/prompts/zh/zh_multisource_merge.txt",
    "fzq_ai/prompts/zh/zh_opinion_landscape.txt",
    "fzq_ai/prompts/zh/zh_policy_brief.txt",
    "fzq_ai/prompts/zh/zh_risk_scan.txt",
]

for p in paths:
    print("\n===== ", p, " =====")
    print(load_prompt_template(p))
