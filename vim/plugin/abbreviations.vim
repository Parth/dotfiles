" Abbreviations are used in Insert mode, Replace mode and Command-line mode.
" inoreabbrev - Insert-mode abbr only and do not remap
" 
" 
" GLOBAL ABBREVIATIONS
" -----------------------------------------
inoreabbrev -- ---
inoreabbrev avi Avi Mehenwal
" inoreabbrev email avi.mehenwal@gmai.com
inoreabbrev bang #!/usr/bin/env python
inoreabbrev shebang #!/usr/bin/env bash
inoreabbrev lorem Lorem ipsum dolor sit amet, consectetur adipisicing elit. Eligendi non quis exercitationem culpa nesciunt nihil aut nostrum explicabo reprehe nderit optio amet ab temporibus asperiores quasi cupiditate. Voluptatum ducimus voluptates voluptas?


" Command Mode Abbreviations
" -----------------------------------------
" command mode :x does the same thing and is shorter
cnoreabbrev hc helpclose
" <F1> with autocommand group vertical_help produces the same result
cnoreabbrev help vertical help


" Emoji shortcuts
" https://www.emojicopy.com/
" -----------------------------------------
inoreabbrev :check: ✅
inoreabbrev :warning: ⚠
inoreabbrev :bulb: 💡
inoreabbrev :pushpin: 📌
inoreabbrev :bomb: 💣
inoreabbrev :pill: 💊
inoreabbrev :construction: 🚧
inoreabbrev :pencil: 📝
inoreabbrev :point_right: 👉
inoreabbrev :book: 📖
inoreabbrev :link: 🔗
inoreabbrev :wrench: 🔧
inoreabbrev :info: 🛈
inoreabbrev :telephone: 📞
inoreabbrev :email: 📧
inoreabbrev :computer: 💻
inoreabbrev :+1: 👍
inoreabbrev :-1: 👎
inoreabbrev :v: ✌️
inoreabbrev :): 😎
inoreabbrev :hi: 🙋

" Markdown abbrevitions
" better use inoremap as they do not leave a
" trailing space after abbr is expanded
" https://stackoverflow.com/questions/11858927/preventing-trailing-whitespace-when-using-vim-abbreviations
" -------------------------------------------------- 
inoremap ` ``<left>
inoremap < <><left>
inoremap * **<left>
inoremap ** ****<left><left>
inoremap [ []<left>
inoremap ( ()<left>
