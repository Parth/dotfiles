" Use configs as .vimrc
" set runtimepath^=~/.vim runtimepath+=~/.vim/after
" let &packpath = &runtimepath
" source ~/.vimrc


" Plugin Manager
call plug#begin()
Plug 'tpope/vim-sensible'                               "set config sensible defaults
Plug 'mhinz/vim-signify'                                "vim gitgutter killer
Plug 'tpope/vim-fugitive'				"version control
Plug 'vim-airline/vim-airline'
Plug 'tpope/vim-unimpaired'				"complementary pair of mappings
Plug 'tpope/vim-commentary'				"comment with ranges
Plug 'ap/vim-css-color'					"vscode like colorbackground for colorcodes

call plug#end()

set updatetime=100


" Build statusline yourself
set cursorline
set statusline=
set statusline+=\ %r       "if file is read-only
set statusline+=\ %M       "is file modifyable
set statusline+=\ %y       "type of file
set statusline+=\ %F       "full file path
" set statusline+=\ %b       "values of char under cursor

" right leaning
set statusline+=%=
set statusline+=\ %p%%       "percentage scroll
set statusline+=\ %l/%L:%c   "total number of line
set statusline+=\ [%n]       "buffer number

" Add colors to status line?
