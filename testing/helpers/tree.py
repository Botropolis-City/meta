import os
import shutil
import subprocess
import tempfile

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))


def check_docs(tree):
    return subprocess.run([os.path.join(tree, 'tools', 'check-docs')],
                          capture_output=True, text=True, cwd=tree)


def copy_tree():
    """Copy this repository's files, tracked or not yet, into a fresh directory.

    Ignored files stay behind, so the children and their worktrees never come
    along. The copy is not a git checkout.
    """
    tree = tempfile.mkdtemp()
    files = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard'],
                           capture_output=True, text=True, cwd=ROOT, check=True).stdout.split('\n')
    for f in filter(None, files):
        src = os.path.join(ROOT, f)
        if not os.path.isfile(src):
            continue
        dst = os.path.join(tree, f)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    return tree


def remove_tree(tree):
    shutil.rmtree(tree)
