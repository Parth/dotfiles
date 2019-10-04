# Awesome Dotfiles

Simple, but extensive customization of ZSH, TMUX, and Vim.

[![VideoWalkthrough](https://img.youtube.com/vi/UgDz_9i2nwc/0.jpg)](https://www.youtube.com/watch?v=UgDz_9i2nwc)

## Setup Options

There are 3 ways in which you can use this, depending on how much you think you'll be customizing.

One of the key features is that this implementation stays in sync across all your machines. So depending on how much you'd like to customize your configuration, you have a few options:

- Little Customization: Just clone this repo and jump to [Installation](#installation).
- Mild Customization: [Fork]() this repo, and clone your own fork. Keep an eye on this repo for bugfixes and other improvements that you'd like to incorporate into your fork. Then jump to [Installation](#installation).
- Most Customization: Building your own dotfiles from scratch! Read through these docs, watch the video above, star this repo, and create your own dotfiles! You can add this repository as a [git module](https://git-scm.com/book/en/v2/Git-Tools-Submodules) and source the parts you like.

If you're unsure, just read the docs, watch the video, clone this repository, and jump to [Installation](#installation).

## Installation

Once the repo is cloned, execute the deploy script:

```shell
./deploy
```

This script guides you through the following:

1. Checks to see if you have zsh, tmux, and vim installed.
2. Installs them using your default package manager if you don't have some of them installed.
3. Checks to see if your default shell is zsh.
4. Sets zsh to your default shell.
5. Backs up your old configuration files.

Pretty convenient for configuring new servers.

## **Summary of Changes**

## Basic runtime operations

All default dotfiles (`.zshrc`, `.vimrc`, etc) source something within the dotfiles repository. This helps separate changes that are synced across all your machines with system-specific changes.

Upon launching a new shell, the first thing that's evaluated is `zshrc_manager.sh`. This script first launches tmux. Then once zsh logs in, within tmux, it updates the dotfiles repository, and sources the changes.

## [Zsh](https://en.wikipedia.org/wiki/Z_shell)

- `cd` has been reassigned to `cd` and `ls`. Every time you navigate to a new directory, it will display the content of that directory.
- `v` has been aliased too: `vim -p`. This lets you open multiple files in vim as tabs.

### Prompt

The prompt takes on the form:

```shell
[plugin, plugin, ...]:
```

Each plugin is sensitive to where you are and what you're doing, they reveal themselves when it's contextually relevant. Plugins include:

- `PWD plugin`: always present, tells you where you are. Always the first plugin.
- `Status code plugin`: appears anytime a program returns with a non-zero status code. Tells you what status code the program completed with.
- `Git plugin`: appears when you're in a git repository. Tells you what branch you're on, and how many files have been changed since the last commit.
- `Sudo plugin`: tells you when you can sudo without a password. Or when you're logged in as root.
- `Time plugin`: appears when a program took more than 1s to execute. Tells you how long it took to execute.
- `PID plugin`: appears when you background a task. Tells you what the PID of the task is.

### Keybindings

| Key Stroke | What It Does                                                                              |
| ---------- | ------------------------------------------------------------------------------------------|
| Ctrl-H     | Goes to the root of a git project, runs `cd $(git rev-parse --show-toplevel || echo ".")` |
| Ctrl-K     | Runs `cd ..`                                                                              |
| Ctrl-G     | Runs `git add -A; git commit -v && git push`                                              |
| Ctrl-V     | Runs `fc`. Takes last command and puts it in a vim buffer.                                |
| Ctrl-S     | Adds `sudo` to the beginning of the buffer.                                               |
| Ctrl-L     | Runs `ls`.                                                                                |
| Ctrl-O     | Equivalent to hitting `Enter`.                                                            |
| Ctrl-P     | Equivalent to pressing `Up Arrow`.                                                        |

### Plugins

- [zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions): Searches your history while you type and provides suggestions.
- [zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting/tree/ad522a091429ba180c930f84b2a023b40de4dbcc): Provides fish style syntax highlighting for zsh.
- [ohmyzsh](https://github.com/robbyrussell/oh-my-zsh/tree/291e96dcd034750fbe7473482508c08833b168e3): Borrowed things like tab completion, fixing ls, tmux's vi-mode plugin.
- [vimode-zsh](https://github.com/robbyrussell/oh-my-zsh/tree/master/plugins/vi-mode) allows you to hit `esc` and navigate the current buffer using vim movement keys.

## [Vim](<https://en.wikipedia.org/wiki/Vim_(text_editor)>)

- Leader key has been remapped to `,`

## [Tmux](https://en.wikipedia.org/wiki/Tmux)

- Ctrl-B has been remapped to the backtick character (&#96;). If you want to type the actual backtick character (&#96;) itself, just hit the key twice.
- `%` has been remapped to `v`.
- Use vim movement keys for moving between panes.
- Copy buffer is copied to xclip.
- Status bar tells you date, time, user, and hostname. Especially useful with nested ssh sessions.
