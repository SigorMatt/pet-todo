<img src="https://img.shields.io/badge/Medium-634FD1?style=flat-square" height="20px" alt="Remediation recommended">

2\. Replacing a lock permits lost updates <code>🐞 Bug</code> <code>≡ Correctness</code>

<pre>
<b><i>_open_lock_file</i></b> opens the current lock pathname and <b><i>lock()</i></b> flocks that descriptor without
ensuring later writers will open the same inode. In a shared directory, an owner of a pre-planted
lock entry can replace it while one writer holds it, allowing a second writer to enter the
read–modify–write sequence under a different lock.
</pre>


<details>
<summary><strong>Agent Prompt</strong></summary>

```
## Issue description
Replacing an attacker-owned lock entry lets two writers flock different inodes while changing the same data file.
## Fix Focus Areas
- todo/store.py[41-47]
- todo/store.py[73-86]
- todo/store.py[102-108]
## Recommended Fix
Use a lock location whose directory entries cannot be replaced by another writer, and reject symlink or non-regular lock entries. Add a test that replaces a pre-planted lock entry while the first process holds its descriptor and verifies that the second cannot enter.
```

<code>ⓘ Copy this prompt and use it to remediate the issue with your preferred AI generation tools</code>
</details>

[Dismiss ↗](https://app.qodo.ai/findings/59f69001-47c8-46a0-b9bf-9a9e3e331962?action=dismiss&origin=git) | [View ↗](https://app.qodo.ai/findings/59f69001-47c8-46a0-b9bf-9a9e3e331962)