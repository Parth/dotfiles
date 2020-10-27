" project specific file
" Dotfiles
" Avi Mehenwal 
"

" respects .gitignore and automatically skip hidden files/directories and binary files.
" use --glob=! to exclude directories
set grepprg=rg\ --smart-case\ --vimgrep\ --glob='!docs/*'\ --glob='!*.lock'


" exclude path
" set path-=node_modules
" set path-=zsh/plugins
set path-=yarn.lock

"   set wildignore+=*/node_modules/*
"   set wildignore+=*/zsh/plugins/*
"   set wildignore+=*/docs/*
"   set wildignore+=*.lock
set wildignore=*/docs/*,*.lock,*/node_modules/*
