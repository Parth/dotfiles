" vim set configurations
"

if has('autocmd')
  filetype plugin indent on 					"filetype detection:ON  plugin:ON  indent:ON
  set backspace=start,eol,indent			"make backspace work in Insert Mode
  set bs=2                            "makes backspace behave like normal again
  set hidden												  "hide a unsaved buffer instead of showing warning
  set noswapfile											"only useful in multi-user systems
  set updatetime=4000                 "ms automatically write swaps to disk
  set autowrite                       "Automatically save before commands like :next and :make
endif
if has('syntax') && !exists('g:syntax_on')
  syntax enable
endif

" look for Project specific .vimrc files
" https://akrabat.com/using-vimrc-for-project-specific-settings/
set exrc
set secure

" do not make VIM compatible with VI. Might have undesired side-effects
" like- no undo file, no search highlights, no filetype and expandtab etc.
set nocompatible           " -N switch

" Preferences
set history=5000
set showcmd
set nojoinspaces
set complete-=t
set clipboard=unnamedplus             "automatically use system clipboard
set foldmethod=manual

" set listchars=tab:▸\ ,eol:¬
set foldlevelstart=99
set number relativenumber             "relative numbering from cursor
set title                             "set title of vim window to filename
" Real programmers don't use TABs but spaces
set autoindent         "copy indent to next line when <CR>
set smartindent        "strict indent rules for C-like files
set smartcase          "used with search patterns from / ? n N :g :s only

" search and sort
" Grepping and searching. Use :vimgrep for quickfix
set path+=**                          "inbuild fuzzy search at path root
set incsearch					                "realtime incremental search as we type
set hlsearch 						              "highlight search
set ignorecase
set smartcase           						  "ignores ignorecase
set cindent						                "indent C code
set autoindent
set tagstack                          "start storing tags on tagstack

" https://stackoverflow.com/questions/1878974/redefine-tab-as-4-spaces#:~:text=Always%20keep%20'tabstop'%20at%208,4%20(or%203)%20characters.
set tabstop=2 shiftwidth=2 softtabstop=0 smarttab expandtab 
setlocal textwidth=120

set wildmenu           " visual autocomplete for command menu
set lazyredraw         " redraw only when needed. Faster macros
""set showmatch          " highlight matching [{()}]
set mouse=a

set shortmess+=I       " disable intro splash
if !&scrolloff
  set scrolloff=1      " scrollon
endif
if !&sidescrolloff
  set sidescrolloff=5
endif
set display+=lastline  " :help 'display'
" displaying whitespaces and tabs at the end

" -------------------------------------------------------------------------------------------
" Build Tools and compilers for quickfix
set makeprg=make
" latex gcc npm \run \lint python haml
" could be updated by plugin for a specific project

" -------------------------------------------------------------------------------------------
" DO NOT UNCOMMENT THIS LINE-causes unpleasent highlights
" set spell spelllang=en_us
set spellfile=$HOME/.vim/en.utf-8.add
set thesaurus+=~/Documents/thesaurus    "Add thesaurus file for ^X^T
set dictionary+=~/Documents/dictionary  "Add dictionary file for ^X^K
