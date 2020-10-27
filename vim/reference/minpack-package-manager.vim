packadd minpac

if !exists('g:loaded_minpac')
  " minpac is not available, Settings for plugin-less environment.
  finish
else
  call minpac#init({'verbose': 0})
  call minpac#add('k-takata/minpac', {'type': 'opt'})

  " Functionality Enhancement
  call minpac#add('tpope/vim-surround')                         "quickly change surround quotes/tags
  call minpac#add('tpope/vim-unimpaired')
  call minpac#add('francoiscabrol/ranger.vim')
  call minpac#add('jremmen/vim-ripgrep')
  call minpac#add('bronson/vim-visual-star-search')
  call minpac#add('junegunn/fzf')                             "!fzf
  call minpac#add('junegunn/fzf.vim')
  call minpac#add('SirVer/ultisnips')
  call minpac#add('honza/vim-snippets')
  call minpac#add('neoclide/coc.nvim')                        "intelliSense
  call minpac#add('tpope/vim-fugitive')
  call minpac#add('tpope/vim-rhubarb')
  call minpac#add('preservim/nerdtree')
  call minpac#add('Xuyuanp/nerdtree-git-plugin')
  call minpac#add('ryanoasis/vim-devicons')

  " syntax highlighting and presentation
  call minpac#add('asciidoc/vim-asciidoc')                      "asciidoc syntax highlight
  call minpac#add('vim-airline/vim-airline')                    "https://github.com/vim-airline/vim-airline
  call minpac#add('vim-airline/vim-airline-themes')
  call minpac#add('junegunn/vim-emoji')
  call minpac#add('bronson/vim-visual-star-search')
  call minpac#add('morhetz/gruvbox')

  " Experimental
  call minpac#add('vim/killersheep')
  call minpac#add('AndrewRadev/quickpeek.vim')

  " Polyfills
  if !has('nvim')
    call minpac#add('rhysd/vim-healthcheck')
  endif
endif

" minpac convenience commands with reloadable vimrc
command! PluginInstall source $MYVIMRC | redraw | call minpac#update()
command! PluginClean  source $MYVIMRC | call minpac#clean()
command! PluginStatus packadd minpac | call minpac#status()

" Resources
" https://www.freecodecamp.org/news/vim-for-people-who-use-visual-studio-code/
