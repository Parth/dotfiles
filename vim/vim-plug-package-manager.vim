call plug#begin('~/.vim/plugged')

" Unmanaged plugin (manually installed and updated)
" Plug '~/dotfiles/vim/keybindings.vim'
" Plug '~/dotfiles/vim/general-config.vim'

" Functionality Enhancement
Plug 'junegunn/fzf.vim'                                                   "GOD of plugins
Plug 'SirVer/ultisnips'                                                   "vscode like snippets
Plug 'tpope/vim-sleuth'                                                   "shiftwidth and expandtab manager
Plug 'tpope/vim-rhubarb'                                                  "fugitive suppliment
Plug 'tpope/vim-fugitive'                                                 "version control within vim
Plug 'tpope/vim-surround'                                                 "YAGNI - text Objects
Plug 'honza/vim-snippets'                                                 "ultisnips suppliment
Plug 'tpope/vim-unimpaired'                                               "sane quickfix,,buffer hotkeys
Plug 'ryanoasis/vim-devicons'                                             "iconify
Plug 'bronson/vim-visual-star-search'                                     "search url like patterns
Plug 'jremmen/vim-ripgrep', { 'on':  'Rg' }                               "use rip-grep from within vim
Plug 'junegunn/fzf', { 'do': { -> fzf#install() } }                       "fzf cli tool
Plug 'francoiscabrol/ranger.vim', { 'on':  'Ranger' }                     "cli file browser
Plug 'preservim/nerdtree', { 'on':  'NERDTreeToggle' }                    "vscode like directory browser
Plug 'Xuyuanp/nerdtree-git-plugin', { 'on':  'NERDTreeToggle' }           "nerdtree supliment
Plug 'neoclide/coc.nvim', {'do': 'yarn install --frozen-lockfile'}        "intellisense

" syntax highlighting and presentation
Plug 'morhetz/gruvbox'                                                    "colorscheme with dark/light mode yob
Plug 'junegunn/vim-emoji'                                                 "emojify
Plug 'asciidoc/vim-asciidoc'                                              "adoc markup
Plug 'vim-airline/vim-airline'                                            "statusline
Plug 'vim-airline/vim-airline-themes'                                     "vim-airline suppliment

" Experimental
Plug 'vim/killersheep'                                                    "vim popup()
Plug 'AndrewRadev/quickpeek.vim'                                          "expand items in popup from quickfix window

" Polyfills
if !has('nvim')
  Plug 'rhysd/vim-healthcheck'                                            ":Healthcheck from neovim
endif

" Initialize plugin system
call plug#end()