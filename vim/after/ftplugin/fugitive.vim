" Toggle git status information in vertical split <F6>
" -------------------------------------------------- 

augroup vertical_git_status
  autocmd!
  autocmd BufWinEnter <buffer> wincmd H | vertical resize 50
augroup END
