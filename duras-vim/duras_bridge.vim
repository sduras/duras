if exists('g:loaded_duras_bridge') | finish | endif
let g:loaded_duras_bridge = 1

function! s:ClipGet()
    let l:text = getreg('+')

    if empty(l:text)
        silent! let l:text = system('pbpaste')
    endif

    return l:text
endfunction


function! s:ClipSet(text)
    call setreg('+', a:text)
    silent! call system('pbcopy', a:text)
endfunction


function! s:BufGet()
    return join(getline(1, '$'), "\n")
endfunction


function! s:Exec(cmd)
    return system(a:cmd)
endfunction


command! -nargs=? DOpen call s:DOpen(<q-args>)

function! s:DOpen(arg)
    let l:cmd = empty(a:arg) ? 'duras path' : 'duras path ' . shellescape(a:arg)
    let l:path = trim(system(l:cmd))

    if v:shell_error != 0 || empty(l:path)
        echoerr 'duras: path failed'
        return
    endif

    if !filereadable(l:path)
        let l:open_cmd = empty(a:arg)
            \ ? 'EDITOR=true duras open'
            \ : 'EDITOR=true duras open ' . shellescape(a:arg)
        call system(l:open_cmd)
        if v:shell_error != 0
            echoerr 'duras: failed to initialize note'
            return
        endif
    endif

    execute 'edit ' . fnameescape(l:path)
endfunction


command! -range=% -nargs=? DAppend <line1>,<line2>call s:DAppend(<q-args>)

function! s:DAppend(arg) range
    if a:arg ==# '-'
        let l:text = s:ClipGet()
    elseif a:arg !=# ''
        let l:text = a:arg
    else
        let l:text = join(getline(a:firstline, a:lastline), "\n")
    endif

    call system('duras append -', l:text)

    if v:shell_error != 0
        echoerr "duras: append failed"
    endif
endfunction


command! -nargs=+ DSearch call s:DSearch(<q-args>)

function! s:DSearch(q)
    let l:out = system('duras search ' . shellescape(a:q))

    if v:shell_error != 0 || empty(l:out)
        echo "No results"
        return
    endif

    belowright new [duras-search]
    setlocal buftype=nofile bufhidden=wipe noswapfile nowrap cursorline

    call setline(1, split(l:out, "\n"))

    nnoremap <silent><buffer> <CR> :call <SID>OpenFromSearch()<CR>
endfunction


function! s:OpenFromSearch()
    let l:line = getline('.')
    let l:date = matchstr(l:line, '^\d\{4\}-\d\{2\}-\d\{2\}')

    if empty(l:date)
        return
    endif

    bwipeout!
    execute 'DOpen ' . l:date
endfunction


command! DStats echo system('duras stats')

command! DPath echo trim(system('duras path'))
command! DCopyPath call s:ClipSet(trim(system('duras path')))

command! -nargs=? DTags call s:DSearch('tags ' . <q-args>)


nnoremap <leader>do :DOpen<CR>
nnoremap <leader>ds :DSearch 
nnoremap <leader>da :DAppend<CR>
vnoremap <leader>da :DAppend<CR>
nnoremap <leader>dp :DPath<CR>
