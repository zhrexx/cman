#!/usr/bin/env python3
import os
import re
import subprocess
import shutil
from bs4 import BeautifulSoup
import json

def get_c_man_pages():
    """Gets all man pages related to C programming"""
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
    """Converts a man page to HTML"""
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
    """Creates an index page with search functionality and performance optimizations"""
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
                <div class="filter-options">
                    <button class="filter-button active" data-section="all">All Sections</button>
                    <button class="filter-button" data-section="2">Section 2</button>
                    <button class="filter-button" data-section="3">Section 3</button>
                </div>
            </div>
            
            <div class="man-pages" id="manPages">
                <!-- Man pages will be dynamically inserted here -->
                <div class="loading-indicator">
                    <div class="spinner"></div>
                    <p>Loading manual pages...</p>
                </div>
            </div>
            
            <div class="pagination" id="pagination">
                <!-- Pagination controls will be inserted here -->
            </div>
        </div>
        
        <footer>
            <div class="container">
                <p>Generated on <span id="genDate"></span></p>
                <p>Total entries: <span id="totalEntries"></span></p>
            </div>
        </footer>
        
        <script>
            // Store man pages data
            const allManPagesData = DATA_PLACEHOLDER;
            
            // Pagination settings
            const PAGE_SIZE = 50;
            let currentPage = 1;
            let filteredPages = [...allManPagesData];
            let currentSection = 'all';
            
            // Function to render a batch of man pages
            function renderManPages() {
                const manPagesContainer = document.getElementById('manPages');
                manPagesContainer.innerHTML = '';
                
                if (filteredPages.length === 0) {
                    manPagesContainer.innerHTML = '<div class="no-results">No matching manual pages found.</div>';
                    updatePagination();
                    return;
                }
                
                // Calculate start and end indices for the current page
                const startIndex = (currentPage - 1) * PAGE_SIZE;
                const endIndex = Math.min(startIndex + PAGE_SIZE, filteredPages.length);
                const pageItems = filteredPages.slice(startIndex, endIndex);
                
                // Create a document fragment for better performance
                const fragment = document.createDocumentFragment();
                
                pageItems.forEach(page => {
                    const card = document.createElement('div');
                    card.className = 'man-card';
                    
                    card.innerHTML = `
                        <div class="man-card-header">
                            ${page.name}
                            <span class="section-badge">Section ${page.section}</span>
                        </div>
                        <div class="man-card-body">
                            <div class="description">${page.description}</div>
                            <a href="man/${page.name}.html" style="display:block; margin-top:1rem; color:var(--primary-color);">View Manual Page</a>
                        </div>
                    `;
                    
                    fragment.appendChild(card);
                });
                
                manPagesContainer.appendChild(fragment);
                updatePagination();
            }
            
            // Function to update pagination controls
            function updatePagination() {
                const paginationContainer = document.getElementById('pagination');
                const totalPages = Math.ceil(filteredPages.length / PAGE_SIZE);
                
                if (totalPages <= 1) {
                    paginationContainer.innerHTML = '';
                    return;
                }
                
                let paginationHTML = '';
                
                // Previous button
                paginationHTML += `<button class="page-button" id="prevPage" ${currentPage === 1 ? 'disabled' : ''}>Previous</button>`;
                
                // Page info
                paginationHTML += `<div class="page-info">Page ${currentPage} of ${totalPages}</div>`;
                
                // Next button
                paginationHTML += `<button class="page-button" id="nextPage" ${currentPage === totalPages ? 'disabled' : ''}>Next</button>`;
                
                paginationContainer.innerHTML = paginationHTML;
                
                // Add event listeners
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
            }
            
            // Function to filter pages based on search and section
            function filterPages() {
                const query = document.getElementById('searchBox').value.toLowerCase();
                
                filteredPages = allManPagesData.filter(page => {
                    // Section filter
                    if (currentSection !== 'all' && page.section !== currentSection) {
                        return false;
                    }
                    
                    // Search filter
                    if (query.trim() !== '') {
                        return (
                            page.name.toLowerCase().includes(query) ||
                            page.description.toLowerCase().includes(query)
                        );
                    }
                    
                    return true;
                });
                
                // Reset to first page when filter changes
                currentPage = 1;
                renderManPages();
            }
            
            // Initialize search functionality with debounce
            function initSearch() {
                const searchBox = document.getElementById('searchBox');
                let debounceTimeout;
                
                searchBox.addEventListener('input', () => {
                    clearTimeout(debounceTimeout);
                    debounceTimeout = setTimeout(filterPages, 300);
                });
                
                // Set up section filter buttons
                document.querySelectorAll('.filter-button').forEach(button => {
                    button.addEventListener('click', () => {
                        // Update active state
                        document.querySelectorAll('.filter-button').forEach(btn => {
                            btn.classList.remove('active');
                        });
                        button.classList.add('active');
                        
                        // Update filter and re-render
                        currentSection = button.dataset.section;
                        filterPages();
                    });
                });
            }
            
            // Initialize the page
            function init() {
                // Set generated date
                document.getElementById('genDate').textContent = new Date().toLocaleDateString();
                document.getElementById('totalEntries').textContent = allManPagesData.length;
                
                // Initialize search and filters
                initSearch();
                
                // Initial render (with a small delay to let the DOM settle)
                setTimeout(() => {
                    renderManPages();
                }, 100);
            }
            
            // Start initialization when DOM is ready
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
