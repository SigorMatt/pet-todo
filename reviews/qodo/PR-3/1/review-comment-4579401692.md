<img src="https://img.shields.io/badge/Medium-634FD1?style=flat-square" height="20px" alt="Remediation recommended">

2\. Large stored ids make edits crash <code>🐞 Bug</code> <code>☼ Reliability</code>

<pre>
<b><i>load</i></b> repairs <b><i>next_id</i></b> by adding one to the largest stored ID without checking whether that result
can be serialized. If a hand-edited file contains a valid 4,300-digit item ID and a smaller
<b><i>next_id</i></b>, the repaired counter has 4,301 digits; subsequent <b><i>add</i></b>, <b><i>done</i></b>, or <b><i>remove</i></b> saves raise
an uncaught <b><i>ValueError</i></b> during JSON serialization.
</pre>


<details>
<summary><strong>Agent Prompt</strong></summary>

```
## Issue description
Repairing `next_id` from a maximum-length JSON integer can produce an integer that `json.dump` cannot serialize, causing mutating commands to crash.
## Fix Focus Areas
- todo/store.py[25-34]
- todo/store.py[37-39]
- tests/test_store.py[101-130]
## Recommended Fix
Detect a repaired counter that cannot be serialized and report it as a store error before a mutating command attempts to save. Add a test with a maximum-length stored ID and a low `next_id`.
```

<code>ⓘ Copy this prompt and use it to remediate the issue with your preferred AI generation tools</code>
</details>

[Dismiss ↗](https://app.qodo.ai/findings/17fac267-76e2-4a35-9537-e4e54baacb97?action=dismiss&origin=git) | [View ↗](https://app.qodo.ai/findings/17fac267-76e2-4a35-9537-e4e54baacb97)