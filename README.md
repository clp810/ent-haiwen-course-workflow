# ENT Haiwen Course Workflow

这是一个供小组共同维护的课程交付工作流仓库。它把每周课件分析、问题澄清、`WEEK_HANDOFF.md`、Weekly Log、Coursework Pack 和 FINAL 确认拆成可追溯的步骤，同时默认不把真实课程资料、成员信息、访谈原始材料或提交文件放入 Git。

仓库当前只提供 repo-scoped Skills，不是 Codex Plugin。等两个 Skill 经多周反馈稳定、并且确实需要跨仓库安装时，再评估 Plugin。

## 快速开始

1. 克隆仓库，并在仓库根目录打开 Codex。
2. 复制 `course/COURSE_PROFILE.example.md` 为 `course/COURSE_PROFILE.local.md`，在本地填写课程、团队、导师和共享链接。该文件不会被 Git 跟踪。
3. 把当周课件放入 `course/weeks/<week-id>/`，例如 `course/weeks/S1_W03/`。原始课件目录默认被忽略。
4. 显式调用 `$course-weekly-delivery`，说明周次和目标阶段，例如：

   ```text
   Use $course-weekly-delivery for S1_W03. Analyze the local materials and prepare the handoff questions.
   ```

5. 第一次运行只分析材料并提出最多 6 个高信息量问题，不创建提交文件。回答后，工作流在本地创建紧凑的 `course/deliverables/<week-id>/WEEK_HANDOFF.md`。
6. 信息足够时生成或更新唯一一份 DRAFT。只有在成员明确确认团队审阅、证据可追溯且合乎伦理、AI 使用已人工核验后，才能生成版本化 FINAL。

讨论与复核默认使用中文；课程提交文件默认使用英文，但课程明确要求其他语言时以课程要求为准。

## 工作流

```text
local weekly materials
        ↓
course-analysis-companion
requirements + locators + unknowns
        ↓  up to 6 grouped questions
WEEK_HANDOFF.md
        ↓
course-weekly-delivery
Weekly Log + Coursework Pack + optional link wrapper
        ↓  explicit confirmation only
versioned FINAL
```

`course-analysis-companion` 负责读取当周材料、区分明确要求与建议，并形成可追溯交接。`course-weekly-delivery` 负责持久化本周状态、调用确定性脚本、维护单一 DRAFT 和 FINAL 门禁。

## 仓库结构

```text
.agents/skills/                  repo-scoped Skills
course/
  COURSE_PROFILE.example.md     可提交的空白配置示例
  templates/                    获准提交且已清除个人元数据的课程模板
  weeks/                        本地原始课件，默认忽略
  deliverables/                 本地 handoff、DRAFT、FINAL，默认忽略
docs/
  HAIWEN_PROJECT_CONTEXT.md      净化后的项目背景
  PRIVACY_AND_EVIDENCE.md       隐私、证据与提交边界
scripts/                        测试、审计和 Skill 校验入口
tests/                          完全虚构的最小测试夹具与回归测试
```

## 模板与脚本

`course/templates/ENT303TC_Weekly_Checkpoint_Template.xlsx` 是经确认可放入仓库的课程模板副本。仓库版本清除了 Office 作者元数据，没有填入团队、导师或提交内容。

交付 Skill 使用三个确定性脚本：

- `patch_weekly_log.py`：只允许修改 `A Student Weekly!B6:B24`、`D1 Evidence Register!B6:G105`、`D2 AI Use!A6:G105`、`Lists!B6:B35`，并完整保护导师与加速门槛工作表；
- `build_coursework_docx.py`：从小型 JSON 规范生成一致的 DOCX；
- `validate_delivery.py`：检查 DRAFT/FINAL 文件名、静态核心必填项、声明、受保护工作表，以及 FINAL 全可编辑区中的未完成标记。

## 验证

在提交变更前运行：

```bash
./scripts/test.sh
./scripts/validate_skills.sh
python3 scripts/audit_repository.py
```

`validate_skills.sh` 会使用本机 Codex 的 `$skill-creator` 官方 `quick_validate.py`。CI 运行脚本回归测试和仓库隐私审计。

## 反馈

使用 GitHub Issues 的 “Skill feedback” 模板提交反馈。只描述可复现的工作流问题和经过净化的最小示例，不粘贴真实课件、学生姓名、导师信息、共享链接、访谈原文或提交文件。详见 `CONTRIBUTING.md`。
