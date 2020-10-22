let g:mapleader       = '\'
let g:maplocalleader  = '['

" Key bindings
" Do not use comments after the line in keymappings
nnoremap ; :

" Markup blocks
inoremap <C-d> <ESC>yypA
" i_<C-m> interferes with Enter
execute "set <M-m>=\em"
inoremap <M-m> <ESC>Bi`<ESC>Ea`

" vscode like bindings
nmap <C-p> :GitFiles<CR>

" Use g for GIT and GOTO
" https://github.com/junegunn/fzf.vim/blob/master/README.md
"
nnoremap gb :Buffers<CR>
nnoremap gc :Commands!<CR>
nnoremap gh :History:<CR>
nnoremap gk :Maps<CR>
nnoremap gl :BCommits!<CR>
nnoremap gL :Commits!<CR>
nnoremap gm :Marks<CR>
nnoremap gp :edit $HOME/.vim/packages.vim<CR>
nnoremap gs :Snippets<CR>
nnoremap gv :edit $MYVIMRC<CR>
nnoremap g? :Helptags<CR>

" open vimrc
nnoremap sv :source $MYVIMRC<CR>

" code refactor
nnoremap <Leader>s :%s/\<<C-r><C-w>\>//g<Left><Left>
nnoremap <Leader>gd <Plug>(coc-definition)
nnoremap <Leader>gr <Plug>(coc-references)

" Function Keys
nnoremap <F4> :Ranger<CR>
nnoremap <F5> :NERDTreeToggle<CR>
nnoremap <F9> :terminal<CR>             "open terminal half-mode
nnoremap <S-F9> :shell<CR>              "open terminal full-screen

