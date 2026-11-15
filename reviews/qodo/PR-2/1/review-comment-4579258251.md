<img src="https://img.shields.io/badge/Medium-634FD1?style=flat-square" height="20px" alt="Remediation recommended">

2\. Edited lists can reuse or reverse ids <code>🐞 Bug</code> <code>≡ Correctness</code>

<pre>
<b><i>_valid</i></b> accepts nonpositive IDs and a <b><i>next_id</i></b> that is no greater than an existing item&#x27;s ID. If a
list has been hand-edited or merged into that state, <b><i>_cmd_add</i></b> uses the inconsistent value
directly, producing duplicate or negative IDs.
</pre>


<details>
<summary><strong>Agent Prompt</strong></summary>

```
## Issue description
An accepted list can assign an already-used or negative ID to the next item.
## Fix Focus Areas
- todo/store.py[40-56]
- todo/cli.py[38-42]
## Recommended Fix
Require positive, unique item IDs and a positive next_id greater than every stored ID when loading the file. Report inconsistent state through StoreError rather than allocating an ambiguous ID.
```

<code>ⓘ Copy this prompt and use it to remediate the issue with your preferred AI generation tools</code>
</details>

[Dismiss ↗](https://app.qodo.ai/findings/5c9955ce-1135-429c-bf26-cf8a0218fe2d?action=dismiss&origin=git) | [View ↗](https://app.qodo.ai/findings/5c9955ce-1135-429c-bf26-cf8a0218fe2d)