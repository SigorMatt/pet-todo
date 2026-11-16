<img src="https://img.shields.io/badge/High-634FD1?style=flat-square" height="20px" alt="Action required">

1\. A planted lock file can hang changes <code>🐞 Bug</code> <code>☼ Reliability</code>

<pre>
<b><i>_open_lock_file</i></b> retries a denied write-open with a blocking <b><i>O_RDONLY</i></b> open, which waits
indefinitely if the lock path is a FIFO with no writer. When another user plants such a FIFO in a
shared directory, every changing command stalls before <b><i>lock()</i></b> starts its five-second deadline.
</pre>


<details>
<summary><strong>Agent Prompt</strong></summary>

```
## Issue description
A FIFO at the lock pathname can block the read-only fallback indefinitely before the lock timeout starts.
## Fix Focus Areas
- todo/store.py[73-86]
- todo/store.py[102-113]
## Recommended Fix
Open lock candidates without blocking, reject non-regular lock files after opening, and add a regression test with a FIFO that has no writer.
```

<code>ⓘ Copy this prompt and use it to remediate the issue with your preferred AI generation tools</code>
</details>

[Dismiss ↗](https://app.qodo.ai/findings/112c7b1f-9aeb-43ed-8971-0e447ed1bf08?action=dismiss&origin=git) | [View ↗](https://app.qodo.ai/findings/112c7b1f-9aeb-43ed-8971-0e447ed1bf08)