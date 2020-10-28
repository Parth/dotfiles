#  vim / neoVim config

* How to use config from `/dotfile` folder?
* Neovim is heavier than vim

```bash
apt show  vim neovim | grep -i size
```

* `after` folder, add these configs to already loaded configs
* `set path=.,**` to make `:find` work seamlessly within project
* [x] include search
* [ ] [GNU stow](https://www.gnu.org/software/stow/) symlinks factory program
  * Manage dotfiles using symlinking


## Install

```
ln --symbolic --verbose \
  $HOME/dotfiles/vim/vimrc.vim \
  $HOME/.vim/vimrc

set TARGET $HOME/.config/
set SOURCE $HOME/dotfiles/
stow --verbose=2 --target=$TARGET --dir=$SOURCE --stow nvim
stow --verbose=2 --target=$TARGET --dir=$SOURCE --delete nvim
stow -v --target=$HOME/.config/ *
```

## Alacritty

* rust bases
* [What is terminfo?](https://man7.org/linux/man-pages/man5/terminfo.5.html)


### vimfm

* Killer feature - undo and redo
* control spilits using CTRL+w s|v
* Save bookmarks with comma `'u`
* Browser preview `w` then `Shift+Tab`

#### vifm | Ranger

* [ ] Image previews
* [ ] Icons

## Q&A

Execute an external command?
:   `:! command`

Execute external command and replace the output of current buffer?
:       `:%! commadn`

Get the output of Ex-mode command in current buffer?
:       kbd:[Shift + Q] to enter Ex mode with multiple commands
        ```
        :redir >> fileName
        :set rtp?
        :redir END
        :visual
        ```

How to reaload the file?
:       `:edit` or `set autoread`

How to configure neovim?
:   `~/.config/nvim/init.vim`

How to configure status line as per your needs?
:   Has its own statusline `:help status-line`

## Checklist

* [x] Dont have to worry about `autoload/plug`, automatically saved there when vim-plug is installed
* [x] Install Fonts [fantasque-sans](https://github.com/belluzj/fantasque-sans)

```
sudo apt-get install -y fonts-fantasque-sans
```

## Use new Plugin system in vim 8+

```
cd ~/dotfiles
git submodule init
git submodule add https://github.com/vim-airline/vim-airline.git vim/pack/shapeshed/start/vim-airline
git add .gitmodules vim/pack/shapeshed/start/vim-airline
git commit

git submodule update --remote --merge
git commit
```

Within this folder a further folder start is needed to hold plugins. Vim will pick up any packages added to this folder and automatically load the plugins.

Optionally another folder opt may be created to hold packages that are not loaded automatically. Packages added in the opt folder may be loaded using
