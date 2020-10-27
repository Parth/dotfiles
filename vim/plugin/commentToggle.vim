" set rootdirectory after a project is opened from ranger bookmarks
" https://vim.fandom.com/wiki/Set_working_directory_to_the_current_file
" :au[tocmd] [group] {event} {pat} [++once] [++nested] {cmd}
" TODO https://superuser.com/questions/598947/setting-vim-options-only-for-files-in-a-certain-directory-tree/598970
" Directory specific autocommands - to manage various projects

autocmd BufEnter $HOME/GIT/*,$HOME/REPO/* silent! call s:local_workspace()

function! s:local_workspace() abort
    " FIXME use relative paths for scripts
    let l:git_path = system('$HOME/REPO/aviscripts/cdr.sh')
    :execute 'lcd ' . l:git_path
    " !ctags-exuberant --recurse
    " let s:tag_path = system('readlink --canonicalize tags')
    " :execute "set tags=" . s:tag_path
endfunction

" Use grep to get a clickable list of function names
" https://vim.fandom.com/wiki/Use_grep_to_get_a_clickable_list_of_function_names
function! ShowFunc()
  let gf_s = &grepformat
  let gp_s = &grepprg
  let &grepformat = '%*\k%*\sfunction%*\s%l%*\s%f %*\s%m'
  let &grepprg = 'ctags -x --c-types=f --sort=no -o -'
  write
  silent! grep %
  cwindow
  let &grepformat = gf_s
  let &grepprg = gp_s
endfunc

" execute a bash script
function! s:get_git_root_dir() abort
  " :echomsg "This is from test function"
  " :echo "shell =" &shell
  " :echo l:git_root
  " :lcd l:git_root
  " execute "!/home/avi/REPO/aviscripts/cdr.sh"
  " !/home/avi/REPO/aviscripts/cdr.sh
endfunction


" vscode line comment and uncomment
function! Comment_line() abort
    " TODO use comment delimiter based on filetype
    :execute "normal! mcI# \<esc>`c2l"
endfunction

function! Uncomment_line() abort
    :execute "normal! mc^2x`c2h"
endfunction

function Comment_block() range
  let l:diff = a:lastline - a:firstline
  :echomsg "difference = " . l:diff
  if ( l:diff > 0 )
    :execute "normal! " . a:firstline . "gg\<C-v>" . l:diff . "jI# \<esc>"
  else
    :execute "normal! " . a:firstline . "gg"
    :call Comment_line()
  endif
endfunction

function Uncomment_block() range
  let l:diff = a:lastline - a:firstline
  :echomsg a:lastline . "-" . a:firstline . " = " . l:diff
  if ( l:diff > 0 )
    :execute "normal! " . a:firstline . "gg\<C-v>" . l:diff . "jlx\<esc>"
  else
    :execute "normal! " . a:firstline . "gg"
    :call Uncomment_line()
  endif
endfunction


nnoremap <C-_> :call Comment_line()<CR>
" <C-S-_> doesnt work neither does <M-/>
nnoremap <Leader>/ :call Uncomment_line()<CR>
vnoremap <C-_> :call Comment_block()<CR>
vnoremap <Leader>/ :call Uncomment_block()<CR>

