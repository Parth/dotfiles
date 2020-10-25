" Use configs as .vimrc
" set runtimepath^=~/.vim runtimepath+=~/.vim/after
" let &packpath = &runtimepath
" source ~/.vimrc


" Plugin Manager
call plug#begin()

Plug 'tpope/vim-sensible'                               "set config sensible defaults
Plug 'mhinz/vim-signify'                                "vim gitgutter killer
Plug 'tpope/vim-fugitive'				                        "version control
Plug 'vim-airline/vim-airline'
Plug 'tpope/vim-unimpaired'		                      		"complementary pair of mappings
Plug 'tpope/vim-commentary'				                      "comment with ranges
Plug 'ap/vim-css-color'					                        "vscode like colorbackground for colorcodes
Plug 'morhetz/gruvbox'

call plug#end()

set backspace=start,eol,indent			                    " make backspace work in Insert Mode
set noswapfile											                    " only useful in multi-user systems
set updatetime=4000                                     " ms automatically write swaps to disk
set hidden												                      " hide a unsaved buffer instead of showing warning

if has('autocmd')
  filetype plugin indent on
endif
if has('syntax') && !exists('g:syntax_on')
  syntax enable
endif

" source $HOME/dotfiles/nvim/statusline.vim