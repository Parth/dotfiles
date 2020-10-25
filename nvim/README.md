# Neovim

* Do not have a [BDFL](https://en.wikipedia.org/wiki/Benevolent_dictator_for_life)
* Supports LSP Language Server Protocol
  * No need to use ctags, cscopes etc in that case
* New VimScript implementation with AST
* VIM way? This is the way
* UNIX way - simple, short, clear, modular and extensible code

```
:help design-improved
:help design-not
```


## Setup

```bash
# main neovim config
ln --symbolic --verbose \
  $HOME/dotfiles/neovim/init.vim \
  $HOME/.config/nvim/init.vim

# install vim-plug
sh -c 'curl -fLo "${XDG_DATA_HOME:-$HOME/.local/share}"/nvim/site/autoload/plug.vim --create-dirs \
       https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim'
```

### Bleeding edge

```bash
[ -f $HOME/mySoftwares/nvim.appimage ] && rm -fv $HOME/mySoftwares/nvim.appimage
wget \
  https://github.com/neovim/neovim/releases/download/nightly/nvim.appimage \
  --directory-prefix=$HOME/mySoftwares
chmod --verbose u+x $HOME/mySoftwares/nvim.appimage
# alias nvim=$HOME/mySoftwares/nvim.appimage
# nvim --version

sudo snap install --edge nvim --classic
```

## dotfiles

* https://github.com/alfunx/.dotfiles/tree/master/.vim