" AUTHOR : avimehenwal
" FILE   : $HOME/.vimrc  $MYVIMRC
" ORIGIN : Sat 28 Apr 05:01:05 IST 2018
"
" Don't seek mastery, seek proficiency
"
" start vim with zero configuration
" -N              									Not fully Vi compatible: 'nocompatible'
" -u <vimrc>      									Use <vimrc> instead of any .vimrc
" vi -Nu NORC <filepath>
"
" Order of rc-file detection
" 1. $VIMINIT												Environment Variable
" 2. $HOME/.vimrc
" 3. $HOME/.vim/vimrc
" 4. $EXINIT												Environment Variable
" 5. $HOME/.exrc
" 6. $VIMRUNTIME/defaults.vim


" linter Tools :retab

" set some environment variable
let $RTP=split(&runtimepath, ',')[0]
let $RC="$HOME/.vim/vimrc"

" Runtimepath
set rtp+=$HOME/.fzf/bin/fzf
set rtp+=$HOME/.vim/plugged/gruvbox

" source vim files
" sometimes order matters
source $HOME/dotfiles/vim/vimPlugPackageManager.vim
source $HOME/dotfiles/vim/setConfig.vim
source $HOME/dotfiles/vim/abbreviations.vim
source $HOME/dotfiles/vim/commentToggle.vim
" source $HOME/dotfiles/vim/netrwconfig.vim
source $HOME/dotfiles/vim/keybindings.vim
source $HOME/dotfiles/vim/autocommands.vim
source $HOME/dotfiles/vim/pluginConfigs.vim

" vim Session-management
"":mksession ~/mysession.vim
"":source ~/mysession.vim
""$ vim -S ~/mysession.vim

"           +--Disable hlsearch while loading viminfo
"           | +--Remember marks for last 500 files
"           | |    +--Remember up to 10000 lines in each register
"           | |    |      +--Remember up to 1MB in each register
"           | |    |      |     +--Remember last 1000 search patterns
"           | |    |      |     |     +---Remember last 1000 commands
"           | |    |      |     |     |
"           v v    v      v     v     v
""set viminfo=h,'500,<10000,s1000,/1000,:1000
""set viminfo='1000,f1,<500  "lines, marks
"}}}
