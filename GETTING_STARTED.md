# OpenStudio · China–ASEAN — practical guide / 使用导读

[Project README](README.md) · [Detailed project record](https://github.com/YucongDuan/YucongDuan/blob/main/projects/1373871217.md) · [Research portfolio](https://github.com/YucongDuan)

Learn with 12 Chinese/English/Vietnamese modules, four semantic labs and a portable student project.

通过中英越三语12个模块、四类语义实验和可导出作品学习与创新。

## First result / 第一个结果

Open the offline HTML after downloading the repository. For accounts and courses, run `python server.py` and visit `http://127.0.0.1:8765`.

下载解压后打开离线HTML；账户与课程功能可运行`python server.py`，访问`http://127.0.0.1:8765`。

[Inspect the entry file / 查看入口文件](OpenStudio_Offline.html)

```bash
python scripts/check_release.py
```

Run from the project root after downloading and extracting the source. For a ZIP-distributed project, enter the inner project directory first. Commands using `PYTHONPATH=src` use POSIX shell syntax; PowerShell users can set `$env:PYTHONPATH='src'` before the Python command.

下载解压后在项目根目录运行；以ZIP分发的项目先进入包内项目目录。含`PYTHONPATH=src`的命令使用POSIX语法，PowerShell可先设置`$env:PYTHONPATH='src'`。

## Inspect what changed / 检查变化

Keep one input and its assumptions, run the documented example, then change one condition and compare the actual output. Preserve both successful and unsuccessful results. Use the README's dependency and test instructions for full verification.

保留输入及其假设，运行文档示例，再改变一个条件并比较实际输出。成功与失败结果都应保留；完整验证按README中的依赖和测试说明执行。

## Next contribution / 下一步贡献

Change one lab assumption and export both results. / 改变一项实验假设，导出并比较两次结果。

A useful public report includes the exact revision, environment, command, minimal input, expected result and observed result. Keep private data out of public examples.

公开报告应包含确切版本、环境、命令、最小输入、预期结果与实际结果。公开示例应去除私人数据。

## Research and collaboration / 研究与合作

[Written collaboration guide](https://github.com/YucongDuan/YucongDuan/blob/main/COLLABORATE.md) · [Citation guide](https://github.com/YucongDuan/YucongDuan/blob/main/CITING.md)

Choose a question, a data scope, a source revision, responsible people, a license and an inspectable deliverable. The project's original implementation scope, author notices and component licenses remain in its README and source.

合作请明确问题、数据范围、源码版本、责任人、许可与可审阅的交付物。项目实现范围、作者声明和组件许可见原README与源码。

Research basis: Yucong Duan (段玉聪). Guide updated 17 September 2026.
