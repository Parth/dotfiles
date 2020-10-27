" Global Plugin - automatically loaded for all files
"
" vscode line code-block, code-line movement keybindings
" https://vim.fandom.com/wiki/Moving_lines_up_or_down
"
" Use ALT + movement keys
" :help move

" use meta key bindings
" https://stackoverflow.com/a/27206531/1915935

execute "set <M-j>=\ej"
execute "set <M-k>=\ek"

nnoremap <M-j> :m .+1<CR>==
nnoremap <M-k> :m .-2<CR>==
vnoremap <M-j> :m '>+1<CR>gv=gv
vnoremap <M-k> :m '<-2<CR>gv=gv
" causes troble editing, maybe latency
"   inoremap <M-k> <Esc>:m .-2<CR>==gi
"   inoremap <M-j> <Esc>:m .+1<CR>==gi
