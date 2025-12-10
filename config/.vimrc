" =============================================================================
" .vimrc - Vim configuration
" =============================================================================
" Copy to ~/.vimrc

" -----------------------------------------------------------------------------
" GENERAL
" -----------------------------------------------------------------------------
set nocompatible              " Use Vim settings, not Vi
filetype plugin indent on     " Enable filetype detection, plugins, indent
syntax enable                 " Enable syntax highlighting

set encoding=utf-8            " Use UTF-8
set fileencoding=utf-8
set termencoding=utf-8

set hidden                    " Allow hidden buffers
set history=1000              " Command history
set undolevels=1000           " Undo history

" -----------------------------------------------------------------------------
" INTERFACE
" -----------------------------------------------------------------------------
set number                    " Show line numbers
set relativenumber            " Relative line numbers
set cursorline                " Highlight current line
set showcmd                   " Show command in bottom bar
set showmode                  " Show current mode
set wildmenu                  " Visual autocomplete for commands
set wildmode=longest:full,full
set laststatus=2              " Always show status line
set ruler                     " Show cursor position
set title                     " Set terminal title
set scrolloff=5               " Keep 5 lines above/below cursor
set sidescrolloff=5           " Keep 5 columns left/right of cursor

" Colors
set background=dark
" colorscheme desert          " Uncomment for colorscheme

" Show invisible characters
set list
set listchars=tab:▸\ ,trail:·,extends:>,precedes:<,nbsp:+

" Line wrapping
set wrap                      " Wrap long lines
set linebreak                 " Wrap at word boundaries
set showbreak=↪\              " Show line continuation

" -----------------------------------------------------------------------------
" EDITING
" -----------------------------------------------------------------------------
set backspace=indent,eol,start  " Make backspace work properly
set autoindent                " Copy indent from current line
set smartindent               " Smart autoindenting on new lines

" Tabs and spaces
set tabstop=4                 " Visual spaces per tab
set softtabstop=4             " Spaces per tab when editing
set shiftwidth=4              " Spaces for autoindent
set expandtab                 " Use spaces instead of tabs
set smarttab                  " Insert tabs according to shiftwidth

" For specific file types
autocmd FileType python setlocal tabstop=4 shiftwidth=4 expandtab
autocmd FileType javascript,typescript,json,yaml setlocal tabstop=2 shiftwidth=2 expandtab
autocmd FileType html,css setlocal tabstop=2 shiftwidth=2 expandtab
autocmd FileType make setlocal noexpandtab  " Makefiles need tabs

" -----------------------------------------------------------------------------
" SEARCH
" -----------------------------------------------------------------------------
set incsearch                 " Search as you type
set hlsearch                  " Highlight matches
set ignorecase                " Ignore case when searching
set smartcase                 " Unless uppercase is used

" Clear search highlighting with <Esc>
nnoremap <Esc> :nohlsearch<CR><Esc>

" -----------------------------------------------------------------------------
" FILES
" -----------------------------------------------------------------------------
set autoread                  " Auto reload files changed outside vim
set nobackup                  " Don't create backup files
set nowritebackup
set noswapfile                " Don't create swap files

" Persistent undo
if has('persistent_undo')
    set undofile
    set undodir=~/.vim/undo
    if !isdirectory(&undodir)
        call mkdir(&undodir, 'p')
    endif
endif

" Remember cursor position
autocmd BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g'\"" | endif

" -----------------------------------------------------------------------------
" KEY MAPPINGS
" -----------------------------------------------------------------------------
" Set leader key to space
let mapleader = " "

" Quick save and quit
nnoremap <leader>w :w<CR>
nnoremap <leader>q :q<CR>
nnoremap <leader>x :x<CR>
nnoremap <leader>Q :qa!<CR>

" Quick edit/reload vimrc
nnoremap <leader>ev :e $MYVIMRC<CR>
nnoremap <leader>sv :source $MYVIMRC<CR>

