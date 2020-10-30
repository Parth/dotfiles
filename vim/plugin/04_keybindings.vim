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
if !has('nvim')
  "doesnt work in nvim
  execute "set <M-m>=\em"
endif
" inoremap <expr> <M-m> FunctionCall()
" causes problems E523
inoremap <M-m> <ESC>Bi`<ESC>Ea`
" For gnome-terminal use CTRL-V ALT-<key> ... for META key mappings
" https://stackoverflow.com/a/10633069/1915935
" i_CTRL-V => insert next non-digit literally
inoremap i <ESC>Bi*<ESC>Ea*
inoremap b <ESC>Bi**<ESC>Ea**
" make META key mappings work on nvim
if has('nvim')
  inoremap <M-i> <ESC>Bi*<ESC>Ea*
  inoremap <M-b> <ESC>Bi**<ESC>Ea**
endif

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
" ---------------------------------------------------
nnoremap <F1> :call ToggleHelpF1()<CR>
nnoremap <F2> :saveas 
nnoremap <F3> :write<CR>
inoremap <F3> <ESC>:write<CR>a
" nnoremap <F4> :Ranger<CR>
nnoremap <F4> :Vifm<CR>
nnoremap <S-F4> :NERDTreeToggle<CR>

nnoremap <F5> :edit<CR>
" discard local buffer changes and load from disk
nnoremap <S-F5> :edit!<CR>
" open git status in vertical split on left, unlike horizontal on top
nnoremap <F6> :call ToggleGitStatusF6()<CR>
nnoremap <S-F6> :Git 
" <F7> lint_program equalprg
" <S-F7> vim formatprg Format program
" <F8> grepprg
nnoremap <F8> :Rg 
nnoremap <S-F8> :grep 

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
    " cannot close last window! If this is the last window open
    execute 'close'
  else
    execute ':Git'
  endif
endfunction

" E523 Not allowed here
function! EncloseWord(symbol)
  "execute "normal! :<ESC>Bi" . a:symbol . "<ESC>Ea" . a:symbol
  :execute "normal B"
  ":execute "normal" count . "w"
endfunction

