# Bard Dotfiles

## Installation

#### Install with copy
 1. clone at your home directory to create the `~/dotfiles/` folder with configs
 1. copy the root level `.zshrc` and `.tmux.conf` files to your home directory at `~/`
   - Alternatively, usea symlink with `ln -s ~/dotfiles/{.zshrc,.zshrc_base,.tmux.conf} ~/`
 1. copy the folders in the `.config` folder to your config location at `~/.config/`
   - Alternatively, use a symlink with `ln -s `~/dotfiles/.config/* ~/.config/`

#### Dependencies
we rely on the following packages, `zsh neovim nvm tmux`
after installing `nvm` you may need to modify the source path in `~/.zshrc_base`


## Plugins

* [zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions): Searches your history while you type and provides suggestions.
* [zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting/tree/ad522a091429ba180c930f84b2a023b40de4dbcc): Provides fish style syntax highlighting for zsh.
* [ohmyzsh](https://github.com/robbyrussell/oh-my-zsh/tree/291e96dcd034750fbe7473482508c08833b168e3): Borrowed things like tab completion, fixing ls, tmux's vi-mode plugin.
* [vimode-zsh](https://github.com/robbyrussell/oh-my-zsh/tree/master/plugins/vi-mode) allows you to hit `esc` and navigate the current buffer using vim movement keys.

## Remapping
#### Vim
|key|function|
|---|--------|
| space | leader |
| j | left   |
| l | right  |
| h | up     |
| k | down   |


#### Tmux
|key|function|
|---|--------|
|C-t| Prefix |
| j | left   |
| l | right  |
| h | up     |
| k | down   |
| c | new window |
| v | new split window |
| j | previous window |
| l | next window |
| r | reload config |
