#!/usr/bin/env python3
import os
import re
import subprocess
import shutil
from bs4 import BeautifulSoup
import json

def get_c_man_pages():
    sections = ["2", "3"]
    c_pages = []
    
    for section in sections:
        try:
            result = subprocess.run(
                f"man -k -s {section} .", 
                shell=True, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line:
                        match = re.match(r'^([^\s]+)\s+\(([^)]+)\)\s+(.*)$', line)
                        if match:
                            name, section, description = match.groups()
                            if re.search(r'c|libc|posix|stdio|stdlib|string|math|unix', 
                                        description.lower() + name.lower()):
                                c_pages.append({
                                    'name': name,
                                    'section': section,
                                    'description': description
                                })
        except Exception as e:
            print(f"Error processing section {section}: {e}")
    
    return c_pages

def convert_man_to_html(man_entry, output_dir):
    name = man_entry['name']
    section = man_entry['section']
    
    try:
        html = subprocess.run(
            f"man -Thtml {name} {section}",
            shell=True,
            capture_output=True,
            text=True
        ).stdout
        
        html = html.replace("'", "'").replace(""", '"').replace(""", '"')
        
        soup = BeautifulSoup(html, 'html.parser')
        
        meta = soup.new_tag('meta')
        meta['name'] = 'viewport'
        meta['content'] = 'width=device-width, initial-scale=1.0'
        soup.head.append(meta)
        
        if not soup.title:
            title = soup.new_tag('title')
            title.string = f"{name}({section}) - C Manual Page"
            soup.head.append(title)
        
        style = soup.new_tag('style')
        style.string = """
            :root {
                --primary-color: #3498db;
                --background-color: #f9f9f9;
                --text-color: #333;
                --code-bg: #f0f0f0;
                --header-color: #2c3e50;
                --link-color: #2980b9;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: var(--text-color);
                background-color: var(--background-color);
                max-width: 900px;
                margin: 0 auto;
                padding: 2rem;
            }
            h1, h2, h3, h4 {
                color: var(--header-color);
            }
            h1 {
                border-bottom: 2px solid var(--primary-color);
                padding-bottom: 0.5rem;
            }
            pre {
                background-color: var(--code-bg);
                padding: 1rem;
                border-radius: 4px;
                overflow-x: auto;
            }
            a {
                color: var(--link-color);
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            .man-navigation {
                background-color: #fff;
                border-bottom: 1px solid #ddd;
                padding: 0.5rem 0;
                position: sticky;
                top: 0;
                z-index: 100;
            }
            .section {
                margin-top: 2rem;
            }
            @media (prefers-color-scheme: dark) {
                :root {
                    --primary-color: #3498db;
                    --background-color: #222;
                    --text-color: #f0f0f0;
                    --code-bg: #333;
                    --header-color: #3498db;
                    --link-color: #5dade2;
                }
            }
            .back-to-index {
                display: inline-block;
                margin: 1rem 0;
                padding: 0.5rem 1rem;
                background-color: var(--primary-color);
                color: white;
                border-radius: 4px;
                text-decoration: none;
            }
            .back-to-index:hover {
                background-color: var(--link-color);
                text-decoration: none;
            }
        """
        soup.head.append(style)
        
        nav = soup.new_tag('div')
        back_link = soup.new_tag('a')
        back_link['href'] = '../index.html'
        back_link['class'] = 'back-to-index'
        back_link.string = '← Back to Index'
        nav.append(back_link)
        
        if soup.body.contents:
            soup.body.insert(0, nav)
        else:
            soup.body.append(nav)
        
        output_path = os.path.join(output_dir, f"{name}.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
            
        return True
    except Exception as e:
        print(f"Error processing {name}({section}): {e}")
        return False

def create_index_page(man_pages, output_dir):
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>C Programming Manual Pages</title>
        <style>
            :root {
                --primary-color: #3498db;
                --secondary-color: #2ecc71;
                --background-color: #f9f9f9;
                --card-bg: #fff;
                --text-color: #333;
                --header-color: #2c3e50;
                --shadow-color: rgba(0, 0, 0, 0.1);
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: var(--text-color);
                background-color: var(--background-color);
                margin: 0;
                padding: 0;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }
            
            header {
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                padding: 2rem 0;
                text-align: center;
                border-radius: 0 0 10px 10px;
                box-shadow: 0 4px 6px var(--shadow-color);
                position: sticky;
                top: 0;
                z-index: 10;
            }
            
            h1 {
                margin: 0;
                font-size: 2.5rem;
            }
            
            .subtitle {
                font-weight: 300;
                margin-top: 0.5rem;
            }
            
            .search-container {
                margin: 2rem 0;
                text-align: center;
                position: sticky;
                top: 8rem;
                z-index: 9;
                background-color: var(--background-color);
                padding: 1rem 0;
                border-radius: 0 0 10px 10px;
                box-shadow: 0 4px 6px var(--shadow-color);
            }
            
            .search-box {
                padding: 0.8rem 1.5rem;
                width: 80%;
                max-width: 600px;
                border: 2px solid #ddd;
                border-radius: 50px;
                font-size: 1rem;
                outline: none;
                transition: all 0.3s;
            }
            
            .search-box:focus {
                border-color: var(--primary-color);
                box-shadow: 0 0 8px rgba(52, 152, 219, 0.5);
            }

            .filter-options {
                margin-top: 1rem;
                display: flex;
                justify-content: center;
                gap: 1rem;
                flex-wrap: wrap;
            }

            .filter-button {
                background-color: var(--card-bg);
                border: 1px solid #ddd;
                border-radius: 20px;
                padding: 0.5rem 1rem;
                cursor: pointer;
                transition: all 0.3s;
            }

            .filter-button.active {
                background-color: var(--primary-color);
                color: white;
                border-color: var(--primary-color);
            }
            
            .search-help {
                font-size: 0.8rem;
                margin-top: 0.5rem;
                color: #666;
                text-align: center;
            }
            
            .search-options {
                display: flex;
                justify-content: center;
                margin-top: 1rem;
                gap: 1rem;
                flex-wrap: wrap;
            }
            
            .search-option {
                display: flex;
                align-items: center;
                gap: 0.3rem;
            }
            
            .pagination {
                display: flex;
                justify-content: center;
                margin: 2rem 0;
                gap: 0.5rem;
            }
            
            .page-button {
                padding: 0.5rem 1rem;
                background-color: var(--card-bg);
                border: 1px solid #ddd;
                border-radius: 4px;
                cursor: pointer;
                transition: all 0.3s;
            }
            
            .page-button.active {
                background-color: var(--primary-color);
                color: white;
                border-color: var(--primary-color);
            }
            
            .page-info {
                margin: 0 1rem;
                display: flex;
                align-items: center;
            }
            
            .man-pages {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 1.5rem;
                margin-top: 2rem;
            }
            
            .man-card {
                background-color: var(--card-bg);
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 6px var(--shadow-color);
                transition: transform 0.3s, box-shadow 0.3s;
                height: 100%;
                display: flex;
                flex-direction: column;
                will-change: transform;
                contain: content;
            }
            
            .man-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 20px var(--shadow-color);
            }
            
            .man-card-header {
                background-color: var(--primary-color);
                color: white;
                padding: 1rem;
                font-weight: bold;
            }
            
            .man-card-body {
                padding: 1.5rem;
                flex-grow: 1;
                display: flex;
                flex-direction: column;
            }
            
            .section-badge {
                display: inline-block;
                background-color: var(--secondary-color);
                color: white;
                border-radius: 20px;
                padding: 0.2rem 0.8rem;
                font-size: 0.8rem;
                margin-left: 0.5rem;
            }
            
            .description {
                margin-top: 0.8rem;
                color: #666;
                flex-grow: 1;
            }
            
            .no-results {
                text-align: center;
                padding: 2rem;
                grid-column: 1 / -1;
                font-style: italic;
                color: #888;
            }
            
            .sort-options {
                display: flex;
                justify-content: flex-end;
                margin: 1rem 0;
                gap: 0.5rem;
            }
            
            .sort-label {
                display: flex;
                align-items: center;
                font-size: 0.9rem;
            }
            
            .sort-select {
                padding: 0.3rem 0.5rem;
                border-radius: 4px;
                border: 1px solid #ddd;
            }
            
            .highlight {
                background-color: rgba(255, 255, 0, 0.3);
                padding: 0 2px;
                border-radius: 2px;
            }
            
            footer {
                text-align: center;
                margin-top: 3rem;
                padding: 1rem 0;
                color: #777;
                font-size: 0.9rem;
            }
            
            .loading-indicator {
                text-align: center;
                padding: 2rem;
                grid-column: 1 / -1;
            }
            
            .spinner {
                display: inline-block;
                width: 40px;
                height: 40px;
                border: 4px solid rgba(0, 0, 0, 0.1);
                border-radius: 50%;
                border-top-color: var(--primary-color);
                animation: spin 1s ease-in-out infinite;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            @media (prefers-color-scheme: dark) {
                :root {
                    --background-color: #222;
                    --card-bg: #333;
                    --text-color: #f0f0f0;
                    --header-color: #3498db;
                    --shadow-color: rgba(0, 0, 0, 0.3);
                }
                
                .search-box {
                    background-color: #444;
                    color: white;
                    border-color: #555;
                }
                
                .description {
                    color: #aaa;
                }
                
                .no-results {
                    color: #aaa;
                }
                
                .search-help {
                    color: #aaa;
                }
                
                .highlight {
                    background-color: rgba(255, 255, 0, 0.2);
                    color: #fff;
                }
                
                footer {
                    color: #999;
                }
                
                .spinner {
                    border-color: rgba(255, 255, 255, 0.1);
                    border-top-color: var(--primary-color);
                }
            }
            
            @media (max-width: 768px) {
                .container {
                    padding: 1rem;
                }
                
                .man-pages {
                    grid-template-columns: 1fr;
                }
                
                .search-box {
                    width: 95%;
                }
                
                .filter-options {
                    flex-wrap: wrap;
                }
            }
        </style>
    </head>
    <body>
        <header>
            <div class="container">
                <h1>C Programming Manual Pages</h1>
                <p class="subtitle">A comprehensive collection of C-related manual pages</p>
            </div>
        </header>
        
        <div class="container">
            <div class="search-container">
                <input type="text" id="searchBox" class="search-box" placeholder="Search for functions, headers, or keywords..." autocomplete="off">
                <div class="search-help">
                    <span>Search tips: Use quotes for exact function names (e.g., "printf"), prefix with @ for functions only</span>
                </div>
                <div class="search-options">
                    <label class="search-option">
                        <input type="checkbox" id="exactMatch"> Exact match
                    </label>
                    <label class="search-option">
                        <input type="checkbox" id="nameOnly"> Search function names only
                    </label>
                    <label class="search-option">
                        <input type="checkbox" id="highlightMatches" checked> Highlight matches
                    </label>
                </div>
                <div class="filter-options">
                    <button class="filter-button active" data-section="all">All Sections</button>
                    <button class="filter-button" data-section="2">Section 2</button>
                    <button class="filter-button" data-section="3">Section 3</button>
                </div>
            </div>
            
            <div class="sort-options">
                <span class="sort-label">Sort by:</span>
                <select id="sortSelect" class="sort-select">
                    <option value="name-asc">Name (A-Z)</option>
                    <option value="name-desc">Name (Z-A)</option>
                    <option value="section-asc">Section (Ascending)</option>
                    <option value="section-desc">Section (Descending)</option>
                </select>
            </div>
            
            <div class="man-pages" id="manPages">
                <div class="loading-indicator">
                    <div class="spinner"></div>
                    <p>Loading manual pages...</p>
                </div>
            </div>
            
            <div class="pagination" id="pagination">
            </div>
        </div>
        
        <footer>
            <div class="container">
                <p>Generated on <span id="genDate"></span></p>
                <p>Total entries: <span id="totalEntries"></span> | Showing: <span id="shownEntries"></span></p>
            </div>
        </footer>
        
        <script>
            const allManPagesData = DATA_PLACEHOLDER;
            
            const PAGE_SIZE = 50;
            let currentPage = 1;
            let filteredPages = [...allManPagesData];
            let currentSection = 'all';
            let currentSort = 'name-asc';
            let searchQuery = '';
            let searchOptions = {
                exactMatch: false,
                nameOnly: false,
                highlightMatches: true
            };
            
            function renderManPages() {
                const manPagesContainer = document.getElementById('manPages');
                manPagesContainer.innerHTML = '';
                
                if (filteredPages.length === 0) {
                    manPagesContainer.innerHTML = '<div class="no-results">No matching manual pages found.</div>';
                    updatePagination();
                    document.getElementById('shownEntries').textContent = '0';
                    return;
                }
                
                const startIndex = (currentPage - 1) * PAGE_SIZE;
                const endIndex = Math.min(startIndex + PAGE_SIZE, filteredPages.length);
                const pageItems = filteredPages.slice(startIndex, endIndex);
                
                const fragment = document.createDocumentFragment();
                
                pageItems.forEach(page => {
                    const card = document.createElement('div');
                    card.className = 'man-card';
                    
                    let displayName = page.name;
                    let displayDesc = page.description;
                    
                    if (searchOptions.highlightMatches && searchQuery.trim() !== '') {
                        if (!searchOptions.exactMatch) {
                            const keywords = searchQuery.toLowerCase().split(/\s+/).filter(kw => kw.length > 0);
                            
                            keywords.forEach(keyword => {
                                if (!searchOptions.nameOnly) {
                                    const re = new RegExp(`(${keyword})`, 'gi');
                                    displayDesc = displayDesc.replace(re, '<span class="highlight">$1</span>');
                                }
                                
                                const nameRe = new RegExp(`(${keyword})`, 'gi');
                                displayName = displayName.replace(nameRe, '<span class="highlight">$1</span>');
                            });
                        } else if (searchOptions.exactMatch) {
                            const query = searchQuery.toLowerCase();
                            if (page.name.toLowerCase().includes(query)) {
                                const re = new RegExp(`(${query})`, 'gi');
                                displayName = displayName.replace(re, '<span class="highlight">$1</span>');
                            }
                        }
                    }
                    
                    card.innerHTML = `
                        <div class="man-card-header">
                            ${displayName}
                            <span class="section-badge">Section ${page.section}</span>
                        </div>
                        <div class="man-card-body">
                            <div class="description">${displayDesc}</div>
                            <a href="man/${page.name}.html" style="display:block; margin-top:1rem; color:var(--primary-color);">View Manual Page</a>
                        </div>
                    `;
                    
                    fragment.appendChild(card);
                });
                
                manPagesContainer.appendChild(fragment);
                updatePagination();
                document.getElementById('shownEntries').textContent = filteredPages.length;
            }
            
            function updatePagination() {
                const paginationContainer = document.getElementById('pagination');
                const totalPages = Math.ceil(filteredPages.length / PAGE_SIZE);
                
                if (totalPages <= 1) {
                    paginationContainer.innerHTML = '';
                    return;
                }
                
                let paginationHTML = '';
                
                paginationHTML += `<button class="page-button" id="prevPage" ${currentPage === 1 ? 'disabled' : ''}>Previous</button>`;
                
                const maxPageButtons = 5;
                let startPage = Math.max(1, currentPage - Math.floor(maxPageButtons / 2));
                let endPage = Math.min(totalPages, startPage + maxPageButtons - 1);
                
                if (endPage - startPage + 1 < maxPageButtons) {
                    startPage = Math.max(1, endPage - maxPageButtons + 1);
                }
                
                if (startPage > 1) {
                    paginationHTML += `<button class="page-button" data-page="1">1</button>`;
                    if (startPage > 2) {
                        paginationHTML += `<span class="page-info">...</span>`;
                    }
                }
                
                for (let i = startPage; i <= endPage; i++) {
                    paginationHTML += `<button class="page-button ${i === currentPage ? 'active' : ''}" data-page="${i}">${i}</button>`;
                }
                
                if (endPage < totalPages) {
                    if (endPage < totalPages - 1) {
                        paginationHTML += `<span class="page-info">...</span>`;
                    }
                    paginationHTML += `<button class="page-button" data-page="${totalPages}">${totalPages}</button>`;
                }
                
                paginationHTML += `<button class="page-button" id="nextPage" ${currentPage === totalPages ? 'disabled' : ''}>Next</button>`;
                
                paginationContainer.innerHTML = paginationHTML;
                
                document.getElementById('prevPage')?.addEventListener('click', () => {
                    if (currentPage > 1) {
                        currentPage--;
                        scrollTo(0, 0);
                        renderManPages();
                    }
                });
                
                document.getElementById('nextPage')?.addEventListener('click', () => {
                    if (currentPage < totalPages) {
                        currentPage++;
                        scrollTo(0, 0);
                        renderManPages();
                    }
                });
                
                document.querySelectorAll('.page-button[data-page]').forEach(button => {
                    button.addEventListener('click', () => {
                        currentPage = parseInt(button.dataset.page);
                        scrollTo(0, 0);
                        renderManPages();
                    });
                });
            }
            
            function filterPages() {
                searchQuery = document.getElementById('searchBox').value.trim();
                searchOptions.exactMatch = document.getElementById('exactMatch').checked;
                searchOptions.nameOnly = document.getElementById('nameOnly').checked;
                
                let query = searchQuery.toLowerCase();
                
                if (query.startsWith('@')) {
                    searchOptions.nameOnly = true;
                    query = query.substring(1);
                }
                
                if (query.startsWith('"') && query.endsWith('"')) {
                    searchOptions.exactMatch = true;
                    query = query.slice(1, -1);
                }
                
                filteredPages = allManPagesData.filter(page => {
                    if (currentSection !== 'all' && page.section !== currentSection) {
                        return false;
                    }
                    
                    if (query.trim() === '') {
                        return true;
                    }
                    
                    if (searchOptions.exactMatch) {
                        if (searchOptions.nameOnly) {
                            return page.name.toLowerCase() === query;
                        } else {
                            return page.name.toLowerCase() === query || 
                                   page.description.toLowerCase().includes(query);
                        }
                    } else {
                        const keywords = query.split(/\s+/).filter(kw => kw.length > 0);
                        
                        if (searchOptions.nameOnly) {
                            return keywords.every(keyword => 
                                page.name.toLowerCase().includes(keyword)
                            );
                        } else {
                            return keywords.every(keyword => 
                                page.name.toLowerCase().includes(keyword) || 
                                page.description.toLowerCase().includes(keyword)
                            );
                        }
                    }
                });
                
                sortPages();
                currentPage = 1;
                renderManPages();
            }
            
            function sortPages() {
                const [field, direction] = currentSort.split('-');
                
                filteredPages.sort((a, b) => {
                    let comparison = 0;
                    
                    if (field === 'name') {
                        comparison = a.name.localeCompare(b.name);
                    } else if (field === 'section') {
                        comparison = a.section.localeCompare(b.section, undefined, { numeric: true });
                    }
                    
                    return direction === 'asc' ? comparison : -comparison;
                });
            }
            
            function initSearch() {
                const searchBox = document.getElementById('searchBox');
                let debounceTimeout;
                
                searchBox.addEventListener('input', () => {
                    clearTimeout(debounceTimeout);
                    debounceTimeout = setTimeout(filterPages, 300);
                });
                
                document.querySelectorAll('.filter-button').forEach(button => {
                    button.addEventListener('click', () => {
                        document.querySelectorAll('.filter-button').forEach(btn => {
                            btn.classList.remove('active');
                        });
                        button.classList.add('active');
                        
                        currentSection = button.dataset.section;
                        filterPages();
                    });
                });
                
                document.getElementById('exactMatch').addEventListener('change', filterPages);
                document.getElementById('nameOnly').addEventListener('change', filterPages);
                document.getElementById('highlightMatches').addEventListener('change', () => {
                    searchOptions.highlightMatches = document.getElementById('highlightMatches').checked;
                    renderManPages();
                });
                
                document.getElementById('sortSelect').addEventListener('change', () => {
                    currentSort = document.getElementById('sortSelect').value;
                    sortPages();
                    renderManPages();
                });
                
                searchBox.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        filterPages();
                    }
                });
            }
            
            function init() {
                document.getElementById('genDate').textContent = new Date().toLocaleDateString();
                document.getElementById('totalEntries').textContent = allManPagesData.length;
                document.getElementById('shownEntries').textContent = allManPagesData.length;
                
                sortPages();
                initSearch();
                
                setTimeout(() => {
                    renderManPages();
                }, 100);
            }
            
            document.addEventListener('DOMContentLoaded', init);
        </script>
    </body>
    </html>
    """
    
    html = html.replace('DATA_PLACEHOLDER', json.dumps(man_pages))
    
    index_path = os.path.join(output_dir, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    output_dir = 'c_man_pages'
    man_dir = os.path.join(output_dir, 'man')
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(man_dir, exist_ok=True)
    
    print("Finding C-related man pages...")
    c_pages = get_c_man_pages()
    print(f"Found {len(c_pages)} C-related man pages")
    
    print("Converting man pages to HTML...")
    successful_conversions = []
    total_pages = len(c_pages)
    
    for i, page in enumerate(c_pages):
        print(f"Processing {i+1}/{total_pages}: {page['name']}({page['section']})...")
        if convert_man_to_html(page, man_dir):
            successful_conversions.append(page)
        
        if (i + 1) % 100 == 0 or i + 1 == total_pages:
            print(f"Progress: {i+1}/{total_pages} ({(i+1)*100/total_pages:.1f}%)")
    
    print(f"Successfully converted {len(successful_conversions)} man pages")
    
    print("Creating index page...")
    create_index_page(successful_conversions, output_dir)
    
    print(f"Done! Open {os.path.join(output_dir, 'index.html')} to view the man pages.")

if __name__ == "__main__":
    main()
