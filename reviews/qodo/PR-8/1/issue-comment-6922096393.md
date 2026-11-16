<h3>Code Review by Qodo</h3>

<code>🐞 Bugs (3)</code>  <code>📘 Rule violations (0)</code>  <code>📜 Skill insights (0)</code>

<img src="https://www.qodo.ai/wp-content/uploads/2025/11/light-grey-line.svg" height="10%" alt="Grey Divider">

<br/>

<img src="https://img.shields.io/badge/High-634FD1?style=flat-square" height="20px" alt="Action required">

<details>
<summary>  1.  A planted lock file can hang changes <code>🐞 Bug</code> <code>☼ Reliability</code></summary>

<br/>

> <details open>
><summary>Description</summary>
><br/>
>
><pre>
><b><i>_open_lock_file</i></b> retries a denied write-open with a blocking <b><i>O_RDONLY</i></b> open, which waits
>indefinitely if the lock path is a FIFO with no writer. When another user plants such a FIFO in a
>shared directory, every changing command stalls before <b><i>lock()</i></b> starts its five-second deadline.
></pre>
></details>

> <details>
><summary>Code</summary>
><br/>
>
><code>[todo/store.py[84]](https://github.com/SigorMatt/pet-todo/pull/8/files#diff-c7564f4bdfa07c8b5636c79fe9d89296b821f29291202a86bd6bae6f741ccdcfR84-R84)</code>
>
>```diff
>+            return os.open(name, os.O_RDONLY | os.O_CLOEXEC)
>```
></details>

> <details>
><summary>Evidence</summary>
><br/>
>
><pre>
>The fallback lacks <b><i>O_NONBLOCK</i></b>, and the deadline is computed only after <b><i>_open_lock_file</i></b> returns.
>The added scoped review records a reproduced 15-second timeout of a command using a planted FIFO.
></pre>
>
> <code>[todo/store.py\[73-86\]](https://github.com/SigorMatt/pet-todo/blob/f3e4b8ac7d2a77f06ce9c1093325c94690d184a5/todo/store.py/#L73-L86)</code>
> <code>[todo/store.py\[102-113\]](https://github.com/SigorMatt/pet-todo/blob/f3e4b8ac7d2a77f06ce9c1093325c94690d184a5/todo/store.py/#L102-L113)</code>
> <code>[reviews/cold/M6/scoped-1.md\[8-11\]](https://github.com/SigorMatt/pet-todo/blob/f3e4b8ac7d2a77f06ce9c1093325c94690d184a5/reviews/cold/M6/scoped-1.md/#L8-L11)</code>
></details>

> <details>
><summary>Agent prompt</summary>
><br/>
>
>```
>The issue below was found during a code review. Follow the provided context and guidance below and implement a solution
>
>## Issue description
>A FIFO at the lock pathname can block the read-only fallback indefinitely before the lock timeout starts.
>## Fix Focus Areas
>- todo/store.py[73-86]
>- todo/store.py[102-113]
>## Recommended Fix
>Open lock candidates without blocking, reject non-regular lock files after opening, and add a regression test with a FIFO that has no writer.
>```
> <code>ⓘ Copy this prompt and use it to remediate the issue with your preferred AI generation tools</code>
></details>

[Dismiss ↗](https://app.qodo.ai/findings/112c7b1f-9aeb-43ed-8971-0e447ed1bf08?action=dismiss&origin=git) | [View ↗](https://app.qodo.ai/findings/112c7b1f-9aeb-43ed-8971-0e447ed1bf08)

<hr/>
</details>


<br/>

<img src="https://img.shields.io/badge/Medium-634FD1?style=flat-square" height="20px" alt="Remediation recommended">

<details>
<summary>  2.  Replacing a lock permits lost updates <code>🐞 Bug</code> <code>≡ Correctness</code></summary>

<br/>

> <details open>
><summary>Description</summary>
><br/>
>
><pre>
><b><i>_open_lock_file</i></b> opens the current lock pathname and <b><i>lock()</i></b> flocks that descriptor without
>ensuring later writers will open the same inode. In a shared directory, an owner of a pre-planted
>lock entry can replace it while one writer holds it, allowing a second writer to enter the
>read–modify–write sequence under a different lock.
></pre>
></details>

> <details>
><summary>Code</summary>
><br/>
>
><code>[todo/store.py[81]](https://github.com/SigorMatt/pet-todo/pull/8/files#diff-c7564f4bdfa07c8b5636c79fe9d89296b821f29291202a86bd6bae6f741ccdcfR81-R81)</code>
>
>```diff
>+        return os.open(name, os.O_RDWR | os.O_CREAT | os.O_CLOEXEC, 0o666)
>```
></details>

> <details>
><summary>Evidence</summary>
><br/>
>
><pre>
>Only the data path is resolved; the appended <b><i>.lock</i></b> entry is opened afresh for each invocation, and
><b><i>flock</i></b> applies to the inode returned by that open. Replacing an attacker-owned entry between opens
>therefore gives the writers distinct lock inodes, while both commands still load and replace the
>same data pathname.
></pre>
>
> <code>[todo/store.py\[41-47\]](https://github.com/SigorMatt/pet-todo/blob/f3e4b8ac7d2a77f06ce9c1093325c94690d184a5/todo/store.py/#L41-L47)</code>
> <code>[todo/store.py\[73-84\]](https://github.com/SigorMatt/pet-todo/blob/f3e4b8ac7d2a77f06ce9c1093325c94690d184a5/todo/store.py/#L73-L84)</code>
> <code>[todo/store.py\[102-108\]](https://github.com/SigorMatt/pet-todo/blob/f3e4b8ac7d2a77f06ce9c1093325c94690d184a5/todo/store.py/#L102-L108)</code>
> <code>[todo/cli.py\[158-172\]](https://github.com/SigorMatt/pet-todo/blob/f3e4b8ac7d2a77f06ce9c1093325c94690d184a5/todo/cli.py/#L158-L172)</code>
> <code>[todo/store.py\[203-220\]](https://github.com/SigorMatt/pet-todo/blob/f3e4b8ac7d2a77f06ce9c1093325c94690d184a5/todo/store.py/#L203-L220)</code>
></details>

> <details>
><summary>Agent prompt</summary>
><br/>
>
>```
>The issue below was found during a code review. Follow the provided context and guidance below and implement a solution
>
>## Issue description
>Replacing an attacker-owned lock entry lets two writers flock different inodes while changing the same data file.
>## Fix Focus Areas
>- todo/store.py[41-47]
>- todo/store.py[73-86]
>- todo/store.py[102-108]
>## Recommended Fix
>Use a lock location whose directory entries cannot be replaced by another writer, and reject symlink or non-regular lock entries. Add a test that replaces a pre-planted lock entry while the first process holds its descriptor and verifies that the second cannot enter.
>```
> <code>ⓘ Copy this prompt and use it to remediate the issue with your preferred AI generation tools</code>
></details>

[Dismiss ↗](https://app.qodo.ai/findings/59f69001-47c8-46a0-b9bf-9a9e3e331962?action=dismiss&origin=git) | [View ↗](https://app.qodo.ai/findings/59f69001-47c8-46a0-b9bf-9a9e3e331962)

<hr/>
</details>


<details>
<summary>  3.  Retargeted links can lose additions <code>🐞 Bug</code> <code>≡ Correctness</code></summary>

<br/>

> <details open>
><summary>Description</summary>
><br/>
>
><pre>
><b><i>lock_path()</i></b> resolves the data symlink when acquiring the lock, but <b><i>_cmd_add</i></b> passes the original
>path to <b><i>load()</i></b> and <b><i>save()</i></b>, which resolve it again later. If the link changes from target A to
>target B during a command, that command can modify B while holding A&#x27;s lock, alongside a writer
>holding B&#x27;s lock.
></pre>
></details>

> <details>
><summary>Code</summary>
><br/>
>
><code>[todo/store.py[47]](https://github.com/SigorMatt/pet-todo/pull/8/files#diff-c7564f4bdfa07c8b5636c79fe9d89296b821f29291202a86bd6bae6f741ccdcfR47-R47)</code>
>
>```diff
>+    return os.path.realpath(path) + ".lock"
>```
></details>

> <details>
><summary>Evidence</summary>
><br/>
>
><pre>
>The new lock key is a point-in-time <b><i>realpath</i></b>, whereas the changed command block retains the
>original pathname. <b><i>load()</i></b> opens that pathname and <b><i>save()</i></b> independently resolves it again before
>replacement, so neither operation is bound to the target whose lock was acquired.
></pre>
>
> <code>[todo/store.py\[41-47\]](https://github.com/SigorMatt/pet-todo/blob/f3e4b8ac7d2a77f06ce9c1093325c94690d184a5/todo/store.py/#L41-L47)</code>
> <code>[todo/cli.py\[158-171\]](https://github.com/SigorMatt/pet-todo/blob/f3e4b8ac7d2a77f06ce9c1093325c94690d184a5/todo/cli.py/#L158-L171)</code>
> <code>[todo/store.py\[124-135\]](https://github.com/SigorMatt/pet-todo/blob/f3e4b8ac7d2a77f06ce9c1093325c94690d184a5/todo/store.py/#L124-L135)</code>
> <code>[todo/store.py\[203-220\]](https://github.com/SigorMatt/pet-todo/blob/f3e4b8ac7d2a77f06ce9c1093325c94690d184a5/todo/store.py/#L203-L220)</code>
></details>

> <details>
><summary>Agent prompt</summary>
><br/>
>
>```
>The issue below was found during a code review. Follow the provided context and guidance below and implement a solution
>
>## Issue description
>The lock key and the data read/write target can differ when a symlink changes during a command.
>## Fix Focus Areas
>- todo/store.py[41-47]
>- todo/cli.py[161-171]
>- todo/cli.py[196-223]
>## Recommended Fix
>Resolve the data target once for each changing command, then use that same target for lock acquisition, loading and saving. Add a test that retargets the symlink after lock acquisition and checks that the command does not write the newly selected target under the old target's lock.
>```
> <code>ⓘ Copy this prompt and use it to remediate the issue with your preferred AI generation tools</code>
></details>

[Dismiss ↗](https://app.qodo.ai/findings/ebdd2f04-6d0a-48d7-82e5-3d271bbde6e6?action=dismiss&origin=git) | [View ↗](https://app.qodo.ai/findings/ebdd2f04-6d0a-48d7-82e5-3d271bbde6e6)

<hr/>
</details>



<img src="https://www.qodo.ai/wp-content/uploads/2025/11/light-grey-line.svg" height="10%" alt="Grey Divider">

<!-- qodo-self-review-slot -->


<!-- qodo-context:start -->
<details><summary><strong>Context sources</strong></summary>

<div>&#x2705; Context preparation</div>
<div>&nbsp;&nbsp;Commit messages: summarized; full text retained for this review</div>
<div>Review mode: <code>Auto: ⚖️ Balanced</code>: Downgraded extended -&gt; standard: change is below the extended eligibility bar (hunks 15/18, lines 741/200; both must reach the floor). Router rationale: Locking changes span multiple commands and subtle filesystem failure paths.</div>
<!-- qodo-context:end -->
</details>

<img src="https://www.qodo.ai/wp-content/uploads/2025/11/light-grey-line.svg" height="10%" alt="Grey Divider">



<!-- qodo-daily-tip:start -->

<details>
<summary><strong>Tip of the day</strong></summary>

<br/>

<pre>💡 Did you know, you can choose which labels appear on a finding, and whether they show icons or text</pre>

<a href="https://docs.qodo.ai/tips-and-tricks">More tips ↗</a> | <a href="https://app.qodo.ai/configurations?tab=display-preferences">Customize Qodo ↗</a> | <a href="https://docs.qodo.ai">Qodo docs ↗</a>

</details>

<img src="https://www.qodo.ai/wp-content/uploads/2025/11/light-grey-line.svg" height="10%" alt="Grey Divider">
<!-- qodo-daily-tip:end -->


<!-- https://github.com/SigorMatt/pet-todo/commit/f3e4b8ac7d2a77f06ce9c1093325c94690d184a5 -->

<a href="https://www.qodo.ai"><img src="https://www.qodo.ai/wp-content/uploads/2025/03/qodo-logo.svg" width="80" alt="Qodo Logo"></a>