" let g:mapleader       = '\'
" let g:maplocalleader  = '['
let g:mapleader="\<Space>"
let maplocalleader="\\"

" Key bindings
" Do not use comments after the line in keymappings
" :help recursive-mapping
nnoremap ; :
nnoremap : ;
vnoremap ; :
vnoremap : ;

" nnoremap Q :q!<CR>     interferes with existing Q Multiple Ex-mode commands
" Quick buffer and Tabs navigation
" gt and gT for :tabNext and :tabPrev correspondingly
" ]b and [b for ;bNext and :bPrev correspondingly
" nnoremap <Tab> :tabNext<CR>

" Remove annoying highlight left after localsearch
nnoremap <silent> '/ :nohlsearch<CR>

" Markup blocks
inoremap <C-d> <ESC>yypA
" i_<C-m> interferes with Enter
if has('vim')
  "doesnt work in nvim
  execute "set <M-m>=\em"
endif
inoremap <M-m> <ESC>Bi`<ESC>Ea`

" vscode like bindings
nnoremap <C-p> :GitFiles<CR>

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

" GIT version Control with fugitive
" ---------------------------------------------------------------------------


" Function Keys
" -------------------------------------------------- 
nnoremap <F1> :call ToggleHelpF1()<CR>
nnoremap <F2> :saveas 
nnoremap <F3> :write<CR>
" nnoremap <F4> :Ranger<CR>
nnoremap <F4> :Vifm<CR>

nnoremap <F5> :NERDTreeToggle<CR>
" open git status in vertical split on left, unlike horizontal on top
nnoremap <F6> :call ToggleGitStatusF6()<CR>
nnoremap <S-F6> :Git 
" <F7> lint_program equalprg
" <S-F7> vim formatprg Format program
" <F8> grepprg
nnoremap <F8> :Rg 

nnoremap <F9> :terminal<CR>             "open terminal half-mode
nnoremap <S-F9> :shell<CR>              "open terminal full-screen
" <F10> copyQ
" <F11> Fullscreen
nnoremap <F12> :make<CR>                "Build project
nnoremap <S-F12> :make 

function! ToggleHelpF1()
  if &buftype == "help"
    execute 'helpclose'
  else
    " execute 'vertical help'
    execute 'Helptags'
  endif
endfunction

" use && and || for AND, OR with of conditions
function! ToggleGitStatusF6()
  if &filetype == "fugitive"
    execute 'close'
  else
    execute ':Git'
  endif
endfunction