" Better window navigation
nnoremap <C-h> <C-w>h
nnoremap <C-j> <C-w>j
nnoremap <C-k> <C-w>k
nnoremap <C-l> <C-w>l

" Split windows
nnoremap <leader>v :vsplit<CR>
nnoremap <leader>h :split<CR>

" Buffer navigation
nnoremap <leader>bn :bnext<CR>
nnoremap <leader>bp :bprevious<CR>
nnoremap <leader>bd :bdelete<CR>
nnoremap <leader>bl :ls<CR>

" Tab navigation
nnoremap <leader>tn :tabnew<CR>
nnoremap <leader>tc :tabclose<CR>
nnoremap gt :tabnext<CR>
nnoremap gT :tabprevious<CR>

" Move lines up/down
nnoremap <A-j> :m .+1<CR>==
nnoremap <A-k> :m .-2<CR>==
vnoremap <A-j> :m '>+1<CR>gv=gv
vnoremap <A-k> :m '<-2<CR>gv=gv

" Indent in visual mode (keep selection)
vnoremap < <gv
vnoremap > >gv

" Y yanks to end of line (like D and C)
nnoremap Y y$

" Keep centered when jumping
nnoremap n nzzzv
nnoremap N Nzzzv
nnoremap * *zzzv
nnoremap # #zzzv

" Quick pairs
inoremap ( ()<Left>
inoremap [ []<Left>
inoremap { {}<Left>
inoremap " ""<Left>
inoremap ' ''<Left>

" jk to exit insert mode
inoremap jk <Esc>
inoremap kj <Esc>

" -----------------------------------------------------------------------------
" FILE EXPLORER (netrw)
" -----------------------------------------------------------------------------
let g:netrw_banner = 0        " Hide banner
let g:netrw_liststyle = 3     " Tree view
let g:netrw_browse_split = 4  " Open in previous window
let g:netrw_winsize = 25      " Width percentage

nnoremap <leader>e :Lexplore<CR>

" -----------------------------------------------------------------------------
" CLIPBOARD
" -----------------------------------------------------------------------------
" Use system clipboard
if has('clipboard')
    set clipboard=unnamedplus
endif

" -----------------------------------------------------------------------------
" MOUSE
" -----------------------------------------------------------------------------
set mouse=a                   " Enable mouse in all modes
set ttymouse=sgr              " Better mouse support in terminals

" -----------------------------------------------------------------------------
" STATUS LINE
" -----------------------------------------------------------------------------
set statusline=
set statusline+=%#PmenuSel#
set statusline+=\ %f          " File name
set statusline+=%m            " Modified flag
set statusline+=%r            " Read only flag
set statusline+=%=            " Right align
set statusline+=\ %y          " File type
set statusline+=\ %{&fileencoding?&fileencoding:&encoding}
set statusline+=\ [%{&fileformat}]
set statusline+=\ %l:%c       " Line:column
set statusline+=\ %p%%        " Percentage through file
set statusline+=\

" -----------------------------------------------------------------------------
" AUTO COMMANDS
" -----------------------------------------------------------------------------
" Remove trailing whitespace on save
autocmd BufWritePre * :%s/\s\+$//e

" Auto-resize splits when vim is resized
autocmd VimResized * wincmd =

" Highlight yanked text
if exists('##TextYankPost')
    autocmd TextYankPost * silent! lua vim.highlight.on_yank{timeout=200}
endif

" -----------------------------------------------------------------------------
" CUSTOM COMMANDS
" -----------------------------------------------------------------------------
" Sudo save
command! W execute 'w !sudo tee % > /dev/null' <bar> edit!

" Strip trailing whitespace
command! StripWhitespace :%s/\s\+$//e

" Convert tabs to spaces
command! TabsToSpaces :%s/\t/    /g

" -----------------------------------------------------------------------------
" LOCAL OVERRIDES
" -----------------------------------------------------------------------------
" Source local vimrc if it exists
if filereadable(expand("~/.vimrc.local"))
    source ~/.vimrc.local
endif
