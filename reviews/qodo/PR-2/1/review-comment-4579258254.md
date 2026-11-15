<img src="https://img.shields.io/badge/Medium-634FD1?style=flat-square" height="20px" alt="Remediation recommended">

3\. One task can make every list fail <code>🐞 Bug</code> <code>☼ Reliability</code>

<pre>
<b><i>add</i></b> stores argument text unchanged, while <b><i>_cmd_list</i></b> prints it without handling an encoding
failure. When an argument contains undecodable bytes represented as surrogate characters and stdout
uses strict UTF-8, subsequent lists raise <b><i>UnicodeEncodeError</i></b> instead of returning a CLI error.
</pre>


<details>
<summary><strong>Agent Prompt</strong></summary>

```
## Issue description
Text accepted by add can later make list crash on strict UTF-8 stdout.
## Fix Focus Areas
- todo/cli.py[38-55]
- todo/store.py[40-46]
## Recommended Fix
Choose a consistent policy for surrogate-containing text: reject it before saving or encode it into a printable representation. Apply that policy when loading existing files too, so a previously stored item cannot crash list.
```

<code>ⓘ Copy this prompt and use it to remediate the issue with your preferred AI generation tools</code>
</details>

[Dismiss ↗](https://app.qodo.ai/findings/a303a4f3-157b-466f-ba2a-349f4acb6f39?action=dismiss&origin=git) | [View ↗](https://app.qodo.ai/findings/a303a4f3-157b-466f-ba2a-349f4acb6f39)