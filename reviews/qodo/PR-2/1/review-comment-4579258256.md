<img src="https://img.shields.io/badge/Medium-634FD1?style=flat-square" height="20px" alt="Remediation recommended">

4\. Task text can impersonate list entries <code>🐞 Bug</code> <code>≡ Correctness</code>

<pre>
<b><i>_cmd_add</i></b> saves text containing newlines, and <b><i>_cmd_list</i></b> inserts that text directly into its
one-line item format. An argument containing a newline and a fabricated ID therefore makes one
stored item appear as multiple entries, including an entry that was never added.
</pre>


<details>
<summary><strong>Agent Prompt</strong></summary>

```
## Issue description
Embedded newlines allow a task's text to masquerade as additional list entries.
## Fix Focus Areas
- todo/cli.py[38-55]
## Recommended Fix
Define whether multiline input is rejected or displayed with escaped line breaks. Enforce that choice on add and on list output from existing files so each displayed item remains unambiguous.
```

<code>ⓘ Copy this prompt and use it to remediate the issue with your preferred AI generation tools</code>
</details>

[Dismiss ↗](https://app.qodo.ai/findings/ade66514-5e6a-498e-b515-edb5bb3d47c2?action=dismiss&origin=git) | [View ↗](https://app.qodo.ai/findings/ade66514-5e6a-498e-b515-edb5bb3d47c2)