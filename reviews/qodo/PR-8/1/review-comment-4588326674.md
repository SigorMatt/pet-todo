<img src="https://img.shields.io/badge/Medium-634FD1?style=flat-square" height="20px" alt="Remediation recommended">

3\. Retargeted links can lose additions <code>🐞 Bug</code> <code>≡ Correctness</code>

<pre>
<b><i>lock_path()</i></b> resolves the data symlink when acquiring the lock, but <b><i>_cmd_add</i></b> passes the original
path to <b><i>load()</i></b> and <b><i>save()</i></b>, which resolve it again later. If the link changes from target A to
target B during a command, that command can modify B while holding A&#x27;s lock, alongside a writer
holding B&#x27;s lock.
</pre>


<details>
<summary><strong>Agent Prompt</strong></summary>

```
## Issue description
The lock key and the data read/write target can differ when a symlink changes during a command.
## Fix Focus Areas
- todo/store.py[41-47]
- todo/cli.py[161-171]
- todo/cli.py[196-223]
## Recommended Fix
Resolve the data target once for each changing command, then use that same target for lock acquisition, loading and saving. Add a test that retargets the symlink after lock acquisition and checks that the command does not write the newly selected target under the old target's lock.
```

<code>ⓘ Copy this prompt and use it to remediate the issue with your preferred AI generation tools</code>
</details>

[Dismiss ↗](https://app.qodo.ai/findings/ebdd2f04-6d0a-48d7-82e5-3d271bbde6e6?action=dismiss&origin=git) | [View ↗](https://app.qodo.ai/findings/ebdd2f04-6d0a-48d7-82e5-3d271bbde6e6)