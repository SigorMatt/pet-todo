<h3>Code Review by Qodo</h3>

<code>🐞 Bugs (1)</code>  <code>📘 Rule violations (0)</code>  <code>📜 Skill insights (0)</code>

<img src="https://www.qodo.ai/wp-content/uploads/2025/11/light-grey-line.svg" height="10%" alt="Grey Divider">

<br/>

<img src="https://img.shields.io/badge/High-634FD1?style=flat-square" height="20px" alt="Action required">

<details>
<summary>  1.  <s>A planted lock file can hang changes</s> <code>✓ Resolved</code></summary>

<br/>

<p><b>Resolving commit:</b> <a href="https://github.com/SigorMatt/pet-todo/commit/e41f62234c5be2068e2e0698551abb3aed84fd25"><code>e41f622</code></a></p>

> <details>
><summary>Resolution reason</summary>
><br/>
>
><pre>
>Both lock-file opens use O_NONBLOCK, and non-regular lock files (such as a FIFO) are rejected via an
>fstat S_ISREG check and an OSError, so a planted FIFO can no longer hang a changing command before
>the 5 s deadline. Regression tests were added for the FIFO case.
></pre>
></details>

<!-- qodo-finding-reference
<code>↗ todo/store.py[R84]</code>
-->
> <details>
><summary>Description</summary>
><br/>
>
><pre>
><b><i>_open_lock_file</i></b> retries a denied write-open with a blocking <b><i>O_RDONLY</i></b> open, which waits
>indefinitely if the lock path is a FIFO with no writer. When another user plants such a FIFO in a
>shared directory, every changing command stalls before <b><i>lock()</i></b> starts its five-second deadline.
></pre>
></details>

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
> <code>[todo/store.py\[41-47\]](https://github.com/SigorMatt/pet-todo/blob/e41f62234c5be2068e2e0698551abb3aed84fd25/todo/store.py/#L41-L47)</code>
> <code>[todo/store.py\[73-84\]](https://github.com/SigorMatt/pet-todo/blob/e41f62234c5be2068e2e0698551abb3aed84fd25/todo/store.py/#L73-L84)</code>
> <code>[todo/store.py\[102-108\]](https://github.com/SigorMatt/pet-todo/blob/e41f62234c5be2068e2e0698551abb3aed84fd25/todo/store.py/#L102-L108)</code>
> <code>[todo/cli.py\[158-172\]](https://github.com/SigorMatt/pet-todo/blob/e41f62234c5be2068e2e0698551abb3aed84fd25/todo/cli.py/#L158-L172)</code>
> <code>[todo/store.py\[203-220\]](https://github.com/SigorMatt/pet-todo/blob/e41f62234c5be2068e2e0698551abb3aed84fd25/todo/store.py/#L203-L220)</code>
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
<summary>  3.  <s>Retargeted links can lose additions</s> <code>✓ Resolved</code></summary>

<br/>

<p><b>Resolving commit:</b> <a href="https://github.com/SigorMatt/pet-todo/commit/e41f62234c5be2068e2e0698551abb3aed84fd25"><code>e41f622</code></a></p>

> <details>
><summary>Resolution reason</summary>
><br/>
>
><pre>
>The diff adds store.resolve() and has each changing command in cli.py (_cmd_add, _cmd_done,
>_cmd_remove, _cmd_edit) resolve the path once, then pass that same target to store.lock(path,
>target=...), store.load(path, target=...) and store.save(path, data, target=...). The lock file, the
>read, and the replace all use the one resolved target, so a retarget mid-command can no longer make
>the command write a file other than the one whose lock it holds. A regression test
>(test_link_retargeted_after_the_lock_still_changes_the_locked_file) was also added to
>tests/test_cli.py.
></pre>
></details>

<!-- qodo-finding-reference
<code>↗ todo/store.py[R47]</code>
-->
> <details>
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


<!-- https://github.com/SigorMatt/pet-todo/commit/e41f62234c5be2068e2e0698551abb3aed84fd25 -->

<a href="https://www.qodo.ai"><img src="https://www.qodo.ai/wp-content/uploads/2025/03/qodo-logo.svg" width="80" alt="Qodo Logo"></a>