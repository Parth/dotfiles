# Awesome Dotfiles

Simple, but extensive customization of ZSH, TMUX, and NeoVim.

## Installation

Once the repo is cloned, execute the deploy script:

```shell
./deploy.sh
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

All default dotfiles (`.zshrc`, `~/.config/nvim`, etc) source something within the dotfiles repository. This helps separate changes that are synced across all your machines with system-specific changes.

Upon launching a new shell, the first thing that's evaluated is `zshrc_manager.sh`. This script first launches tmux. Then once zsh logs in, within tmux, it updates the dotfiles repository, and sources the changes.

## [Zsh](https://en.wikipedia.org/wiki/Z_shell)

- `cd` has been reassigned to `cd` and `ls`. Every time you navigate to a new directory, it will display the content of that directory.

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

### Plugins

- [zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions): Searches your history while you type and provides suggestions.
- [zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting/tree/ad522a091429ba180c930f84b2a023b40de4dbcc): Provides fish style syntax highlighting for zsh.
- [ohmyzsh](https://github.com/robbyrussell/oh-my-zsh/tree/291e96dcd034750fbe7473482508c08833b168e3): Borrowed things like tab completion, fixing ls, tmux's vi-mode plugin.

## [Tmux](https://en.wikipedia.org/wiki/Tmux)


## [Dir-color](http://manpages.ubuntu.com/manpages/xenial/man5/dir_colors.5.html)
- The color is located in `.dir_colors`. You can change it to dir-colors you want. The default is Zenburn.


- Ctrl-B has been remapped to the backtick character (&#96;). If you want to type the actual backtick character (&#96;) itself, just hit the key twice.
- `%` has been remapped to `v`.
- Use vim movement keys for moving between panes.
- Copy buffer is copied to xclip.
- Status bar tells you date, time, user, and hostname. Especially useful with nested ssh sessions.