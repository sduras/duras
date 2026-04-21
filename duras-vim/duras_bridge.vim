if exists('g:loaded_duras_bridge') | finish | endif
let g:loaded_duras_bridge = 1


function! s:ClipGet()
    if executable('pbpaste')
        let l:text = trim(system('pbpaste'))
        if v:shell_error == 0 | return l:text | endif
    endif
    if executable('xclip')
        let l:text = trim(system('xclip -selection clipboard -o'))
        if v:shell_error == 0 | return l:text | endif
    endif
    if executable('xsel')
        let l:text = trim(system('xsel --clipboard --output'))
        if v:shell_error == 0 | return l:text | endif
    endif
    return getreg('+')
endfunction


function! s:ClipSet(text)
    call setreg('+', a:text)
    if executable('pbcopy')
        silent! call system('pbcopy', a:text)
    elseif executable('xclip')
        silent! call system('xclip -selection clipboard', a:text)
    elseif executable('xsel')
        silent! call system('xsel --clipboard --input', a:text)
    endif
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
        let l:open_cmd = empty(a:arg) ? 'duras open' : 'duras open ' . shellescape(a:arg)
        call system('EDITOR=echo ' . l:open_cmd)
        if v:shell_error != 0
            echoerr 'duras: failed to initialise note'
            return
        endif
    endif

    execute 'edit ' . fnameescape(l:path)
endfunction


command! -range=% -nargs=* DAppend <line1>,<line2>call s:DAppend(<q-args>)

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
        echoerr 'duras: append failed'
    endif
endfunction


command! -nargs=+ DSearch call s:DSearch(<q-args>)

function! s:DSearch(q)
    let l:out = system('duras search ' . shellescape(a:q))

    if v:shell_error != 0 || empty(l:out)
        echo 'No results'
        return
    endif

    belowright new
    setlocal buftype=nofile bufhidden=wipe noswapfile nowrap cursorline
    silent execute 'file [duras-search]'
    call setline(1, split(l:out, "\n"))

    nnoremap <silent><buffer> <CR> :call <SID>OpenFromSearch()<CR>
endfunction


function! s:OpenFromSearch()
    let l:date = matchstr(getline('.'), '^\d\{4\}-\d\{2\}-\d\{2\}')

    if empty(l:date)
        return
    endif

    bwipeout!
    execute 'DOpen ' . l:date
endfunction


command! DClipYank  call s:ClipSet(s:BufGet())
command! DClipPaste call s:DClipPaste()

function! s:DClipPaste()
    let l:text = s:ClipGet()
    if empty(l:text)
        echoerr 'duras: clipboard is empty'
        return
    endif
    call append(line('.'), split(l:text, "\n"))
endfunction


command! DStats    echo system('duras stats')
command! DPath     echo trim(system('duras path'))
command! DCopyPath call s:ClipSet(trim(system('duras path')))

command! -nargs=? DTags call s:DTags(<q-args>)

function! s:DTags(tag)
    let l:cmd = empty(a:tag) ? 'duras tags' : 'duras tags ' . shellescape(a:tag)
    let l:out = system(l:cmd)
    if v:shell_error != 0 || empty(l:out)
        echo 'No tags'
        return
    endif
    echo l:out
endfunction


nnoremap <leader>do :DOpen<CR>
nnoremap <leader>ds :DSearch 
nnoremap <leader>da :DAppend<CR>
vnoremap <leader>da :DAppend<CR>
nnoremap <leader>dp :DPath<CR>
